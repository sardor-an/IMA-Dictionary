-- Table: User
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Word
CREATE TABLE Word (
    id SERIAL PRIMARY KEY,
    word VARCHAR(255) UNIQUE NOT NULL,
    phonetic VARCHAR(255),
    definition TEXT NOT NULL,
    synonym TEXT,
    antonym TEXT,
    example TEXT,
    class VARCHAR(50) NOT NULL
);

CREATE TABLE Wordlist (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    owner_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Wordlist_Word (
    wordlist_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    PRIMARY KEY (wordlist_id, word_id),
    FOREIGN KEY (wordlist_id) REFERENCES Wordlist(id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES Word(id) ON DELETE CASCADE
);


-- printing: worksheets and quized