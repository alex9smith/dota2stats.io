"""
Upload a Dota 2 replay to the dota2stats.io API, parse the response and calculate
fantasy points for each player.

Usage:
    fantasy_points.py REPLAY_FILE

Options:
    -h --help    show this

Examples:
    fantasy_points.py ./replays/1234567.dem
"""

from docopt import docopt
import requests
import logging
from time import sleep
from helpers.parser import ReplaySummariser, Summary

API_HOST = "https://dota2stats.io"
API_HOST = "http://localhost:5000"

def upload_replay(file: str) -> str:
    """
    Upload a replay to dota2stats.io for parsing
    Parameters
    ----------
    file: The relative path to the replay file

    Returns
    -------
    The replay ID on the dota2stats.io API
    """
    logging.info(f"Uploading replay file at {file} for parsing")
    response = requests.post(
        f"{API_HOST}/api/v1/upload",
        files={"file": open(file, "rb")},
        data={}
    )
    return response.json()["id"]


def fetch_parsed_replay(replay_id: str) -> str:
    """
    Wait for the replay parsing to finish and download the result
    Parameters
    ----------
    replay_id: The replay ID on the dota2stats.io API

    Returns
    -------
    The raw parsed replay data
    """
    logging.info(f"Fetching replay data for replay {replay_id}")
    time_to_wait = 2
    response = requests.get(f"{API_HOST}/api/v1/status/{replay_id}")
    while response.status_code == 201:
        logging.info(f"Parsing not finished. Trying again in {time_to_wait} seconds")
        sleep(time_to_wait)
        time_to_wait = min(time_to_wait * 2, 60)
        response = requests.get(f"{API_HOST}/api/v1/status/{replay_id}")

    data_location = response.json()["location"]
    return requests.get(f"{API_HOST}{data_location}").text


if __name__ == "__main__":
    args = docopt(__doc__)
    logging.basicConfig(level=logging.INFO)

    #replay_id = upload_replay(args["REPLAY_FILE"])
    replay_id = "05e6674e-e1ea-4d27-a10d-0aa470f4caa5"
    replay_id = "05e6674e-e1ea-4d27-a10d-0aa470f4caa5"
    parsed_replay = fetch_parsed_replay(replay_id)
    summary = ReplaySummariser(parsed_replay)
    fantasy_points = summary.fantasy_points()
    print(fantasy_points)