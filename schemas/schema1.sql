-- Commands Table
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    args TEXT,
    desc TEXT
);

-- Tags Table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL UNIQUE
);

-- Junction Table (Many-to-Many relationship between commands and tags)
CREATE TABLE command_tags (
    command_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (command_id, tag_id)
);