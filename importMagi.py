import sqlite3
import pandas as pd

csv_path = "card_csv\\cardsMagi25.csv"  # Update path to new csv
df = pd.read_csv(csv_path)


db_path = "instance\\magiprof_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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
    department REAL,
    printing TEXT,
    image_filepath TEXT
);
""")


df.to_sql("cards", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Works I think")
