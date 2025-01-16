from flask import Flask, jsonify, request, render_template
from task import Task
from parser_methods.soup_parser import SoupParser
from parser_methods.regex_parser import RegexParser
from concurrent.futures import ThreadPoolExecutor
import threading
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, Float
import sqlite3
import os

app = Flask(__name__, static_folder="papaparse_dir", template_folder="papaparse_dir")

basedir = os.path.abspath("papaparse_dir")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'task_res.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)
                 
CREATE_DB = True

# Declare model
class Result(db.Model):
    __tablename__ = 'result_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    text = db.Column(db.String)
    tags = db.Column(db.String, nullable=True)

    def __init__(self, name, text, tags) -> None:
        super(Result, self).__init__()
        self.name = name
        self.text = text
        self.tags = tags

    def __repr__(self) -> str:
        return '<Question %r>' % self.name

# Schema
class ResultSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'text', 'tags')

multiple_vol_data_schema = ResultSchema(many=True)

def save_results(results):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        for el in results:
            #add some psrsing logic
            r = Result("", "", "")
            try:
                session.add(r)
                session.commit()
            except:
                print('Unable to add ' + r.name + ' to db.')
                continue
        session.close()

if CREATE_DB:
    with app.app_context():
        db.create_all();

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
        elif task.type == "regex_parse":
            parser = RegexParser()
            urls = task.parameters.get("urls", [])
            regex_parameters = task.parameters.get("regex_patterns", [])

            all_results = []
            with executor as pool:
                futures = [pool.submit(parser.parse, url, {"regex_patterns": regex_parameters}) for url in urls]

                for future in futures:
                    try:
                        result = future.result()
                        all_results.extend(result)
                    except Exception as e:
                        print(f"Error processing regex parsing: {e}")

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

    if not task_type or not isinstance(parameters, dict):
        return jsonify({"error": "Invalid input"}), 400

    task_id = generate_task_id()
    task = Task(task_id=task_id, task_type=task_type, parameters=parameters)
    tasks[task_id] = task

    threading.Thread(target=run_task, args=(task,)).start()

    return jsonify({"message": "Task created", "task_id": task_id})


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


if __name__ == '__main__':
    app.run(debug=True)
