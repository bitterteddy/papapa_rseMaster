from flask import Flask, jsonify, request, render_template
from task import Task
from parser_methods.soup_parser import SoupParser
from parser_methods.regex_parser import RegexParser
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.exc import SQLAlchemyError
from database import initialization, create_results_table, insert_parsing_results, update_table, insert_to_table
from database import User, TaskModel
import threading
import os
import json

app = Flask(__name__, static_folder="papaparse_dir", template_folder="papaparse_dir/templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dynamic_parsing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

initialization(app)

task_lock = threading.Lock()
executor = ThreadPoolExecutor(max_workers=5)

def run_task(task_model):
    try:
        task = Task(
            task_id=task_model.id,
            task_type=task_model.task_type,
            parameters=json.loads(task_model.parameters)
        )
        task.start()

        if task.type == "parse":
            parser = SoupParser()
            urls = task.parameters.get("urls", []) 
            parse_parameters = task.parameters.get("parse_parameters", {})

            all_results = []
            for url in urls:
                if task.is_stopped():
                    break
                if task.is_paused():
                    continue 

                result = parser.parse(url, parse_parameters)
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

        with app.app_context():
            update_table(task_model, {"status": task.status})

            if task.result:
                table_name = f"parsed_results_{task_model.id}"
                elements = task.parameters.get(elements, [])

                create_results_table(table_name, elements)
                insert_parsing_results(table_name, task.result)

    except Exception as e:
        task.fail(f"Error: {str(e)}")
        with app.app_context():
            update_table(task_model, {
                "status": task.status,
                "error_message": str(e)
                })

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        user = User.query.get(1)
        if not user:
            user = User(name="John Doe", mail="johndoe@example.com", pswrd="password123")
            insert_to_table(app, user)

        data = request.json
        task_type = data.get('task_type')
        parameters = data.get('parameters', {})

        if not task_type or not isinstance(parameters, dict):
            return jsonify({"error": "Invalid input"}), 400

        pars=json.dumps(parameters)
        task_model = TaskModel(user=user, task_type=task_type, parameters=pars, status="created")

        insert_to_table(app, task_model)

        return jsonify({"message": "Task created"})
    except Exception as e:
        return jsonify({"error": f"Error creating task: {str(e)}"}), 500

@app.route('/tasks/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    try: 
        with app.app_context():
            task_model = task_model = TaskModel.query.get(task_id)
            if not task_model:
                return jsonify({"error": "Task not found"}), 404
            
            if task_model.status not in ["stopped", "paused"]:
                return jsonify({"error": f"Task {task_id} cannot be started."}), 400
            
            update_table(task_model, {"status": "in progres..."})
        
        threading.Thread(target=run_task, args=(task_model,)).start()
        
        return jsonify({"message": f"Task {task_id} started."})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# @app.route('/tasks/<task_id>/pause', methods=['POST'])
# def pause_task(task_id):
#     task = tasks.get(task_id)
#     if not task:
#         return jsonify({"error": "Task not found"}), 404
    
#     if task.is_paused() or task.is_stopped():
#         return jsonify({"error": f"Task {task_id} is already paused or stopped."}), 400
    
#     task._paused = True
#     return jsonify({"error": f"Task {task_id} is paused."}), 400

# @app.route('/tasks/<task_id>/stop', methods=['POST'])
# def stop_task(task_id):
#     task = tasks.get(task_id)
#     if not task:
#         return jsonify({"error": "Task not found"}), 404

#     if task.is_stopped():
#         return jsonify({"error": "Task {task_id} is already stopped."}), 400

#     task._stopped = True
#     return jsonify({"message": f"Task {task_id} stopped."})


# @app.route('/tasks/<task_id>', methods=['GET'])
# def get_task(task_id):
#     task = tasks.get(task_id)
#     if task:
#         return jsonify(task.to_dict())
#     else:
#         return jsonify({"error": "Task not found"}), 404


# @app.route('/tasks', methods=['GET'])
# def get_all_tasks():
#     return jsonify({task_id: task.to_dict() for task_id, task in tasks.items()})

if __name__ == '__main__':
    app.run(debug=True)
