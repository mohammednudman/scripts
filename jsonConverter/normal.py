import json
import re

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

        pairs = re.findall(r'(\w+):\s*"([^"]+)"', match)
        for key, value in pairs:
            if key == "order_event_type":
                order_event_type = value.strip()
                order_event[order_event_type] = {}
            elif key == "RISKPARAMS":
                order_event["CheckContext"]["Checks"] = [val for val in value.split('|') if val]
            elif key == "order_event_attr_vals":
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

        risk_check_override_matches = re.findall(r'risk_check_override:\s*\[({.*?})\]', match, re.DOTALL)
        if risk_check_override_matches:
            for override_str in risk_check_override_matches:
                override_pairs = re.findall(r"(\w+):\s*'([^']+)'", override_str)
                override_obj = {}
                for key, value in override_pairs:
                    override_obj[key.strip()] = value.strip()
                order_event["CheckOverrides"].append(override_obj)

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

# Open output file in write mode
with open("output.txt", "w") as output_file:
    for request_json in check_requests:
        # Convert request_json to JSON string
        json_str = json.dumps(request_json, indent=2)
        # Write JSON string to output file
        output_file.write(json_str)
        output_file.write("\n")  # Add a newline after each JSON object
