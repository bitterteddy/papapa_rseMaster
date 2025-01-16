
from sqlalchemy import Table, Column, String, Integer, Text, Boolean, MetaData
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
metadata = MetaData()

def initialization(app):
    db.init_app(app)

def create_results_table(table_name, elements):
    """
    Создает таблицу для результатов парсинга на основе параметров.
    """
    columns = [
        Column("id", Integer, primary_key=True, autoincrement=True),  # ID столбец
    ]

    for element in elements:
        column_name = element["name"]
        column_type = Text if element.get("multiple", False) else String(255)
        columns.append(Column(column_name, column_type))

    # Создаем таблицу
    table = Table(table_name, metadata, *columns, extend_existing=True)
    metadata.create_all(bind=db.engine)  # Создаем таблицу в базе данных
    return table

def insert_parsing_results(table_name, results):
    """
    Добавляет результаты парсинга в таблицу.
    """
    table = Table(table_name, metadata, autoload_with=db.engine)

    # Преобразование данных для записи в таблицу
    insert_values = [
        {key: (",".join(value) if isinstance(value, list) else value) for key, value in result.items()}
        for result in results
    ]

    # Вставка данных
    with db.engine.connect() as conn:
        conn.execute(table.insert(), insert_values)