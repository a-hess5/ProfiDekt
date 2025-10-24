"""
Initial import script for MagiProf database.
This script imports both cards22.csv and cardsMagi25.csv into the magiprof database.
This script should only be run once during initial setup to populate the database.
WARNING: This will replace the 'cards' table with data from the CSV files.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Define paths
csv_path_22 = script_dir / "card_csv" / "cards22.csv"
csv_path_magi = script_dir / "card_csv" / "cardsMagi25.csv"
db_path = script_dir / "instance" / "magiprof_database.db"

# Ensure instance directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

# Validate CSV files exist
if not csv_path_22.exists():
    raise FileNotFoundError(f"CSV file not found at: {csv_path_22}")
if not csv_path_magi.exists():
    raise FileNotFoundError(f"CSV file not found at: {csv_path_magi}")

print(f"Reading CSV files:")
print(f"  1. {csv_path_22}")
print(f"  2. {csv_path_magi}")
print(f"Database location: {db_path}")

# Confirm before proceeding
confirm = input("\nWARNING: This will replace the 'cards' table. Continue? (yes/no): ")
if confirm.lower() != "yes":
    print("Import cancelled.")
    exit()

# Read CSVs
df_22 = pd.read_csv(csv_path_22)
df_magi = pd.read_csv(csv_path_magi)
print(f"Loaded {len(df_22)} cards from cards22.csv")
print(f"Loaded {len(df_magi)} cards from cardsMagi25.csv")

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create table (drops existing one)
cursor.executescript("""
DROP TABLE IF EXISTS cards;

CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_year TEXT NOT NULL,
    card_color TEXT,
    card_name TEXT NOT NULL,
    alt_name TEXT,
    mana_value TEXT,
    type1 TEXT,
    type2 TEXT,
    type3 TEXT,
    type4 TEXT,
    type5 TEXT,
    type6 TEXT,
    rules_text1 TEXT,
    rules_text2 TEXT,
    rules_text3 TEXT,
    rules_text4 TEXT,
    rules_text5 TEXT,
    flavor_text TEXT,
    power TEXT,
    toughness TEXT,
    department TEXT,
    printing TEXT,
    image_filepath TEXT
);

CREATE INDEX idx_card_name ON cards(card_name);
CREATE INDEX idx_department ON cards(department);
""")

# Import data from both CSVs
# Note: cards22.csv has different column names, so we rename them to match the schema
df_22_renamed = df_22.rename(columns={
    'name': 'card_name',
    'image_path': 'image_filepath'
})

# Select only the columns that exist in our schema
df_22_select = df_22_renamed[['card_year', 'card_name', 'image_filepath']]
# Add missing columns with None values for MagiProf schema compatibility
for col in ['card_color', 'alt_name', 'mana_value', 'type1', 'type2', 'type3',
            'type4', 'type5', 'type6', 'rules_text1', 'rules_text2', 'rules_text3',
            'rules_text4', 'rules_text5', 'flavor_text', 'power', 'toughness',
            'department', 'printing']:
    if col not in df_22_select.columns:
        df_22_select[col] = None

# Reorder columns to match table schema
schema_columns = ['card_year', 'card_color', 'card_name', 'alt_name', 'mana_value',
                  'type1', 'type2', 'type3', 'type4', 'type5', 'type6', 'rules_text1',
                  'rules_text2', 'rules_text3', 'rules_text4', 'rules_text5', 'flavor_text',
                  'power', 'toughness', 'department', 'printing', 'image_filepath']
df_22_select = df_22_select[schema_columns]

df_magi_select = df_magi[schema_columns]

# Combine dataframes
df_combined = pd.concat([df_22_select, df_magi_select], ignore_index=True)

# Import data from combined CSV
df_combined.to_sql("cards", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print(f"✓ Successfully imported {len(df_combined)} total cards into magiprof_database.db")
print(f"  - {len(df_22_select)} cards from cards22.csv")
print(f"  - {len(df_magi_select)} cards from cardsMagi25.csv")