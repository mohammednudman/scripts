import re
import json


def parse_request(request_str):
    order_events = []
    matches = re.findall(r'order_event_uuid.*?(?=order_event_uuid|$)', request_str, re.DOTALL)

    for match in matches:
        order_event = {
            "CheckContext": {
                "Checks": []
            },
            "CheckOverrides": []
        }
        order_event_type = None
        attr_vals = {}

        # Extract key-value pairs
        pairs = re.findall(r'(\w+):\s*"([^"]+)"', match)
        for key, value in pairs:
            if key == "order_event_type":
                order_event_type = value.strip()
                order_event[order_event_type] = {}
            elif key == "RISKPARAMS":
                order_event["CheckContext"]["Checks"] = [val for val in value.split('|') if val]
            elif key == "risk_check_override":
                overrides = re.findall(r'{PARAM:\s*(\d+),\s*justification:\s*\'([^\']+)\'}', match)
                for param, justification in overrides:
                    order_event["CheckOverrides"].append({
                        "PARAM": param,
                        "justification": justification
                    })
            elif key == "order_event_attr_vals":
                # Extract attr_vals content correctly
                attr_vals_str = match[
                                match.index("order_event_attr_vals: {") + len("order_event_attr_vals: {"):match.index(
                                    "}", match.index("order_event_attr_vals: {"))]
                attr_vals_pairs = re.findall(r'(\w+):\s*([^,}]+)', attr_vals_str)
                for attr_key, attr_value in attr_vals_pairs:
                    attr_vals[attr_key.strip()] = attr_value.strip()
                if order_event_type:
                    order_event[order_event_type].update(attr_vals)
            else:
                if order_event_type:
                    order_event[order_event_type][key] = value

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

    return json.dumps(request, indent=2)


file_path = "input.txt"
check_requests = parse_file(file_path)

for request_json in check_requests:
    print(request_json)
