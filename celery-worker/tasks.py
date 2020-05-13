import time
import subprocess
import json

from celery import Celery
from redis import Redis
from datetime import datetime

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task(name = "tasks.parse_and_store")
def parse_and_store(replay_file: str) -> None:
    """
    Celery task to take the replay file, send to the parser, 
    and save the response

    Parameters
    ----------
    replay_file: str The filename of the replay file
    """
    # send the replay to the parser & save
    parsed_replay = replay_file.split(".")[0] + ".json"
    replay_id = parsed_replay.split("/")[-1].split(".")[0]
    subprocess.call("curl parser:5600 -s --data-binary '@%s' > %s" % (replay_file, parsed_replay), shell = True)

    # Update Redis with the completed filename
    r = Redis(
        host = "redis",
        port = 6379,
        db = 0,
        ssl_cert_reqs = None
    )

    # Check for any extra information that's been stored
    stored_data = json.loads(r.get(replay_id))

    r.set(
        replay_id,
        json.dumps(
            {
                # Unpack first so any values in stored data with the same key are overwritten
                **{k: v for k, v in stored_data.items()},
                "id": replay_id,
                "status": "Completed",
                "location": parsed_replay,
                "completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
    )

    # Add the processed ID to the list of completed replays
    r.lpush("completed", replay_id)