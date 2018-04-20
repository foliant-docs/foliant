from time import time
from logging import getLogger, FileHandler, Formatter

from cliar import Cliar


class BaseCli(Cliar):
    '''Base CLI. All CLI extensions must inherit from this one.'''

    def __init__(self):
        super().__init__()
        self.logger = getLogger('flt')
        handler = FileHandler(f'{int(time())}.log', delay=True)
        handler.setFormatter(Formatter('%(asctime)s | %(name)20s | %(levelname)8s | %(message)s'))
        self.logger.addHandler(handler)
