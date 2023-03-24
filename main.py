from pprint import pprint


levels = {
	"level8": {
		"clients": [ "R12", "C1", "D1" ],
		"goals": [
			{ "C1": "D1" }, { "D1": "C1" },
			{ "C1": "R12" }, { "R12": "C1" },
			{ "D1": "R12" }, { "R12": "D1" },
		],
		"interface_connections": {
			"R13": "R21", "R21": "R13",
			"R22": "C1", "C1": "R22",
			"R23": "D1", "D1": "R23",
		},
		"interfaces": {
			"R12": { "ip": "163.115.250.12", "mask": "255.255.255.240" },
			"R13": { "ip": None, "mask": None },
			"R21": { "ip": None, "mask": None },
			"R22": { "ip": None, "mask": None },
			"R23": { "ip": None, "mask": None },
			"C1": { "ip": None, "mask": None },
			"D1": { "ip": None, "mask": "255.255.255.240" },
		},
		"routing_tables": {
			"I": [ { "destination": "133.245.16.0", "cidr": 26, "next_hop": None } ],
			"R1": [ { "destination": None, "cidr": None, "next_hop": None }, { "destination": "0.0.0.0", "cidr": 0, "next_hop": "163.115.250.1" } ],
			"R2": [ { "destination": None, "cidr": None, "next_hop": "133.245.16.62" } ],
			"C": [ { "destination": None, "cidr": None, "next_hop": None } ],
			"D": [ { "destination": None, "cidr": None, "next_hop": None } ],
		},
	}
}


def main():
	level = levels["level8"]
	mark_known_interfaces(level)
	mark_known_routing_tables(level)
	print_level(level)


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
