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
    "Order_Action": "",
    "CheckContext": {
        "Checks": []
    },
    "CheckOverrides": []
}

def parse_request(request_str):
    order_event = default_values.copy()
    match = re.findall(r'(\w+):\s*"([^"]+)"', request_str)
    for key, value in match:
        if key in order_event:
            order_event[key.strip()] = value.strip()
        elif key == "RISKPARAMS":
            order_event["CheckContext"]["Checks"] = [val for val in value.split('|') if val]
    return {"NewOrder": order_event}

def parse_file(file_path):
    order_events = []
    
    with open(file_path, 'r') as file:
        for line in file:
            requests = line.split("order_event_uuid")
            for request_str in requests[1:]:
                order_events.append(parse_request("order_event_uuid" + request_str))
    
    return order_events

def create_request(order_events):
    request = {
        "CheckRequest": {
            "OrderEventInfos": order_events
        }
    }
    
    return json.dumps(request, indent=2)


file_path = "test.txt"
order_events = parse_file(file_path)
request_json = create_request(order_events)
print(request_json)