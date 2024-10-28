from fastapi import FastAPI, HTTPException
from task import Task
from typing import Dict, Any

app = FastAPI()

tasks: Dict[str, Task] = {}

task_id_counter = 1
def generate_task_id():
    global task_id_counter
    task_id = str(task_id_counter)
    task_id_counter += 1
    return task_id

@app.post("/tasks", response_model = dict)
def create_task(task_type: str, parameters: Dict[str, Any]):
    task_id = generate_task_id()
    
    task = Task(
        task_id = task_id,
        task_type = task_type,
        parameters = parameters)
    
    tasks[task_id] = task
    return {"message": "Task created", "task_id": task_id}

@app.get("/tasks/{task_id}", response_model=dict)
def get_task(task_id: str):
    task = tasks.get(task_id)
    if task:
        return task.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    
@app.get("/tasks", response_model=dict)
def get_all_tasks():
    return {task_id: task.to_dict() for task_id, task in tasks.items()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)