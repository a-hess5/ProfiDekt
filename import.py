import sqlite3
import pandas as pd

csv_path = "C:\\Users\\aug30\\Downloads\\cards22.csv"  # Update path to new csv
df = pd.read_csv(csv_path)


db_path = "instance\\pokidekt_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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
""")


df.to_sql("cards", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Works I think")
