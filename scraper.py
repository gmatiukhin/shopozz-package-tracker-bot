import requests
import json
from datetime import datetime

import logging


def get_status(tracking_number):
    data = get_russian_post_data(tracking_number)

    if data:
        return format_russian_post_event(data[0])
    else:
        data = get_shopozz_data(tracking_number)
        if data:
            return format_shopozz_event(data[0])
    return ""


def format_event(date, event, location, source):
    date = date.strftime("%Y-%m-%d %H-%M-%S")
    message = f"{event}\n{date}\n{location}\n~ {source}"
    return message


def format_russian_post_event(json_data):
    date = datetime.fromisoformat(json_data["date"])
    event = json_data["humanStatus"]
    city = json_data["cityName"]
    country = json_data["countryName"]
    location = ""
    if city:
        location += city + ", "
    location += country
    return format_event(date, event, location, "pochta.ru")


def format_shopozz_event(json_data):
    date = datetime.fromisoformat(json_data["datetime"])
    event = json_data["event"]
    location = json_data["location"]
    return format_event(date, event, location, "shopozz.ru")


def get_shopozz_data(tracking_number):
    url = f"https://shopozz.ru/tracking/{tracking_number}?ajax=true"
    headers = {
        "User-Agent": "Shopozz-package-tracker-bot/1.0",
    }

    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        return data["events"]
    except requests.exceptions.ConnectionError:
        logging.error("Connection refused: shopozz.ru")
    except KeyError as ke:
        logging.error(f"Key not found in 'shopozz.ru' response: {ke}")
    return []


def get_russian_post_data(tracking_number):
    url = "https://www.pochta.ru/api/nano-apps/api/v1/tracking.get-by-barcodes?language=ru"
    payload = [str(tracking_number)]
    headers = {
        "User-Agent": "Shopozz-package-tracker-bot/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, allow_redirects=True
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            return data["detailedTrackings"][0]["trackingItem"][
                "trackingHistoryItemList"
            ]
    except requests.exceptions.ConnectionError:
        logging.error("Connection refused: pochta.ru")
    except KeyError as ke:
        logging.error(f"Key not found in 'pochta.ru' response: {ke}")

    return None
