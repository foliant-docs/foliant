from time import time
from logging import getLogger, FileHandler, Formatter

from cliar import set_help

from foliant import __version__ as foliant_version
from foliant.utils import get_available_clis


class Foliant(*get_available_clis().values()):
    '''Foliant is an all-in-one modular documentation authoring tool.'''

    @set_help({'version': 'show version and exit'})
    def _root(self, version=False):
        # pylint: disable=no-self-use

        if version:
            print(f'Foliant v.{foliant_version}')

        else:
            self._parser.print_help()


def entry_point():
    Foliant().parse()
