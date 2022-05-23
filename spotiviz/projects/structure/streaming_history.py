from __future__ import annotations

import json
from typing import Optional
from datetime import datetime

from spotiviz.projects import utils as ut
from spotiviz.projects.structure import (
    project_class as pc, spotify_download as sd, generic_file as gf
)

from spotiviz.database.structure.project_struct import (
    StreamingHistories, StreamingHistoryRaw
)


class StreamingHistory(gf.GenericFile):
    """
    This class represents a single `StreamingHistoryX.json` file for a
    Spotify download. It stores the SpotifyDownload instance to which it is
    attached, along with the relative path to the streaming history file.
    """

    def __init__(self,
                 project: pc.Project,
                 download: sd.SpotifyDownload,
                 file_name: str):
        """
        Initialize a StreamingHistory instance.

        Args:
            project: See GenericFile.__init__().
            download: See GenericFile.__init__().
            file_name: See GenericFile.__init__().
        """

        super().__init__(project, download, file_name)

        # Initialize the id and start_time to temporary values so that they can
        # be computed and assigned later
        self.id: int = -1
        self.start_time: Optional[datetime] = None

    def to_sql_object(self) -> StreamingHistories:
        """
        Create a SQLAlchemy object of this StreamingHistory based on the
        StreamingHistories class from
        spotiviz.database.structure.project_struct.py.

        Returns:
            The SQL object with the appropriate parameters.
        """

        # noinspection PyArgumentList
        return StreamingHistories(download_id=self.download.id,
                                  file_name=self.file_name,
                                  start_time=self.start_time)

    def save_to_database(self) -> None:
        """
        This opens the streaming history file, parses the JSON, and sends it
        to the SQLite database for this project.

        Returns:
            None
        """

        # TODO add try-except clauses here to handle malformed JSON

        # Open the streaming history file and parse the json
        file = open(self.download.get_full_path(self.file_name),
                    encoding='utf-8')
        j = json.load(file)
        file.close()

        # Set the start time (the timestamp of the first listen). Note that
        # this assumes the streaming history file is sorted chronologically
        self.start_time = ut.to_datetime(j[0]['endTime'])

        # Open a connection to the database
        with self.project.open_session() as session:
            h = self.to_sql_object()
            session.add(h)
            session.flush()
            self.id = h.id

            # Create StreamingHistoryRaw objects for each record in the
            # streaming history file.

            # noinspection PyArgumentList
            records = [StreamingHistoryRaw(history_id=self.id,
                                           position=position,
                                           end_time=ut.to_datetime(
                                               listen['endTime']),
                                           artist_name=listen['artistName'],
                                           track_name=listen['trackName'],
                                           ms_played=listen['msPlayed'])
                       for position, listen in enumerate(j)]

            # Add the records to the database and save changes
            session.add_all(records)

            # Commit changes to project database
            session.commit()
