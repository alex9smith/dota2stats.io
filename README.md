# dota2stats.io
![](https://github.com/alex9smith/dota2stats.io/workflows/Build%20App%20&%20Worker%20Images/badge.svg)      ![](https://github.com/alex9smith/dota2stats.io/workflows/Deploy%20Site/badge.svg)

The stack behind [dota2stats.io](https://dota2stats.io).

Wraps OpenDota's [replay parser](https://github.com/odota/parser/) to provide a hosted API and web interface for parsing Dota 2 replay files into JSON objects.

## Usage
Anyone can upload a replay file via the form on the homepage. This kicks off the replay parser and adds data from the match to the database. Alternatively, call the HTTP API from any other program. 

See [the homepage](https://dota2stats.io) for documentation on the API.

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