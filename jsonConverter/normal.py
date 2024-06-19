import json
import re


def parse_request(request_str):
    order_events = []
    matches = re.findall(r'{order_event_uuid.*?},\s*]', request_str, re.DOTALL)

    for match in matches:
        order_event = {
            "CheckContext": {
                "Checks": []
            },
            "CheckOverrides": []
        }
        order_event_type = None
        attr_vals = {}

        pairs = re.findall(r'(\w+):\s*("[^"]+"|\d+|\[[^]]*\]|\w+)', match)
        for key, value in pairs:
            if key == "order_event_type":
                order_event_type = value.strip('"')
                order_event[order_event_type] = {}
            elif key == "RISKPARAMS":
                order_event["CheckContext"]["Checks"] = [val for val in value.split('|') if val != '"']
            elif key == "order_event_attr_vals":
                attr_vals_str = match[
                                match.index("order_event_attr_vals: {") + len("order_event_attr_vals: {"):match.index(
                                    "}", match.index("order_event_attr_vals: {"))
                                ]
                attr_vals_pairs = re.findall(r'(\w+):\s*("[^"]+"|\d+)', attr_vals_str)
                for attr_key, attr_value in attr_vals_pairs:
                    attr_vals[attr_key.strip()] = attr_value.strip('"')
                if order_event_type:
                    order_event[order_event_type].update(attr_vals)
            elif key == "risk_check_overrides":
                override_matches = re.findall(r'\{(.*?)\}', value)
                for override_match in override_matches:
                    override_pairs = re.findall(r'(\w+):\s*("[^"]*"|\S+)', override_match)
                    override_obj = {}
                    for o_key, o_value in override_pairs:
                        o_value = o_value.strip('"')
                        if o_key == "justification":
                            o_key = "overrideJustification"
                        elif o_key == "PARAM":
                            o_key = "Check"
                        elif o_key == "overrider_sid":
                            o_key = "overriderSID"
                        override_obj[o_key.strip()] = o_value
                    order_event["CheckOverrides"].append(override_obj)
            else:
                if order_event_type:
                    order_event[order_event_type][key] = value.strip('"')

        if order_event_type:
            order_events.append(order_event)

    return order_events


def parse_file(file_path):
    check_requests = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                order_events = parse_request(line.strip())
                check_requests.append(create_request(order_events))

    return check_requests


def create_request(order_events):
    request = {
        "CheckRequest": {
            "OrderEventInfos": order_events
        }
    }

    return request


file_path = "input.txt"
check_requests = parse_file(file_path)

output_file_path = "output.json"
with open(output_file_path, 'w') as output_file:
    json.dump(check_requests, output_file, indent=2)

print(f"Output has been written to {output_file_path}")
