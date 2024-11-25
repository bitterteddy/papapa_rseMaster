from fastapi import FastAPI, HTTPException, BackgroundTasks
from task import Task
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from soup_parser import SoupParser

app = FastAPI()

tasks: Dict[str, Task] = {}

executor = ThreadPoolExecutor(max_workers=5)

task_id_counter = 1
def generate_task_id():
    global task_id_counter
    task_id = str(task_id_counter)
    task_id_counter += 1
    return task_id

@app.post("/tasks", response_model = dict)
def create_task(task_type: str, parameters: Dict[str, Any], background_tasks: BackgroundTasks):
    task_id = generate_task_id()
    
    task = Task(
        task_id = task_id,
        task_type = task_type,
        parameters = parameters)
    
    tasks[task_id] = task

    background_tasks.add_task(run_task, task)

    return {"message": "Task created", "task_id": task_id}

def run_task(task: Task):
    try:
        task.start()
        if task.type == "parse":
            parser = SoupParser()
            urls = task.parameters.get("urls", [])
            parse_parameters = task.parameters.get("parse_parameters", {})

            all_results = []
            with executor as pool:
                futures = [pool.submit(parser.parse, url, parse_parameters) for url in urls]

                for future in futures:
                    try:
                        result = future.result()
                        all_results.extend(result)
                    except Exception as e:
                        print(f"Error processing a page: {e}")

            task.complete(all_results)
        else:
            task.fail(f"Unknown task type: {task.type}")
    except Exception as e:
        task.fail(f"Error: {str(e)}")

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