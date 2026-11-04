# MBTA Tracker with CPX Control

Working title.

Personal project to learn API usage.
Brain controls all things Internet.
CPX is CircuitPython code for a Circuit Playground Express. Interprets serial signals received from Brains and lights up accordingly.

Setup:
Clone this repo and set up python:

```sh
git clone <repo url> && cd <repo name>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill out .env file.

- API_KEY: your MBTA V3 API key.
- HOME_STATION: default station to track, using the MBTA stop ID
- DEFAULT_DIRECTION: inbound/outbound?
- DEFAULT_DESTINATION: ashmont/braintree? blank if irrelevant
- POLL_INTERVAL: how often to check data, in seconds
