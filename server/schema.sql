-- Table: User
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Table: Wordlist
CREATE TABLE Wordlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    user_id INTEGER,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Table: Word
CREATE TABLE Word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_eng TEXT NOT NULL,
    text_uz TEXT,
    part_of_speech_id INTEGER,
    definition_id INTEGER,
    synonyms_id INTEGER,
    example_id INTEGER,
    FOREIGN KEY (part_of_speech_id) REFERENCES Part_of_speech(id),
    FOREIGN KEY (definition_id) REFERENCES Definition(id),
    FOREIGN KEY (synonyms_id) REFERENCES Synonyms(id),
    FOREIGN KEY (example_id) REFERENCES Example(id)
);

-- Table: Part_of_speech
CREATE TABLE Part_of_speech (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_of_speech TEXT NOT NULL
);

-- Table: Definition
CREATE TABLE Definition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    definition_en TEXT,
    definition_uz TEXT
);

-- Table: Synonyms
CREATE TABLE Synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synonyms TEXT
);

-- Table: Example
CREATE TABLE Example (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_en TEXT,
    example_uz TEXT
);