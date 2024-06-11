import re
import json

default_values = {
    "RootOrderID": "",
    "ClordID": "",
    "OrigClordID": "",
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
    match = re.findall(r'(\w+): "([^"]+)"', request_str)
    for key, value in match:
        order_event[key.strip()] = value.strip()
    return {"NewOrder": order_event}

def create_request(order_events):
    request = {
        "CheckRequest": {
            "OrderEventInfos": order_events
        }
    }
    return json.dumps(request, indent=2)

def process_stream(file_path, batch_size=1000):
    with open(file_path, 'r') as file:
        batch = []
        for line in file:
            requests = line.split("order_event_uuid")
            for request_str in requests[1:]:
                batch.append(parse_request("order_event_uuid" + request_str))
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
        if batch:
            yield batch

def main(file_path):
    for batch in process_stream(file_path):
        request_json = create_request(batch)
        print(request_json)

if __name__ == "__main__":
    file_path = "test.txt"
    main(file_path)
