from pathlib import Path

from yaml import add_constructor

from foliant.config.base import BaseParser


class Parser(BaseParser):
    def _resolve_path_tag(self, _, node) -> str:
        '''Convert value after ``!path`` to an existing, absolute Posix path.

        Relative paths are relative to the project path.
        '''

        path = Path(node.value).expanduser()
        return (self.project_path / path).resolve(strict=True).as_posix()

    def _resolve_project_path_tag(self, _, node) -> str:
        '''Convert value after ``!project_path`` to Path object relative to the
        project path.

        Return absolute path to this file without checks for existance.
        '''

        return (self.project_path / node.value).resolve()

    @staticmethod
    def _resolve_rel_path_tag(_, node) -> str:
        '''Convert value after ``!rel_path`` to Path object.'''

        return Path(node.value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_constructor('!path', self._resolve_path_tag)
        add_constructor('!project_path', self._resolve_project_path_tag)
        add_constructor('!rel_path', self._resolve_rel_path_tag)
