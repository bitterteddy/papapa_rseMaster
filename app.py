from flask import Flask, jsonify, request, render_template
from task import Task
from parser_methods.soup_parser import SoupParser
from parser_methods.regex_parser import RegexParser
from concurrent.futures import ThreadPoolExecutor
import threading
import os
from sqlalchemy.exc import SQLAlchemyError
from database import initialization, create_results_table, insert_parsing_results

app = Flask(__name__, static_folder="papaparse_dir", template_folder="papaparse_dir/templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dynamic_parsing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

initialization(app)

tasks = {}
task_id_counter = 1
task_lock = threading.Lock()
executor = ThreadPoolExecutor(max_workers=5)

def generate_task_id():
    global task_id_counter
    with task_lock:
        task_id = str(task_id_counter)
        task_id_counter += 1
    return task_id

def run_task(task):
    try:
        task.start()
        if task.type == "parse":
            parser = SoupParser()
            urls = task.parameters.get("urls", [])
            container_selector = task.parameters.get("container_selector")  
            parse_parameters = task.parameters.get("parse_parameters", {})

            all_results = []
            print(f"Parsing URLs: {urls}")
            for url in urls:
                if task.is_stopped():
                    break
                if task.is_paused():
                    continue 

                print(f"Parsing URL: {url}")
                result = parser.parse(url, parse_parameters)
                print(f"Parsed result: {result}")
                all_results.extend(result)
            
            if not task.is_stopped():
                task.complete(all_results)
        elif task.type == "regex_parse":
            parser = RegexParser()
            urls = task.parameters.get("urls", [])
            regex_parameters = task.parameters.get("regex_patterns", [])

            all_results = []
            for url in urls:
                if task.is_stopped():
                    break
                if task.is_paused():
                    continue
                result = parser.parse(url, {"regex_patterns": regex_parameters})
                all_results.extend(result)

            if not task.is_stopped():
                task.complete(all_results)
        else:
            task.fail(f"Unknown task type: {task.type}")
    except Exception as e:
        task.fail(f"Error: {str(e)}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    task_type = data.get('task_type')
    parameters = data.get('parameters', {})

    print(parameters)

    if not task_type or not isinstance(parameters, dict):
        return jsonify({"error": "Invalid input"}), 400

    task_id = generate_task_id()
    task = Task(task_id=task_id, task_type=task_type, parameters=parameters)
    tasks[task_id] = task

    threading.Thread(target=run_task, args=(task,)).start()

    return jsonify({"message": "Task created", "task_id": task_id})

@app.route('/tasks/<task_id>/start', methods=['POST'])
def start_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task.is_paused() or task.is_stopped():
        task._paused = False  
        task._stopped = False
        threading.Thread(target=run_task, args=(task,)).start()
        return jsonify({"message": f"Task {task_id} resumed and started."})

    return jsonify({"error": "Task is already running."}), 400

@app.route('/tasks/<task_id>/pause', methods=['POST'])
def pause_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task.is_paused() or task.is_stopped():
        return jsonify({"error": f"Task {task_id} is already paused or stopped."}), 400
    
    task._paused = True
    return jsonify({"error": f"Task {task_id} is paused."}), 400

@app.route('/tasks/<task_id>/stop', methods=['POST'])
def stop_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.is_stopped():
        return jsonify({"error": "Task {task_id} is already stopped."}), 400

    task._stopped = True
    return jsonify({"message": f"Task {task_id} stopped."})


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks.get(task_id)
    if task:
        return jsonify(task.to_dict())
    else:
        return jsonify({"error": "Task not found"}), 404


@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    return jsonify({task_id: task.to_dict() for task_id, task in tasks.items()})

@app.route('/parse_and_store', methods=['POST'])
def parse_and_store():
    data = request.json

    table_name = f"parsed_results_{data.get('task_id')}"
    elements = data.get("parameters", {}).get("elements", [])
    results = data.get("results", [])

    if not elements or not results:
        return jsonify({"error": "Invalid input. 'elements' and 'results' are required."}), 400

    try:
        create_results_table(table_name, elements)

        insert_parsing_results(table_name, results)

        return jsonify({"message": f"Results stored in table '{table_name}'"}), 201
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
