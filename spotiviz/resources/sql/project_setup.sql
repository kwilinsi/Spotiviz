/*
 * These SQL instructions set up the sqlite database for a specific project. This is
 * executed whenever a new project is created.
 */

DROP TABLE IF EXISTS Downloads;
DROP TABLE IF EXISTS StreamingHistories;
DROP TABLE IF EXISTS StreamingHistoryRaw;
DROP TABLE IF EXISTS StreamingHistory;

CREATE TABLE Downloads
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    start_time TIMESTAMP
);

CREATE TABLE StreamingHistories
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    download_id INTEGER,
    file_name   TEXT NOT NULL,
    start_time  TIMESTAMP,
    FOREIGN KEY (download_id) REFERENCES Downloads (id),
    UNIQUE (download_id, file_name)
);

CREATE TABLE StreamingHistoryRaw
(
    history_id  INTEGER,
    position    INTEGER,
    end_time    TIMESTAMP,
    artist_name TEXT,
    track_name  TEXT,
    ms_played   INTEGER,
    PRIMARY KEY (history_id, position),
    FOREIGN KEY (history_id) REFERENCES StreamingHistories (id)
);

CREATE TABLE StreamingHistory
(
    position    INTEGER,
    end_time    TIMESTAMP,
    artist_name TEXT,
    track_name  TEXT,
    ms_played   INTEGER
);
