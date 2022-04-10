/*
 * These SQL instructions set up the sqlite database for a specific project.
 * This is executed whenever a new project is created.
 */

DROP TABLE IF EXISTS Downloads;
DROP TABLE IF EXISTS StreamingHistories;
DROP TABLE IF EXISTS StreamingHistoryRaw;
DROP TABLE IF EXISTS StreamingHistory;

/*
 * The Downloads table contains a list of Spotify downloads.
 *
 * Each download has a unique, auto-incrementing ID; a path to the download's
 * folder; a name; and a start date.
 */
CREATE TABLE Downloads
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    start_time TIMESTAMP
);

/*
 * The StreamingHistories table contains a list of streaming history files.
 *
 * Each streaming history file is associated with a specific download,
 * specified by its id. The file is given only by its name (e.g.
 * StreamingHistory0.json), which is appended to the download's path to get
 * the full path to the history file. This also includes a timestamp for the
 * the first listen in the streaming history.
 */
CREATE TABLE StreamingHistories
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    download_id INTEGER,
    file_name   TEXT NOT NULL,
    start_time  TIMESTAMP,
    FOREIGN KEY (download_id) REFERENCES Downloads (id),
    UNIQUE (download_id, file_name)
);

/*
 * The StreamingHistoryRaw table contains all the contents of the streaming
 * history files given in the StreamingHistories table.
 *
 * Each StreamingHistory#.json file contains a list of Spotify listen records.
 * When the files are parsed, each of those listens is stored in this table.
 * Note however that this table will likely contain duplicate entries.
 */
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

/*
 * The StreamingHistory table is a duplicate of the StreamingHistoryRaw table
 * where the duplicate listens have been removed.
 *
 * Each listen includes a Spotify track name, the artist name, the number of
 * milliseconds spent listening to that song, and the end time that the song
 * stopped playing.
 */
CREATE TABLE StreamingHistory
(
    position    INTEGER,
    end_time    TIMESTAMP,
    artist_name TEXT,
    track_name  TEXT,
    ms_played   INTEGER
);
