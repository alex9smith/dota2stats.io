# dota2stats.io
![](https://github.com/alex9smith/dota2stats.io/workflows/Build%20App%20&%20Worker%20Images/badge.svg)      ![](https://github.com/alex9smith/dota2stats.io/workflows/Deploy%20Site/badge.svg)

The stack behind [dota2stats.io](https://dota2stats.io).

Wraps OpenDota's [replay parser](https://github.com/odota/parser/) to provide a hosted API and web interface for parsing Dota 2 replay files into JSON objects.

## Using the service
Anyone can upload a replay file via the form on the homepage. This kicks off the replay parser and adds data from the match to the database. Alternatively, call the HTTP API from any other program. 

See [the homepage](https://dota2stats.io) for documentation on the API.

### Parsing the results
The parsed replay is a text file, where each line is an event in the match stored as JSON.
A helper class `ReplaySummariser` is provided in `scripts/helpers/parser.py` which turns this output
into something useful.

#### Fantasy points
Fantasy points have been broken in the Dota 2 client for a while, but they can be calculated by the `ReplaySummariser`.
See `scripts/fantasy_points.py` for an example.

To install dependencies and run the script,

1. Make sure you have Python >= 3.8 installed and in your path
2. Clone this repository
3. From the repository root run `python -m venv venv` to create a new virtual environment
4. Run `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows) to activate the virtual environment
5. Run `pip install -r requirements.txt` to install dependencies
6. Run the script with `python scripts/fantasy_points.py /path/to/replay/file.dem`

## Architecture
dota2stats.io is made up of 4 components:
* Web front-end (Python/Flask)
* Replay parser (OpenDota's Java parser)
* Task queue & file database (Redis)
* Task worker (Python/Celery)

The front-end is the only component accessible outside the network.
Docker volumes are used to provide persistent storage for the uploaded replay files.

When the front-end recieves a replay file it saves the file to disk then kicks off a Celery task. It's this task that passes the file to the replay parser, stores the results and updates the status in Redis.

## Deployment
The whole app is launched via `docker-compose`, and the front-end is accessible on port `5000`.
```
docker-compose build
docker-compose up
```

CD is managed through two workflows using Github Actions.
When a PR is opened, the first workflow (`build_images.yml`) tries to build the Docker images in `app` and `celery-worker`.
The second workflow (`deploy.yml`) runs when a commit is made to `master` and deploys the new `master` branch to the hosting server.
