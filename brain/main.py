import datetime as dt
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

base_url = "https://api-v3.mbta.com/"

poll_interval = int(os.environ["POLL_INTERVAL"])
default_station = os.environ["DEFAULT_STATION"].lower()
active_line = os.environ["ACTIVE_LINE"].title()
default_direction = os.environ["DEFAULT_DIRECTION"].lower()
api_key = os.environ.get("API_KEY", "fallback")


headers = {
    "x-api-key": api_key,
}


def mbta_fetch(endpoint, params=None):
    response = httpx.get(
        base_url + endpoint,
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


active_route = mbta_fetch(f"routes/{active_line}")["data"]
normalized_directions = active_route["attributes"]["direction_names"]
active_direction = [direction.lower() for direction in normalized_directions].index(
    default_direction
)

active_station = ""
station_list = mbta_fetch("stops", {"filter[route]": active_line})["data"]
for station in station_list:
    if station["attributes"]["name"] == default_station:
        active_station = station["id"]
        break


def get_predictions():
    parameters = {
        "filter[stop]": active_station,
        "filter[route]": active_line,
        "filter[direction_id]": active_direction,
        "sort": "arrival_time",
        "fields[prediction]": "arrival_time,departure_time",
    }

    predictions_list = mbta_fetch("predictions", parameters)["data"]
    minutes_list = []

    for x in predictions_list[:2]:
        attr = x["attributes"]
        time = attr["arrival_time"] or attr["departure_time"]
        minutes = (
            dt.datetime.fromisoformat(time) - dt.datetime.now(dt.timezone.utc)
        ).total_seconds() / 60
        minutes_list.append(round(minutes))

    return minutes_list
