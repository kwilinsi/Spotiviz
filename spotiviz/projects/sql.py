PROJECT_SETUP_SCRIPT = 'project_setup.sql'

CHECK_PROJECT_EXISTS = 'SELECT name FROM Projects WHERE name = ?;'

ADD_PROJECT_ENTRY = 'INSERT OR IGNORE INTO Projects (name) VALUES (?);'

CLEAR_ALL_PROJECTS = 'DELETE FROM Projects WHERE TRUE;'

ADD_DOWNLOAD = 'INSERT OR IGNORE INTO Downloads (path) VALUES (?);'

ADD_STREAMING_HISTORY = 'INSERT OR IGNORE INTO StreamingHistories (' \
                        'download_id, file_name) VALUES (?, ?);'

ADD_RAW_STREAM = 'INSERT INTO StreamingHistoryRaw (history_id, position, ' \
                 'end_time, artist_name, track_name, ms_played) ' \
                 'VALUES (?, ?, ?, ?, ?, ?);'

CLEAN_STREAMING_HISTORY = """
                        INSERT INTO StreamingHistory
                        SELECT row_number() over (ORDER BY end_time, 
                                   position) as position,
                               end_time,
                               artist_name,
                               track_name,
                               ms_played
                        FROM (
                            SELECT *
                            FROM StreamingHistoryRaw
                            ORDER BY history_id, position
                        )
                        GROUP BY end_time, artist_name, track_name, ms_played;
                        """
