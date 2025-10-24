"""
Initial import script for PokiDekt database.
This script should only be run once during initial setup to populate the database.
WARNING: This will replace the cards table with data from the CSV file.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Define paths
csv_path = script_dir / "card_csv" / "cards22.csv"
db_path = script_dir / "instance" / "pokidekt_database.db"

# Ensure instance directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

# Validate CSV file exists
if not csv_path.exists():
    raise FileNotFoundError(f"CSV file not found at: {csv_path}")

print(f"Reading CSV from: {csv_path}")
print(f"Database location: {db_path}")

# Confirm before proceeding
confirm = input("\nWARNING: This will replace the 'cards' table. Continue? (yes/no): ")
if confirm.lower() != "yes":
    print("Import cancelled.")
    exit()

# Read CSV
df = pd.read_csv(csv_path)
print(f"Loaded {len(df)} cards from CSV")

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create table (drops existing one)
cursor.executescript("""
DROP TABLE IF EXISTS cards;

CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_year TEXT NOT NULL,
    name TEXT NOT NULL,
    card_type TEXT NOT NULL,
    hp REAL,
    poke_type TEXT,
    card_number INTEGER,
    room_number TEXT,
    title TEXT,
    height TEXT,
    prof_year TEXT,
    ability_name TEXT,
    ability_description TEXT,
    attack_name TEXT,
    attack_type TEXT,
    attack_damage REAL,
    attack_description TEXT,
    weakness TEXT,
    resistance TEXT,
    retreat_cost INTEGER,
    extra_rule TEXT,
    flavor_text TEXT,
    image_path TEXT
);

CREATE INDEX idx_card_name ON cards(name);
CREATE INDEX idx_card_type ON cards(card_type);
""")

# Import data from CSV
df.to_sql("cards", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print(f"✓ Successfully imported {len(df)} cards into pokidekt_database.db")