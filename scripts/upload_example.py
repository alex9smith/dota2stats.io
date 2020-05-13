import requests
import sys

from time import sleep

if __name__ == "__main__":
    """
    Run with
    python upload_example.py /path/to/replay.dem
    """
    replay_file = sys.argv[1]

    response = requests.post(
        "http://localhost:5000/api/v1/upload",
        files = {
            "file": open(replay_file, "rb")
        },
        # Store any other data along with the replay by
        # sending it as form-encoded data
        data = {
            "radiant_team": "The Radiant Team Name",
            "dire_team": "The Dire Team Name"
        }
    )
    request_id = response.json()["id"]
    print(f"Request ID: {request_id}")

    wait = 2
    sleep(wait)
    while response.status_code == 201:
        response = requests.get("http://localhost:5000/api/v1/status/" + request_id)
        wait = min(wait * 2, 60)
        print(f"Parsing not finished. Trying again in {wait} seconds")
        sleep(wait)

    print(response.json())
    download_url = response.json()["location"]
        
    with open("output.json", "wb") as o:
        o.write(requests.get("http://localhost:5000" + download_url).content)