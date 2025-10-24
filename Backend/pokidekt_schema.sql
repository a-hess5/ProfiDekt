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