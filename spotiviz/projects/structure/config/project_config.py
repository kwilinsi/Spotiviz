from __future__ import annotations

from typing import Any, Dict

from sqlalchemy import select

from spotiviz.utils.log import LOG

from spotiviz.database.structure.project_struct import Config as ConfigTbl
from spotiviz.projects.structure.config.properties import (
    Config, config_from_name
)
from spotiviz.projects.structure import project_class as pc


class ProjectConfig:
    """
    Each project can have its own configuration. This class stores all the
    settings for a certain project.

    This is a mirror of the Config table in a project database. That table
    should only be modified and accessed through this class.
    """

    def __init__(self, project: pc.Project):
        """
        Create a new ProjectConfig instance attached to a Project.

        Args:
            project: The project to which this configuration belongs.
        """

        self.project = project

        # Initialize the properties dictionary
        self.properties: Dict[Config, Any] = dict()

    def read_from_db(self) -> None:
        """
        Set the config properties by loading them from the project's
        database. If any property is not found in the project's database,
        reference the global, program-level database to see if it's set there.

        Note that this presumes that the project's SQLAlchemy engine has
        been opened, and it is therefore safe to open a session.

        Returns:
            None
        """

        LOG.debug(f'Loading configuration for project {self.project} '
                  f'from database')

        with self.project.open_session() as session:
            stmt = select(ConfigTbl)
            result = session.execute(stmt)

            for row in result:
                c = config_from_name(row[0].key)
                self.properties[c] = c.cast(row[0].value)

    def get(self, config: Config) -> Any:
        """
        Get the state of some configuration element as it appears in the
        cached properties dictionary. To force reloading it from the SQLite
        database for the project, use get_force_reload()

        Args:
            config: The setting to retrieve.

        Returns:
            The value of that setting.
        """

        return self.properties[config]

    def get_force_reload(self, config: Config) -> Any:
        """
        Get the state of some configuration element. It will be retrieved
        from the SQLite database for the project, even if it's cached in the
        properties dictionary. If the cached value is out of dated, it will
        be updated.

        Note that this presumes that the project's SQLAlchemy engine has
        been opened, and it is therefore safe to open a session.

        Args:
            config: The setting to retrieve.

        Returns:
            The current value of that setting in the project's SQLite
            database file.

        Raises:
            ValueError: If the provided config element was not found in the
                        database.
        """

        with self.project.open_session() as session:
            stmt = select(ConfigTbl.value).where(ConfigTbl.value == config.name)
            result = session.scalars(stmt)

            try:
                val = result.first()
                self.properties[config] = config.cast(val)
                return val
            except Exception:
                raise ValueError(f'Failed to find config \"{config.name}\"')
