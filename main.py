import requests
import json
import sys
from os.path import exists



def main():
    tracking_number = sys.argv[1]
    url = f"https://shopozz.ru/tracking/{tracking_number}?ajax=true"
    headers = {
        'User-Agent': 'My User Agent 1.0',
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    events = data["events"]

    timestamp = 0
    if exists("timestamp.txt"):
        with open("timestamp.txt", "r") as ts_file:
            timestamp = ts_file.read()

    for event in reversed(events):
        if event["timestamp"] > timestamp:
            # send info
            ...

if __name__ == "__main__":
    main()
