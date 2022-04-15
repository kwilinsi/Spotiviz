import os.path

PREPROCESSING_DIR = 'preprocessing'

PROJECT_SETUP_SCRIPT = 'project_setup.sql'

CLEAN_STREAMING_HISTORY_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                              'clean_streaming_history.sql')

CORRECT_DATE_ANOMALIES_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                             'correct_date_anomalies.sql')

CHECK_PROJECT_EXISTS = 'SELECT name FROM Projects WHERE name = ?;'

ADD_PROJECT_ENTRY = 'INSERT OR IGNORE INTO Projects ' \
                    '(name, database_path) VALUES (?, ?);'

GET_PROJECT_PATH = 'SELECT database_path FROM Projects WHERE name = ?;'

UPDATE_PROJECT_PATH = 'UPDATE Projects SET database_path=? WHERE name = ?;'

CLEAR_ALL_PROJECTS = 'DELETE FROM Projects WHERE TRUE;'

ADD_DOWNLOAD = 'INSERT OR IGNORE INTO Downloads (path, name, download_date) ' \
               'VALUES (?, ?, ?);'

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

GET_LAST_END_TIME = 'SELECT MAX(DATE(SHR.end_time)) ' \
                    'FROM StreamingHistoryRaw SHR ' \
                    'LEFT JOIN StreamingHistories SH ' \
                    'ON SHR.history_id = SH.id ' \
                    'LEFT JOIN Downloads D ON SH.download_id = D.id ' \
                    'WHERE D.id = ?;'

UPDATE_DOWNLOAD_DATE = 'UPDATE Downloads ' \
                       'SET download_date = ? WHERE id = ?;'

GET_ALL_INCLUDED_DATES = 'SELECT DATE(end_time) d ' \
                         'FROM StreamingHistory ' \
                         'GROUP BY d ORDER BY d;'

ADD_DATE = 'INSERT INTO ListenDates (day, has_listen) VALUES (?, ?);'

GET_DOWNLOAD_DATES = 'SELECT DATE(download_date) FROM Downloads;'

GET_ALL_DATES = 'SELECT day FROM ListenDates;'

UPDATE_DATE_MISSING_STATUS = 'UPDATE ListenDates ' \
                             'SET is_missing = ? WHERE day = ?;'
