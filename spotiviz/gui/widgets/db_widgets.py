from typing import List

from spotiviz.projects import manager
from spotiviz.gui.widgets.project_button import ProjectButton


def get_all_project_buttons() -> List[ProjectButton]:
    projects = manager.get_all_projects()
    return [ProjectButton(name, projects[name][0]) for name in projects]
