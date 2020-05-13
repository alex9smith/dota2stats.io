import os
import json

from uuid import uuid4
from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
from worker import worker
from redis_client import RedisClient
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("homepage.html")


@app.route("/api/v1/upload", methods = ["POST"])
def upload():
    replay = request.files["file"]
    if replay:
        replay_id = str(uuid4())

        replay_filename = os.path.join(
            os.path.sep,
            "app",
            "replays",
            secure_filename(replay_id + ".dem")
        )
        replay.save(replay_filename)

        rc = RedisClient()
        rc.start_task(replay_id, request.form)
        worker.send_task("tasks.parse_and_store", args = [replay_filename])

        return jsonify(
            {
                "id": replay_id,
                "status": "Accepted"
            }
        ), 201

    else:
        return jsonify(
            {
                "id": "None",
                "status": "Rejected",
                "error": "No replay file found"
            }
        ), 406


@app.route("/api/v1/status/<id>", methods = ["GET"])
def get_status(id: str):
    rc = RedisClient()
    status = rc.get_task_status(id)
    if status.message == "Completed" and not status.error:
        content = {
            "id": id,
            "status": status.message,
            "location": url_for('download_replay', id = id)
        }
        status_code = 200

    elif not status.error:
        content = {
            "id": id,
            "status": status.message
        }
        status_code = 201

    else:
        # There's an error, probably this ID wasn't found
        content = {
            "id": id,
            "status": status.message,
            "error": "true"
        }
        status_code = 404

    if status.other_data and not status.error:
        content.update(status.other_data)

    return jsonify(content), status_code


@app.route("/api/v1/download/<id>", methods = ["GET"])
def download_replay(id: str):
    return send_file(
        os.path.join(
            os.path.sep,
            "app",
            "replays",
            secure_filename(id + ".json")
        )
    ), 200


@app.route("/api/v1/all-completed", methods = ["GET"])
def all_completed():
    rc = RedisClient()
    return jsonify({"ids": rc.all_completed_tasks()}), 200