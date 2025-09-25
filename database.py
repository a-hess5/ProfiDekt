import sqlite3
from flask import g, current_app

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # access rows like dicts
    return g.db

def init_db():
    db = get_db_connection()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()
