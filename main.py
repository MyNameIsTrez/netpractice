import json

import more_itertools


def main():
    with open("levels/level8.json") as f:
        level = json.load(f)
    mark_known(level)
    convert_to_trits(level)

    solve(level)
    # level["interfaces"]["C1"]["ip"] = [1] * 31
    # level["interfaces"]["C1"]["ip"].append(0)

    print_solution(level)


def mark_known(level):
    for interface in level["interfaces"].values():
        interface["ip_unknown"] = interface["ip"] is None
        interface["mask_unknown"] = interface["mask"] is None

        for route in interface["routing_table"]:
            route["destination_unknown"] = route["destination"] is None
            route["cidr_unknown"] = route["cidr"] is None
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
            interface["mask"] = get_trits(interface["mask"])
        else:
            interface["mask"] = get_empty_trits()

        for route in interface["routing_table"]:
            if route["destination"]:
                route["destination"] = get_trits(route["destination"])
            else:
                route["destination"] = get_empty_trits()

            if route["cidr"]:
                route["cidr"] = get_trits(route["cidr"])
            else:
                route["cidr"] = get_empty_trits()

            if route["next_hop"]:
                route["next_hop"] = get_trits(route["next_hop"])
            else:
                route["next_hop"] = get_empty_trits()


def get_trits(bit_string):
    return [
        int(bit) for byte in bit_string.split(".") for bit in format(int(byte), "08b")
    ]


def get_empty_trits():
    return [None for _ in range(32)]


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

    closest_other_router_interfaces = level["closest_other_router_interfaces"]

    for interface_name, interface in interfaces.items():
        # interface["ip"]

        # Try to copy a mask from another interface in the network.
        for neighbor_name in level["interface_network_neighbors"][interface_name]:
            neighbor_mask = interfaces[neighbor_name]["mask"]
            fill_unknown_trits(interface["mask"], neighbor_mask)

        for route in interface["routing_table"]:
            pass

            # route["destination"]

            # route["cidr"]

            # Finds the closest interface that's on another router,
            # and use its IP as this route's next_hop.
            closest_other = closest_other_router_interfaces[interface_name]
            fill_unknown_trits(route["next_hop"], interfaces[closest_other]["ip"])


def fill_unknown_trits(a_trits, b_trits):
    for trit_index, b_trit in enumerate(b_trits):
        if a_trits[trit_index] is None:
            a_trits[trit_index] = b_trit


def print_solution(level):
    print_interfaces(level["interfaces"])


def print_interfaces(interfaces):
    print("interfaces:")
    for interface_name, interface in interfaces.items():
        interface_string = ""

        if interface["ip_unknown"]:
            interface_string += f", ip: {get_bit_string(interface['ip'])}"
        if interface["mask_unknown"]:
            interface_string += f", mask: {get_bit_string(interface['mask'])}"

        routes_string = ""

        for route in interface["routing_table"]:
            route_string = ""

            if route["destination_unknown"]:
                route_string += f"destination: {get_bit_string(route['destination'])}, "
            if route["cidr_unknown"]:
                route_string += f"cidr: {get_bit_string(route['cidr'])}, "
            if route["next_hop_unknown"]:
                route_string += f"next_hop: {get_bit_string(route['next_hop'])}, "

            if route_string:
                routes_string += f"{{ {route_string}}},"

        if routes_string:
            interface_string += f", routing_table: [ {routes_string} ]"

        if interface_string:
            print(f"{interface_name}" + interface_string)


def get_bit_string(trits):
    if None in trits:
        # TODO: Raise this error instead:
        # raise ValueError("Encountered None trit.")
        return None

    bytes = []

    # 8 is the number of bits in a byte.
    for byte_bit_list in more_itertools.chunked(trits, 8):
        byte = 0
        for bit in byte_bit_list:
            byte = (byte << 1) | bit

        bytes.append(str(byte))

    return ".".join(bytes)


if __name__ == "__main__":
    main()
