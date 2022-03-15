DROP TABLE IF EXISTS Collections;
DROP TABLE IF EXISTS Downloads;

CREATE TABLE Collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES Collections (id)
);
