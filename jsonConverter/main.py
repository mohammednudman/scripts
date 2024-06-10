import json
import re

def parse_order_event(event):
    attrs_pattern = re.compile(
        r'(?P<key>\w+):\s*"(?P<value>.*?)"'
        r'|(?P<key2>\w+):\s*(?P<value2>\d+\.\d+|\d+)'
        r'|(?P<key3>\w+):\s*null'
    )

    attributes = {}
    for match in attrs_pattern.finditer(event):
        if match.group("key"):
            attributes[match.group("key")] = match.group("value")
        elif match.group("key2"):
            attributes[match.group("key2")] = float(match.group("value2")) if '.' in match.group("value2") else int(match.group("value2"))
        elif match.group("key3"):
            attributes[match.group("key3")] = None

    return {
        "CheckRequest": {
            "OrderEventInfos": [
                {
                    "NewOrder": {
                        "RootOrderID": attributes.get("RootOrderID", ""),
                        "ClordID": attributes.get("ClordID", ""),
                        "OrigClordID": attributes.get("OrigClordID", ""),
                        "Instance": "LCETEST01",
                        "SourceSysCode": attributes.get("SourceSysCode", ""),
                        "TraderID": attributes.get("TraderID", ""),
                        "Region": attributes.get("Region", ""),
                        "TradeDate": attributes.get("TradeDate", ""),
                        "Trader_Location": attributes.get("Trader_Location", ""),
                        "Booking_ID": attributes.get("Booking_ID", ""),
                        "DeskID": attributes.get("DeskID", ""),
                        "BookingLegalEntityID": attributes.get("BookingLegalEntityID", ""),
                        "OrderQty": attributes.get("OrderQty", 0),
                        "Instrument": attributes.get("Instrument", ""),
                        "Price": attributes.get("Price", 0.0),
                        "Side": attributes.get("Side", ""),
                        "Instrument_Type": attributes.get("Instrument_Type", ""),
                        "Product": attributes.get("Product", ""),
                        "OrdType": attributes.get("OrdType", ""),
                        "Capacity": attributes.get("Capacity", ""),
                        "TimeInForce": attributes.get("TimeInForce", ""),
                        "FlowType": attributes.get("FlowType", ""),
                        "Country": attributes.get("Country", ""),
                        "Currency": attributes.get("Currency", ""),
                        "RLChecks": attributes.get("RLChecks", ""),
                        "DOUPDATE": attributes.get("DOUPDATE", ""),
                        "IS_CBFM": 0 if attributes.get("Is_CBFM") is None else attributes.get("Is_CBFM"),
                        "Order_Action": attributes.get("Order_Action", ""),
                        "CheckContext": {
                            "Checks": []
                        },
                        "CheckOverrides": []
                    }
                }
            ]
        }
    }

def parse_log_line(line):
    pattern = re.compile(
        r'order_requests: \[(.*)\]',
        re.DOTALL
    )

    match = pattern.search(line)
    if not match:
        return None

    order_events = match.group(1).split('}, {')
    order_event_infos = []
    for event in order_events:
        event = event.strip('{').strip('}')
        parsed_event = parse_order_event(event)
        if parsed_event:
            order_event_infos.append(parsed_event)

    return order_event_infos

with open('input.txt', 'r') as file:
    log_lines = file.readlines()

final_json = []
for line in log_lines:
    parsed_lines = parse_log_line(line)
    if parsed_lines:
        final_json.extend(parsed_lines)

print(json.dumps(final_json, indent=4))
