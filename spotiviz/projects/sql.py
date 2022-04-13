import os.path

PREPROCESSING_DIR = 'preprocessing'

PROJECT_SETUP_SCRIPT = 'project_setup.sql'

CLEAN_STREAMING_HISTORY_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                              'clean_streaming_history.sql')

CHECK_PROJECT_EXISTS = 'SELECT name FROM Projects WHERE name = ?;'

ADD_PROJECT_ENTRY = 'INSERT OR IGNORE INTO Projects (name) VALUES (?);'

CLEAR_ALL_PROJECTS = 'DELETE FROM Projects WHERE TRUE;'

ADD_DOWNLOAD = 'INSERT OR IGNORE INTO Downloads (path, name) VALUES (?, ?);'

ADD_STREAMING_HISTORY = 'INSERT OR IGNORE INTO StreamingHistories (' \
                        'download_id, file_name, start_time) VALUES (?, ?, ?);'

ADD_RAW_STREAM = 'INSERT INTO StreamingHistoryRaw (history_id, position, ' \
                 'end_time, artist_name, track_name, ms_played) ' \
                 'VALUES (?, ?, ?, ?, ?, ?);'

UPDATE_DOWNLOAD_TIME = 'UPDATE Downloads SET start_time = (' \
                       'SELECT start_time FROM StreamingHistories ' \
                       'WHERE download_id = ? ' \
                       'ORDER BY datetime(start_time) LIMIT 1) ' \
                       'WHERE id = ?;'

GET_ALL_INCLUDED_DATES = 'SELECT DATE(end_time) date ' \
                         'FROM StreamingHistoryRaw ' \
                         'GROUP BY date ORDER BY date;'

ADD_DATE = 'INSERT INTO Dates (day, has_listen) VALUES (?, ?);'
