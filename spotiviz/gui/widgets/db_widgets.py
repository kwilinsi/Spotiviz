from typing import List

from spotiviz.gui.database import loader
from spotiviz.gui.widgets.project_button import ProjectBtn

# The maximum number of recent projects to list on the home screen
__MAX_RECENT_PROJECTS = 4


def get_all_project_buttons() -> List[ProjectBtn]:
    projects = loader.get_recent_projects(__MAX_RECENT_PROJECTS)
    return [ProjectBtn(name, projects[name][0]) for name in projects]
