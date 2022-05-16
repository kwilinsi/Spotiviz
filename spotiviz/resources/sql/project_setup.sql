/*
 * These SQL instructions set up the sqlite database for a specific project.
 * This is executed whenever a new project is created.
 *
 * This creates every permanent table and view used by the project.
 */

DROP TABLE IF EXISTS Downloads;
DROP TABLE IF EXISTS StreamingHistories;
DROP TABLE IF EXISTS StreamingHistoryRaw;
DROP TABLE IF EXISTS Artists;
DROP TABLE IF EXISTS Tracks;
DROP TABLE IF EXISTS StreamingHistory;
DROP TABLE IF EXISTS ListenDates;

DROP VIEW IF EXISTS StreamingHistoryFull;

/*
 * The Downloads table contains a list of Spotify downloads.
 *
 * Each download has a unique, auto-incrementing ID; a path to the download's
 * folder; a name; and a start date.
 */
CREATE TABLE Downloads
(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    path          TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    start_time    TIMESTAMP,
    download_date DATE
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
 * The Artists table is simply a list of artist names and ids (for smaller
 * storage in other tables). It's used mainly for foreign key references.
 *
 * Note that this typically does NOT include an 'Unknown Artist' entry. If a
 * listen was 'Unknown Track' by 'Unknown Artist', then that won't put 'Unknown
 * Artist' in this table. But there are actual artists on Spotify with the name
 * 'Unknown Artist'. If there's a listen to a valid track name by 'Unknown
 * Artist', then it will appear in this table.
 */
CREATE TABLE Artists
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    UNIQUE (name)
);

/*
 * This is similar to the Artists table, in that it's a list of track with
 * a unique id used primarily for foreign key references. It helps with grouping
 * by tracks because the group can be performed across only the id rather than
 * both the artist and the track name.
 *
 * Note that this does NOT include an 'Unknown Track' entry unless a real track
 * with that name was streamed. See the Artists table documentation for more
 * information.
 */
CREATE TABLE Tracks
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id INTEGER,
    name      TEXT,
    FOREIGN KEY (artist_id) REFERENCES Artists (id),
    UNIQUE (artist_id, name)
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
    position  INTEGER PRIMARY KEY,
    end_time  TIMESTAMP NOT NULL,
    track_id  INTEGER,
    ms_played INTEGER   NOT NULL,
    FOREIGN KEY (track_id) REFERENCES Tracks (id)
);

/*
 * The ListenDates table is used for resolving issues with missing data. It
 * contains one entry for every date between the very first and very last
 * recorded listen dates in a project.
 *
 * Each date is matched with booleans indicating whether there is any listen
 * history data present for that date and whether it is known as a missing date.
 *
 * Missing dates are defined as those that were not captured by any of the
 * Spotify downloads associated with a project. Spotify downloads have a
 * duration of one year (or less if the Spotify account is newer than that).
 * If one download ends January 1st 2020 and another ends February 1st 2022,
 * all the dates from 01-02-20 to 01-31-21 will be marked missing, because they
 * are not captured in either download.
 *
 * Note that any entry where is_missing is TRUE should also list has_listen as
 * FALSE. Having no data doesn't *define* missing data, but missing data should
 * not have any data.
 */
CREATE TABLE ListenDates
(
    day        DATE,
    has_listen INTEGER NOT NULL CHECK (has_listen IN (0, 1)),
    is_missing BOOLEAN
);

/*
 * This view is simply an expansion on StreamingHistory that uses joins with the
 * Artists and Tracks tables to provide full artist and track names.
 */
CREATE VIEW StreamingHistoryFull AS
SELECT SH.position,
       SH.track_id,
       A.name AS artist,
       T.name AS track,
       SH.end_time,
       SH.ms_played
FROM StreamingHistory AS SH
         LEFT JOIN Tracks T on T.id = SH.track_id
         LEFT JOIN Artists A on A.id = T.artist_id;
