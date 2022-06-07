from typing import List

from spotiviz.gui.database import loader
from spotiviz.gui.widgets.project_button import ProjectButton

# The maximum number of recent projects to list on the home screen
__MAX_RECENT_PROJECTS = 4


def get_all_project_buttons() -> List[ProjectButton]:
    projects = loader.get_recent_projects(__MAX_RECENT_PROJECTS)
    return [ProjectButton(name, projects[name][0]) for name in projects]
