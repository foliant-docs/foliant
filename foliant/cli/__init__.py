from foliant import __version__ as foliant_version
from foliant.utils import get_available_clis

from cliar import set_help


class Foliant(*get_available_clis().values()):
    '''Foliant is an all-in-one modular documentation authoring tool.'''

    @set_help({'version': 'show version and exit'})
    def _root(self, version=False):
        if version:
            exit(f'Foliant v.{foliant_version}')


def entry_point():
    Foliant().parse()
