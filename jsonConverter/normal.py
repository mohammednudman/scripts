import re
import json

default_values = {
    "RootOrderID": "",
    "ClOrdID": "",
    "OrigClOrdID": "",
    "Instance": "LCETEST01",
    "SourceSysCode": "",
    "TraderID": "",
    "Region": "",
    "TradeDate": "",
    "Trader_Location": "",
    "Booking_ID": "",
    "DeskID": "",
    "BookingLegalEntityID": "",
    "OrderQty": 0,
    "Instrument": "",
    "Price": 0.0,
    "Side": "",
    "Instrument_Type": "",
    "Product": "",
    "OrdType": "",
    "Capacity": "",
    "TimeInForce": "",
    "FlowType": "",
    "Country": "",
    "Currency": "",
    "RLChecks": "",
    "DOUPDATE": "",
    "IS_CBFM": 0,
    "Order_Action": ""
}


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
        pairs = re.findall(r'(\w+):\s*"([^"]+)"', match)
        order_event_type = None

        for key, value in pairs:
            if key == "order_event_type":
                order_event_type = value.strip()
                order_event[order_event_type] = default_values.copy()
            elif order_event_type and key in default_values:
                order_event[order_event_type][key.strip()] = value.strip()
            elif key == "RISKPARAMS":
                order_event["CheckContext"]["Checks"] = [val for val in value.split('|') if val]
            elif key == "risk_check_override":
                order_event["CheckOverrides"].append(json.loads(value))

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
