import json
# from pprint import pprint


def main():
	with open("levels/level8.json") as f:
		level = json.load(f)
	mark_known(level)
	convert_to_trits(level)
	# solve(level)
	# print_level(level)


def mark_known(level):
	for interface in level["interfaces"].values():
		interface["ip_known"] = interface["ip"] is not None
		interface["mask_known"] = interface["mask"] is not None

		for route in interface["routing_table"]:
			route["destination_known"] = route["destination"] is not None
			route["cidr_known"] = route["cidr"] is not None
			route["next_hop_known"] = route["next_hop"] is not None


def convert_to_trits(level):
	"""Trit standing for trinary digit,
	since the values are either None, 0, or 1.
	"""
	for interface in level["interfaces"].values():
		if interface["ip"]:
			interface["ip"] = convert_bit_string_to_trit_field(interface["ip"])
		else:
			interface["ip"] = get_empty_trit_field()

		if interface["mask"]:
			interface["mask"] = convert_bit_string_to_trit_field(interface["mask"])
		else:
			interface["mask"] = get_empty_trit_field()

		for route in interface["routing_table"]:
			if route["destination"]:
				route["destination"] = convert_bit_string_to_trit_field(route["destination"])
			else:
				route["destination"] = get_empty_trit_field()

			if route["cidr"]:
				route["cidr"] = convert_bit_string_to_trit_field(route["cidr"])
			else:
				route["cidr"] = get_empty_trit_field()

			if route["next_hop"]:
				route["next_hop"] = convert_bit_string_to_trit_field(route["next_hop"])
			else:
				route["next_hop"] = get_empty_trit_field()


def convert_bit_string_to_trit_field(bit_string):
	# [2:] is to chop off the "0b" part
	return [bit for byte in bit_string.split(".") for bit in bin(int(byte))[2:]]


def get_empty_trit_field():
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
	for goal in level["goals"]:
		# print(goal)
		pass


def print_level(level):
	print_interfaces(level["interfaces"])


def print_interfaces(interfaces):
	print("interfaces:")
	for interface_name, interface in interfaces.items():
		interface_string = ""

		if not interface["ip_known"]:
			interface_string += f", ip: {interface['ip']}"
		if not interface["mask_known"]:
			interface_string += f", mask: {interface['mask']}"

		routes_string = ""

		for route in interface["routing_table"]:
			route_string = ""

			if not route["destination_known"]:
				route_string += f"destination: {route['destination']}, "
			if not route["cidr_known"]:
				route_string += f"cidr: {route['cidr']}, "
			if not route["next_hop_known"]:
				route_string += f"next_hop: {route['next_hop']}, "

			if route_string:
				routes_string += f"{{ {route_string}}},"

		if routes_string:
			interface_string += f", routing_table: [ {routes_string} ]"

		if interface_string:
			print(f"{interface_name}" + interface_string)


if __name__ == "__main__":
	main()
