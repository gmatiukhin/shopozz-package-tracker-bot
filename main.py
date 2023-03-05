import requests
import json
import sys
from datetime import datetime

def main():
    tracking_number = sys.argv[1]
    status_message = get_status(tracking_number)
    print(status_message)

def get_status(tracking_number):
    data = get_russian_post_data(tracking_number)

    if data:
        return format_russian_post_event(data[0])
    else:
        data = get_shopozz_data(tracking_number)
        if data:
            return format_shopozz_event(data[0])

def format_event(date, event, location):
    date = date.strftime("%Y-%m-%d %H-%M-%S")
    message = f"{event}\n{date}\n{location}"
    return message

def format_russian_post_event(json_data):
    date = datetime.fromisoformat(json_data["date"])
    event = json_data["humanStatus"]
    city = json_data["cityName"]
    country = json_data["countryName"]
    location = ""
    if not city:
        location += city + ", "
    location += country
    return format_event(date, event, location)

def format_shopozz_event(json_data):
    date = datetime.fromisoformat(json_data["datetime"])
    event = json_data["event"]
    location = json_data["location"]
    return format_event(date, event, location)

def get_shopozz_data(tracking_number):
    url = f"https://shopozz.ru/tracking/{tracking_number}?ajax=true"
    headers = {
        "User-Agent": "Shopozz-package-tracker-bot/1.0",
    }
    response = requests.get(url, headers=headers)

    with open("shopozz.json", "w") as file:
        file.write(response.text)

    data = json.loads(response.text)
    try:
        return data["events"]
    except KeyError:
        return []


def get_russian_post_data(tracking_number):
    url = "https://www.pochta.ru/api/nano-apps/api/v1/tracking.get-by-barcodes?language=ru"
    payload = [str(tracking_number)]
    headers = {
        "User-Agent": "Shopozz-package-tracker-bot/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, allow_redirects=True)

    with open("ru-post.json", "w") as file:
        file.write(response.text)

    data = json.loads(response.text)
    return data["detailedTrackings"][0]["trackingItem"]["trackingHistoryItemList"]


if __name__ == "__main__":
    main()
