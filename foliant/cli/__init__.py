from time import time
from logging import getLogger, FileHandler, Formatter

from foliant import __version__ as foliant_version
from foliant.utils import get_available_clis

from cliar import set_help


class Foliant(*get_available_clis().values()):
    '''Foliant is an all-in-one modular documentation authoring tool.'''

    def __init__(self):
        super().__init__()
        self.logger = getLogger('flt')
        handler = FileHandler(f'{int(time())}.log', delay=True)
        handler.setFormatter(Formatter('%(asctime)s | %(name)20s | %(levelname)8s | %(message)s'))
        self.logger.addHandler(handler)

    @set_help({'version': 'show version and exit'})
    def _root(self, version=False):
        if version:
            exit(f'Foliant v.{foliant_version}')


def entry_point():
    Foliant().parse()
