from __future__ import annotations

from datetime import date, datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from spotiviz.database import db, setup
from spotiviz.database.structure.program_struct import Projects

from spotiviz.projects.structure import spotify_download as sd
from spotiviz.projects.structure.config.project_config import ProjectConfig
from spotiviz.projects.structure.config.properties import Config


class Project:
    """
    This class holds all pieces of a project while it is being processed and
    sent to a SQLite database. It contains SpotifyDownload instances,
    which holds the StreamingHistory files that are primarily processed.
    """

    def __init__(self, name: str, path: str, created_at: datetime = None):
        """
        Create a new Project instance by providing its name and the path to
        its SQLite database file.

        Args:
            name: The name of the project.
            path: The path to the project's SQLite database file.
            created_at: [Optional] the time this project was created.
                        Typically, this is generated by the SQL database and is
                        only set here later.
        """

        self.name = name
        self.path = path
        self.created_at = created_at
        # This stores all the configuration properties for the project
        self.config = ProjectConfig(self)

    @classmethod
    def from_sql(cls, projects_record: Projects):
        """
        Generate a Project instance from an instance of the SQLAlchemy-based
        Projects class, which represents a record in the Projects table in
        the global program database.

        In other words, where this class typically goes from new instance ->
        SQL Projects instance -> Projects table in the database, this method
        allows the process to go in reverse. An already-existing project in
        the Projects table can be converted back to a Project instance. This
        is useful for accessing methods like open_session() while calculating
        statistics.

        Args:
            projects_record: A record in the SQL database from the Projects
                             table, given as an instance of the Projects class.

        Returns:
            A new Project instance for the project.
        """

        return cls(projects_record.name,
                   projects_record.database_path,
                   projects_record.created_at)

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
                        database_path=self.path,
                        created_at=self.created_at)

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

    def initialize_engine(self) -> sa.engine.Engine:
        """
        Initialize the SQLAlchemy engine for this project's SQLite database
        file. This is necessary for using self.open_session() later.

        Note that this does not install the database. For that,
        use self.create_database().

        Returns:
            The engine instance.
        """

        return db.initialize_project_engine(self.name, self.path)

    def open_session(self) -> Session:
        """
        Open a SQLAlchemy session connected to the project's SQLite database
        file. The database must first have been initialized.

        Returns:
            The new Session.
        """

        return db.session(project=self.name)

    def create_database(self) -> None:
        """
        Create a SQLite database file at this project's path. This is done by
        initializing a SQLAlchemy engine associated with that file.
        Additionally, set up the initial SQL environment within that database
        according to the standard project structure.

        Returns:
            None
        """

        setup.setup_project_db(self.initialize_engine())

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

    def get_config(self, config: Config) -> Any:
        """
        Get the value of some config property. This is semantically
        equivalent to calling project.config.get(<config>).

        For a shorter alias, use alias project.c(<config>).

        To use the current value in the SQLite database, rather than relying
        on the cache, use project.get_config_force_reload(<config>).

        Args:
            config: The desired Config property.

        Returns:
            The current cached value of that property.
        """

        return self.config.get(config)

    # Define the alias .c() for .get_config()
    c = get_config

    def get_config_force_reload(self, config: Config) -> Any:
        """
        Similar to self.get_config() and self.c() (its alias), except that
        the value is always loaded directly from the SQLite database for the
        project, rather than using the current cached value. Calling this
        method also updates the cache for the requested property.

        This is semantically equivalent to calling
        project.config.get_force_reload(<config>).

        Args:
            config: The desired Config property.

        Returns:
            The current value of that property in the SQLite database.
        """

        return self.config.get_force_reload(config)
