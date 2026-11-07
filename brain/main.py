# TODO: look into logging library; use it to potentially save .json response from api
# TODO: use it to show what level of msg you wanna see (info, warning, etc)

import datetime as dt
import os
import logging
import json
import argparse

import httpx
from dotenv import load_dotenv


log = logging.getLogger(__name__)


def main():
    load_dotenv()

    arg_parser = argparse.ArgumentParser(prog="brains :)")
    arg_parser.add_argument("--verbose", "-v", action="count", default=0)
    args = arg_parser.parse_args()

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(
        level=levels[min(args.verbose, len(levels) - 1)],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    lib_level = logging.DEBUG if args.verbose >= 3 else logging.WARNING
    logging.getLogger("httpx").setLevel(lib_level)
    logging.getLogger("httpcore").setLevel(lib_level)

    dump_log = logging.getLogger("rawjson")
    dump_log.propagate = False

    if args.verbose >= 3:
        file_handler = logging.FileHandler("mbta_responses.log", mode="w")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        dump_log.addHandler(file_handler)

    base_url = "https://api-v3.mbta.com/"

    poll_interval = int(os.environ["POLL_INTERVAL"])
    default_station = os.environ["DEFAULT_STATION"].lower()
    active_line = os.environ["ACTIVE_LINE"].title()
    default_direction = os.environ["DEFAULT_DIRECTION"].lower()
    api_key = os.environ.get("API_KEY", "fallback")

    if api_key == "fallback":
        log.warning("No API key set. You will be severely rate limited.")

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
        log.debug(
            "%s -> %s in %.0f ms",
            endpoint,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )
        response.raise_for_status()
        data = response.json()
        if args.verbose >= 3:
            dump_log.debug(f"{endpoint} {json.dumps(data, indent=2)}")
        return data

    active_route = mbta_fetch(f"routes/{active_line}")["data"]
    normalized_directions = [
        direction.lower() for direction in active_route["attributes"]["direction_names"]
    ]
    if default_direction not in normalized_directions:
        raise ValueError(
            f"Direction '{default_direction}' not valid for {active_line} line. "
            f"Options: {normalized_directions}"
        )

    active_direction = normalized_directions.index(default_direction)
    log.info(
        "Line = %s direction = %s (id %s)",
        active_line,
        default_direction,
        active_direction,
    )

    active_station = ""
    station_list = mbta_fetch("stops", {"filter[route]": active_line})["data"]
    log.debug(f"Fetched {len(station_list)} stops for {active_line} line.")
    for station in station_list:
        if station["attributes"]["name"].lower() == default_station:
            active_station = station["id"]
            break

    if active_station:
        log.info(f"Resolved station '{default_station}' to id {active_station}")
    else:
        raise ValueError(
            f"No station matched '{default_station}' on {active_line} line."
        )

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

        for y in predictions_list:
            attr = y["attributes"]
            log.debug(
                "Prediction at %s: arrival=%s departure=%s",
                active_station,
                attr["arrival_time"],
                attr["departure_time"],
            )

        for x in predictions_list[:2]:
            attr = x["attributes"]
            time = attr["arrival_time"] or attr["departure_time"]
            # Presently potentially incompatible with terminus stations
            minutes = (
                dt.datetime.fromisoformat(time) - dt.datetime.now(dt.timezone.utc)
            ).total_seconds() / 60
            minutes_list.append(round(minutes))

        return minutes_list


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        log.error("%s", e)
        raise SystemExit(1)
