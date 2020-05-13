import redis
import json

from datetime import datetime

from typing import NamedTuple, Union, Dict, List, Optional

class TaskStatus(NamedTuple):
    message: str
    error: bool = False
    location: Union[None, str] = None
    other_data: Dict = None


class RedisClient:
    def __init__(self) -> None:
        self.r = redis.Redis(
            host = "redis",
            port = 6379,
            db = 0,
            ssl_cert_reqs = None
        )


    def _set_json(self, id: str, value: Dict) -> bool:
        self.r.set(id, json.dumps(value))


    def _get_json(self, id: str) -> Dict:
        return json.loads(self.r.get(id).decode("utf-8"))


    def _task_exists(self, id: str) -> bool:
        return self.r.exists(id) != 0


    def start_task(self, id: str, values: Optional[Dict] = None) -> bool:
        data = {
            "id": id,
            "status": "Running",
            "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if values:
            # Overwrite possible keys in values with those in data
            data = {**values, **data}

        return self._set_json(
            id = id,
            value = data
        )


    def get_task_status(self, id: str) -> TaskStatus:
        if self._task_exists(id):
            s = self._get_json(id)
            if s["status"] == "Completed":
                return TaskStatus(
                    message = s["status"],
                    location = s["location"],
                    other_data = {k: v for k, v in s.items() if k not in ["status", "location"]}
                )
            else:
                return TaskStatus(message = s["status"], other_data = {k: v for k, v in s.items() if k not in ["status", "location"]})

        else:
            return TaskStatus(message = "Not Found", error = True)

    
    def all_completed_tasks(self) -> List[str]:
        if self._task_exists("completed"):
            return [self.r.lindex("completed", i) for i in range(0, self.r.llen("completed"))]

        else:
            return []