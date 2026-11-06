# MBTA Tracker with CPX Control

Working title.

Personal project to learn API usage.
`brain` controls all things Internet.
`cpx` is CircuitPython code for a Circuit Playground Express.
It interprets serial signals received from `brain` and lights up accordingly.

## Pre-requisites

- An updated Circuit Playground Express.
- Something with WAN access & ability to run Python scripts.
  I'm using a Raspberry Pi Zero W but that is overkill.
  It's just what I had on hand.
- Written in and thus probably requires Python 3.14.
- `pip`

## Setup

Clone this repo and install dependencies:

```sh
git clone <repo url> && cd <repo name>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the example `.env` file and fill it out:

`cp .env.example .env`

| Env               |Example Value | Explanation                                                  |
|-------------------|-------|----------------------------------------------------------|
| API_KEY           |       | Claim yours <a href="https://api-v3.mbta.com/">here.</a> |
| ACTIVE_LINE       | Red   | Red/Blue/Orange/Green-A? Only tested with Red for now. |
| DEFAULT_STATION   | Davis | Station name in plain English                            |
| DEFAULT_DIRECTION | North | Depends on your ACTIVE_LINE.                             |
| POLL_INTERVAL     | 15    |                                                          |
