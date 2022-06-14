import os.path
from enum import Enum

from spotiviz import get_resources


class Icons(Enum):
    """
    Each enum here represents an icon image in the resources directory.
    Complete paths to the icons can be obtained with .path().
    """

    INFO = 'info.png'

    def path(self) -> str:
        """
        Get the complete path to this icon file.

        Returns:
            The absolute path.
        """

        return get_resources(os.path.join('gui', 'icons', self.value))
