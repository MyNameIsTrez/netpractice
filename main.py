import json

import more_itertools

# CONFIGURABLE
LEVEL_NUMBER = 8


BITS_PER_BYTE = 8
BITS_PER_ADDRESS = 4 * BITS_PER_BYTE


def main():
    with open(f"levels/level{LEVEL_NUMBER}.json") as f:
        level = json.load(f)

    setup(level)
    solve(level)
    # TODO: Add this back in!
    # if not is_solved(level["interfaces"]):
    #     raise ValueError("There was an unsolved value! Report this to sbos.")
    print_interface_solutions(level["interfaces"])


def setup(level):
    mark_known(level)
    convert_to_trits(level)

    assign_default_destinations(level)

    floodfill_masks(level)
    assign_default_masks(level)

    if LEVEL_NUMBER == 8:
        use_level_8_internet_destination(level)
        use_level_8_next_hop(level)
    # assign_ips_using_next_hops(level) # TODO:
    # assign_default_ips(level) # TODO:
    floodfill_network_addresses(level)

    point_next_hops_to_closest_router(level)


def mark_known(level):
    for interface in level["interfaces"].values():
        interface["ip_unknown"] = interface["ip"] is None
        interface["mask_unknown"] = interface["mask"] is None

        for route in interface["routing_table"]:
            route["destination_unknown"] = route["destination"] is None
            route["next_hop_unknown"] = route["next_hop"] is None


def convert_to_trits(level):
    """Trit standing for trinary digit,
    since the values are either None, 0, or 1.
    """
    for interface in level["interfaces"].values():
        if interface["ip"]:
            interface["ip"] = get_trits(interface["ip"])
        else:
            interface["ip"] = get_empty_trits()

        if interface["mask"]:
            interface["mask"] = interface["mask"]

        for route in interface["routing_table"]:
            if route["destination"]:
                route["destination"] = get_trits(route["destination"])
            else:
                route["destination"] = get_empty_trits()

            if route["cidr"]:
                route["cidr"] = route["cidr"]

            if route["next_hop"]:
                route["next_hop"] = get_trits(route["next_hop"])
            else:
                route["next_hop"] = get_empty_trits()


def get_trits(bit_string):
    return [
        int(bit)
        for byte in bit_string.split(".")
        for bit in format(int(byte), f"0{BITS_PER_BYTE}b")
    ]


def get_empty_trits():
    return [None for _ in range(BITS_PER_ADDRESS)]


def assign_default_destinations(level):
    """Assign all unknown route destinations to "0.0.0.1" and a CIDR of 0.

    The reason "0.0.0.0" or "default" isn't used instead, is because those
    throw "invalid default route on internet I" in the logs
    when used as the internet's destination.
    And so it's easiest to just use "0.0.0.1" for all other clients and router
    interfaces as well.
    """
    for interface in level["interfaces"].values():
        for route in interface["routing_table"]:
            if None in route["destination"]:
                route["destination"] = [0] * 31 + [1]
                route["cidr"] = 0


def floodfill_masks(level):
    """Tries to copy a mask from another interface in the network."""
    interfaces = level["interfaces"]

    for interface_name, interface in interfaces.items():
        if interface["mask"] is None:
            for neighbor_name in level["network_neighbors_of_interfaces"][
                interface_name
            ]:
                interface["mask"] = interfaces[neighbor_name]["mask"]


def assign_default_masks(level):
    """Assign mask 29 to networks without a mask.

    Networks without a switch in them can always get away with mask 30,
    but it's easier to not have to check whether there is a switch by
    always assigning mask 29.
    """
    interfaces = level["interfaces"]

    for interface_name in interfaces:
        if interfaces[interface_name]["mask"] is None:
            interfaces[interface_name]["mask"] = 29


def use_level_8_internet_destination(level):
    interfaces = level["interfaces"]
    internet_route = interfaces["I1"]["routing_table"][0]
    destination = internet_route["destination"]

    for i in range(internet_route["cidr"]):
        interfaces["C1"]["ip"][i] = destination[i]
        interfaces["D1"]["ip"][i] = destination[i]


def use_level_8_next_hop(level):
    interfaces = level["interfaces"]

    for i in range(BITS_PER_ADDRESS):
        interfaces["R13"]["ip"][i] = interfaces["R21"]["routing_table"][0]["next_hop"][
            i
        ]


def assign_ips_using_next_hops(level):
    pass


def assign_default_ips(level):
    """1.1.1.1, 1.1.1.2 -> 2.2.2.1, 2.2.2.2, etc."""
    pass


def floodfill_network_addresses(level):
    interfaces = level["interfaces"]

    for interface_name, neighbors in level["network_neighbors_of_interfaces"].items():
        interface = interfaces[interface_name]

        for i in range(interface["mask"]):
            for neighbor_name in neighbors:
                ip = interface["ip"]
                neighbor_ip = interfaces[neighbor_name]["ip"]
                if ip[i] is None:
                    ip[i] = neighbor_ip[i]


def point_next_hops_to_closest_router(level):
    """Looks up the name of the closest interface that's on another router,
    and lets this route's next_hop point to that other router's IP.
    """

    closest_other_router_interfaces = level["closest_other_router_interfaces"]
    interfaces = level["interfaces"]

    for interface_name, interface in interfaces.items():
        closest_other = closest_other_router_interfaces[interface_name]

        for route in interface["routing_table"]:
            if None in route["next_hop"]:
                route["next_hop"] = interfaces[closest_other]["ip"]


def solve(level):
    """Replaces None values in level with solved values.

    It relies on these observations:
    1. Switches can be entirely ignored.
    Just create a web of connections between interfaces.
    2. Routers can be entirely ignored.
    Just assign the router's routing table to all its interfaces.
    3. Every interface has a (possibly empty) routing table.
    4. If an interface can't pass its packet on to an interface
    it is connected to, the interface iterates over its routing table.
    5. In level 6 with seed "sbos", the internet has its own interface.
    Most of the time it won't have one though, in which case its interface
    IP and mask are always set to its neighboring interface's settings, with
    the last byte set to 1.
    6. Always set empty client routing table destinations to "default" (or 0.0.0.1/0 sometimes for the internet?).
    7. Routers can't be abstracted away, because interfaces aren't capable
    of asserting whether other interfaces should be part of the same network.
    Routers assert where networks end.
    8. Packets can not immediately travel back to the place they just came from.
    9. 127.x.x.x throws the error "loopback address detected", and
    anything above 223.255.255.255 throws the error "invalid IP".

    The setup phase of the program:
    1. Set every unknown client destination to "default",
    unless it is the internet, in which case TODO: ?

    The program executes these steps in a loop until the puzzle is solved:
    1. Iterate over all interface masks. If a network's mask is known,
    floodfill it to all other interfaces on the network. If the floodfill
    encounters either an interface with a non-NULL mask,
    then stop floodfilling in that direction.

    ?. Use known destinations of routes
    to set client (and maybe also router) interface IPs?
    ?. If a route doesn't have a next hop set, recursively try to set it
    for every neighboring router with a known IP?
    ?. Use that /32 always being the same as /0,
    both as interface masks and routing masks?
    """
    interfaces = level["interfaces"]

    for interface_name, interface in interfaces.items():
        # interface["ip"]

        for route in interface["routing_table"]:
            pass

            # route["destination"]

            # route["cidr"]


def is_solved(interfaces):
    """Checks that all unknown values have been found."""
    for interface in interfaces.values():
        if None in interface["ip"] or interface["mask"] is None:
            return False

        for route in interface["routing_table"]:
            if (
                None in route["destination"]
                or route["cidr"] is None
                or None in route["next_hop"]
            ):
                return False

    return True


def print_interface_solutions(interfaces):
    print("interfaces:")
    for interface_name, interface in interfaces.items():
        interface_strings = []

        if interface["ip_unknown"]:
            interface_strings.append(f"ip: {get_bit_string(interface['ip'])}")
        if interface["mask_unknown"]:
            interface_strings.append(f"mask: {interface['mask']}")

        routes_strings = []

        for route in interface["routing_table"]:
            route_strings = []

            if route["destination_unknown"]:
                route_strings.append(
                    f"destination: {get_bit_string(route['destination'])}/{route['cidr']}"
                )

            if route["next_hop_unknown"]:
                route_strings.append(f"next_hop: {get_bit_string(route['next_hop'])}")

            if route_strings:
                routes_strings.append("{" + ", ".join(route_strings) + "}")

        if routes_strings:
            interface_strings.append(f"routing_table: [ {', '.join(routes_strings)} ]")

        if interface_strings:
            interface_strings.insert(0, interface_name)
            print(", ".join(interface_strings))


def get_bit_string(trits):
    # TODO: Get rid of this, since is_solved() handles this!
    if None in trits:
        return None

    bytes = []

    for byte_bit_list in more_itertools.chunked(trits, BITS_PER_BYTE):
        byte = 0
        for bit in byte_bit_list:
            byte = (byte << 1) | bit

        bytes.append(str(byte))

    return ".".join(bytes)


if __name__ == "__main__":
    main()
