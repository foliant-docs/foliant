from pathlib import Path

from yaml import add_constructor

from foliant.config.base import BaseParser

class Parser(BaseParser):
    def _resolve_path_tag(self, _, node) -> str:
        '''Convert value after ``!path`` to an existing, absolute Posix path.

        Relative paths are relative to the project path.
        '''

        path = Path(node.value).expanduser()
        return (self.project_path/path).resolve(strict=True).as_posix()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_constructor('!path', self._resolve_path_tag)
