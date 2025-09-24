import sqlite3
import os
from flask import current_app, g


def get_db_connection():
    """Establishes a connection to the database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db


def init_db():
    """
    Initializes the database. If the database file does not exist,
    it creates it and runs the schema.sql script.
    """
    db_path = current_app.config['DATABASE']
    # Check if the database already exists.
    if not os.path.exists(db_path):
        print("Creating new database...")
        # Connecting to a non-existent file will create it.
        db = get_db_connection()
        try:
            with current_app.open_resource('schema.sql') as f:
                db.executescript(f.read().decode('utf8'))
            print("Database initialized successfully from schema.sql.")
        except FileNotFoundError:
            print("ERROR: schema.sql not found. Cannot initialize database.")
        except Exception as e:
            print(f"An error occurred during database initialization: {e}")
    else:
        print("Database already exists.")

