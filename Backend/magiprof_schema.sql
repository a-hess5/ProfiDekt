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