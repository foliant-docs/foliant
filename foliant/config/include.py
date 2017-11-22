from pathlib import Path

from yaml import load, add_constructor

from foliant.config.base import BaseParser


class Parser(BaseParser):
    def _resolve_include_tag(self, _, node) -> str:
        '''Replace value after ``!include`` with the content of the referenced file.'''

        path = Path(node.value).expanduser()
        with open(self.project_path/path) as include_file:
            return load(include_file)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_constructor('!include', self._resolve_include_tag)
