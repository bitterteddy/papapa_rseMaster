from typing import Any, Dict
import threading


class Task:
    def __init__(self, task_id: str, task_type: str, parameters: Dict[str, Any]):
        self.task_id = task_id
        self.status = "waiting to create..."
        self.type = task_type
        self.parameters = parameters
        self.result = None
        self.error_message = None
        self._paused = False
        self._stopped = False
        self._lock = threading.Lock()

    def start(self):
        self.status = "in progress"
        print(f"Task {self.task_id} - in progress...")

    def complete(self, result: Any):
        self.status = "completed"
        self.result = result
        print(f"Task {self.task_id} - completed!")

    def fail(self, error_message: str):
        self.status = "error"
        self.error_message = error_message
        print(f"Task {self.task_id} failed to complete! Error: {error_message}")

    def is_paused(self):
        return self._paused
    
    def pause(self):
        with self._lock:
            self._paused = True
            self.status = "paused"
            print(f"Task {self.task_id} - paused!")

    def resume(self):
        with self._lock:
            self._paused = False
            self.status = "in progress"
            print(f"Task {self.task_id} - resumed!")
            print(f"Task {self.task_id} - in progress...")

    def stop(self):
        with self._lock:
            self._stopped = True
            self.status = "stopped"
            print(f"Task {self.task_id} - stopped!")

    def is_paused(self):
        return self._paused

    def is_stopped(self):
        return self._stopped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "type": self.type,
            "parameters": self.parameters,
            "result": self.result,
            "error_message": self.error_message,
        }
