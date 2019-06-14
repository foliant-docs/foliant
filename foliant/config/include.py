from pathlib import Path

from yaml import load, add_constructor, Loader

from foliant.config.base import BaseParser


class Parser(BaseParser):
    def _resolve_include_tag(self, _, node) -> str:
        '''Replace value after ``!include`` with the content of the referenced file.'''

        parts = node.value.split('#')

        if len(parts) == 1:
            path = Path(parts[0]).expanduser()

            with open(self.project_path/path) as include_file:
                return load(include_file, Loader)

        elif len(parts) == 2:
            path, section = Path(parts[0]).expanduser(), parts[1]

            with open(self.project_path/path) as include_file:
                return load(include_file, Loader)[section]

        else:
            raise ValueError('Invalid include syntax')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_constructor('!include', self._resolve_include_tag)
