from pprint import pprint
import json


def main():
	with open("levels/level8.json") as f:
		level = json.load(f)
	mark_known_interfaces(level)
	mark_known_routing_tables(level)
	solve(level)
	# print_level(level)


def mark_known_interfaces(level):
	for interface in level["interfaces"].values():
		interface["ip_known"] = interface["ip"] is not None
		interface["mask_known"] = interface["mask"] is not None


def mark_known_routing_tables(level):
	for routing_table in level["routing_tables"].values():
		for route in routing_table:
			route["destination_known"] = route["destination"] is not None
			route["cidr_known"] = route["cidr"] is not None
			route["next_hop_known"] = route["next_hop"] is not None


def solve(level):
	for goal in level["goals"]:
		print(goal)


def print_level(level):
	print_interfaces(level["interfaces"])
	print()
	print_routing_tables(level["routing_tables"])


def print_interfaces(interfaces):
	print("interfaces:")
	for interface_name, interface in interfaces.items():
		ip_known = interface["ip_known"]
		mask_known = interface["mask_known"]
		if not ip_known or not mask_known:
			string = f"{interface_name}:"
			if not ip_known:
				string += f" ip: {interface['ip']}"
			if not mask_known:
				string += f" mask: {interface['mask']}"
			print(string)


def print_routing_tables(routing_tables):
	print("routing tables:")
	for routing_table_name, routing_table in routing_tables.items():
		for route in routing_table:
			destination_known = route["destination_known"]
			cidr_known = route["cidr_known"]
			next_hop_known = route["next_hop_known"]
			if not destination_known or not cidr_known or not next_hop_known:
				string = f"{routing_table_name}:"
				if not destination_known:
					string += f" destination: {route['destination']}"
				if not cidr_known:
					string += f" cidr: {route['cidr']}"
				if not next_hop_known:
					string += f" next_hop: {route['next_hop']}"
				print(string)


if __name__ == "__main__":
	main()
