from os import getenv
from yaml import load, add_constructor, Loader

from foliant.config.base import BaseParser


class Parser(BaseParser):
    @staticmethod
    def _resolve_env_tag(_, node) -> str or int or bool or dict or list or None:
        '''Replace value after ``!env`` with the value of referenced environment variable.'''

        return load(getenv(node.value, default='null'), Loader)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_constructor('!env', self._resolve_env_tag)
