import os.path

PREPROCESSING_DIR = 'preprocessing'

PROJECT_SETUP_SCRIPT = 'project_setup.sql'

LOAD_ARTISTS_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                   'load_artists.sql')

LOAD_TRACKS_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                  'load_tracks.sql')

CLEAN_STREAMING_HISTORY_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                              'clean_streaming_history.sql')

LOAD_TRACK_LENGTHS_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                         'load_track_lengths.sql')

CORRECT_DATE_ANOMALIES_SCRIPT = os.path.join(PREPROCESSING_DIR,
                                             'correct_date_anomalies.sql')
