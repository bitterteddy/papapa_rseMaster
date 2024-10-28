from typing import Any, Dict

class Task:
    def __init__(self, task_id: str, task_type: str, parameters: Dict[str, Any]):
        self.task_id = task_id
        self.status = "Waiting to create"
        self.type = task_type
        self.parameters = parameters
        self.result = None
        self.error_message = None

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
