
from sqlalchemy import Table, Column, String, Integer, Text, Boolean, MetaData
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
metadata = MetaData()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def __init__(self, name, mail, pswrd) -> None:
        self.username = name
        self.email = mail
        self.password = pswrd
    
    def __repr__(self) -> str:
        return '<User %r>' % self.name
 
def create_standart_tables():
    metadata.create_all(bind=db.engine)

def initialization(app):
    db.init_app(app)

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

    with db.engine.connect() as conn:
        conn.execute(table.insert().values(insert_values))
        conn.commit()
