from typing import List

from spotiviz.gui.database import loader
from spotiviz.gui.widgets.project_button import ProjectBtn

# The maximum number of recent projects to list on the home screen
__MAX_RECENT_PROJECTS = 4


# TODO migrate __MAX_RECENT_PROJECTS to standard installation config


def get_all_project_buttons(click_fcn) -> List[ProjectBtn]:
    """
    Get a list of buttons for all the recent projects.

    Args:
        click_fcn: The function that the buttons should call when clicked.

    Returns:
        A list of project buttons.
    """

    projects = loader.get_recent_projects(__MAX_RECENT_PROJECTS)
    return [ProjectBtn(name, projects[name][0], click_fcn)
            for name in projects]
