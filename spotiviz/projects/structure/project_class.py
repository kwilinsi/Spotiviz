from __future__ import annotations

from datetime import date

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from spotiviz.database import db, setup
from spotiviz.database.structure.program_struct import Projects

from spotiviz.projects.structure import spotify_download as sd


class Project:
    """
    This class holds all pieces of a project while it is being processed and
    sent to a SQLite database. It contains SpotifyDownload instances,
    which holds the StreamingHistory files that are primarily processed.
    """

    def __init__(self, name: str, path: str):
        """
        Create a new Project instance by providing its name and the path to
        its SQLite database file.

        Args:
            name: The name of the project.
            path: The path to the project's SQLite database file.
        """

        self.name = name
        self.path = path

    def __str__(self) -> str:
        """
        Get the string representation of this project (its name in single
        quotes).

        Returns:
            A string for this project.
        """

        return f'\'{self.name}\''

    def to_sql_object(self) -> Projects:
        """
        Create an instance of the Projects class for use with SQLAlchemy.

        Returns:
            The SQL representation of this project.
        """

        # noinspection PyArgumentList
        return Projects(name=self.name,
                        database_path=self.path)

    def save_to_database(self) -> None:
        """
        Add this project to the global, program-level database.

        If it is already in the projects table, nothing happens and no data
        is overwritten.

        Note that the project name doesn't need to be cleaned with
        clean_project_name(). Cleaning is only used while referencing the
        database file, not storing the project name in the SQL database or
        displaying it to the user.

        Returns:
            None
        """

        with db.session() as session:
            session.add(self.to_sql_object())
            session.commit()

    def update_database(self) -> None:
        """
        Update the path for this project in the global, program-level
        database. This is useful if the project isn't being created from
        scratch, but its database path changed.

        Returns:
            None
        """

        with db.session() as session:
            try:
                # Get the previously saved SQL instance for this project
                p = session.scalars(
                    select(Projects).where(Projects.name == self.name)).one()

                # Update its path
                p.database_path = self.path

                # Save changes
                session.commit()
            except:
                raise NameError(f'Project {self} not in SQL database. '
                                f'Path cannot be updated.')

    def open_session(self) -> Session:
        """
        Open a SQLAlchemy session connected to the project's SQLite database
        file. The database must first have been initialized.

        Returns:
            The new Session.
        """

        return db.session(self.name)

    def create_database(self) -> None:
        """
        Create a SQLite database file at this project's path. This is done by
        initializing a SQLAlchemy engine associated with that file.
        Additionally, set up the initial SQL environment within that database
        according to the standard project structure.

        Returns:
            None
        """

        setup.setup_project_db(
            db.initialize_project_engine(self.name, self.path)
        )

    def add_download(self,
                     path: str,
                     name: str = None,
                     download_date: date = None) -> None:
        """
        Create a new Download instance pointing to a Spotify download,
        and assign it to this project. Save its contents to the project
        database.

        Args:
            path: The path to the directory with the Spotify download.
            name: [Optional] The name to give the download (or omit to default
                  to the name of the bottom-level directory in the path).
            download_date: [Optional] The date that the download was requested
                           from Spotify.

        Returns:
            None
        """

        d = sd.SpotifyDownload(self, path, name, download_date)
        d.save_to_database()
