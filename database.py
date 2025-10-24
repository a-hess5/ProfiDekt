import sqlite3
import os
from flask import current_app, g

# ============================================
# MAGIPROF DATABASE FUNCTIONS
# ============================================

def get_magiprof_db_connection():
    """Establishes a connection to the MagiProf database."""
    db = getattr(g, '_magiprof_database', None)
    if db is None:
        db = g._magiprof_database = sqlite3.connect(
            current_app.config['MAGIPROF_DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db


def init_magiprof_db():
    """
    Initializes the MagiProf database. If the database file does not exist,
    it creates it and runs the magiprof_schema.sql script.
    """
    db_path = current_app.config['MAGIPROF_DATABASE']
    if not os.path.exists(db_path):
        print("Creating new MagiProf database...")
        db = get_magiprof_db_connection()
        try:
            with current_app.open_resource('magiprof_schema.sql') as f:
                db.executescript(f.read().decode('utf8'))
            db.commit()
            print("MagiProf database initialized successfully from magiprof_schema.sql.")
        except FileNotFoundError:
            print("ERROR: magiprof_schema.sql not found. Cannot initialize MagiProf database.")
        except Exception as e:
            print(f"An error occurred during MagiProf database initialization: {e}")
    else:
        print("MagiProf database already exists.")


# ============================================
# POKIDEKT DATABASE FUNCTIONS
# ============================================

def get_pokidekt_db_connection():
    """Establishes a connection to the PokiDekt database."""
    db = getattr(g, '_pokidekt_database', None)
    if db is None:
        db = g._pokidekt_database = sqlite3.connect(
            current_app.config['POKIDEKT_DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db


def init_pokidekt_db():
    """
    Initializes the PokiDekt database. If the database file does not exist,
    it creates it and runs the pokidekt_schema.sql script.
    """
    db_path = current_app.config['POKIDEKT_DATABASE']
    if not os.path.exists(db_path):
        print("Creating new PokiDekt database...")
        db = get_pokidekt_db_connection()
        try:
            with current_app.open_resource('pokidekt_schema.sql') as f:
                db.executescript(f.read().decode('utf8'))
            db.commit()
            print("PokiDekt database initialized successfully from pokidekt_schema.sql.")
        except FileNotFoundError:
            print("ERROR: pokidekt_schema.sql not found. Cannot initialize PokiDekt database.")
        except Exception as e:
            print(f"An error occurred during PokiDekt database initialization: {e}")
    else:
        print("PokiDekt database already exists.")