from sqlalchemy import Table, Column, String, Integer, Text, Boolean, MetaData, ForeignKey, update, insert
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import json
from task import Task

db = SQLAlchemy()
metadata = MetaData()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tasks: Mapped[list["TaskModel"]] = relationship(
        "TaskModel",
        back_populates="user",
        cascade="all, delete",
    )
    
    def __init__(self, name, mail, pswrd) -> None:
        self.username = name
        self.email = mail
        self.password = pswrd
    
    def __repr__(self) -> str:
        return '<User %r>' % self.name

class TaskModel(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(120), nullable=False)
    task_type = db.Column(db.String(120), nullable=False)
    parameters = db.Column(db.Text, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="tasks",
    )
    
    def __init__(self, user: User, status: str, task_type: str, parameters: str, err_msg: str = "") -> None:
        # self.id = task_id
        self.status = status
        self.task_type = task_type
        self.parameters = parameters
        self.error_message = err_msg
        self.user_id = user.id
        self.user = user
    
    @classmethod
    def from_task_and_user(cls, task:Task, user:User):
        pars = json.dumps(task.parameters)
        # return cls(task.task_id, user, task.status, task.type, pars, task.error_message)
        return cls(user, task.status, task.type, pars, task.error_message)
    
    def __repr__(self) -> str:
        return '<Task %r>' % self.id
 
def create_standart_tables(app):
    with app.app_context():
        # metadata.create_all(bind=db.engine)
        db.create_all()

def initialization(app):
    db.init_app(app)
    create_standart_tables(app)

def create_results_table(table_name, elements):
    columns = [
        Column("id", Integer, primary_key=True, autoincrement=True),  # ID ñòîëáåö
    ]

    for element in elements:
        column_name = element["name"]
        column_type = Text if element.get("multiple", False) else String(255)
        columns.append(Column(column_name, column_type))

    table = Table(table_name, metadata, *columns, extend_existing=True)
    metadata.create_all(bind=db.engine)
    return table

def insert_parsing_results(table_name, results):
    table = Table(table_name, metadata, autoload_with=db.engine)
    insert_values = [
        {key: (",".join(value) if isinstance(value, list) else value) for key, value in result.items()}
        for result in results
    ]
    execute_command(table.insert().values(insert_values))

def update_table(table, updates: dict):
    execute_command(update(table).where(table.c.id == table.id).values(updates))

def insert_to_table(app, item):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            session.add(item)
            session.commit()
        except Exception as e:
            print(f"Unable to add {item}: {e}")
        session.close()

def execute_command(com):
    with db.engine.connect as conn:
        conn.execute(com)
        conn.commit()