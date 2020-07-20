from pathlib import Path
from time import time
from logging import getLogger, FileHandler, Formatter

from cliar import Cliar


class BaseCli(Cliar):
    '''Base CLI. All CLI extensions must inherit from this one.'''

    def __init__(self, logs_dir=None):
        super().__init__()
        self.logger = getLogger('flt')

        for old_handler in self.logger.handlers:
            if isinstance(old_handler, FileHandler):
                self.logger.removeHandler(old_handler)

        filename = f'{int(time())}.log'

        if logs_dir:
            logs_dir_path = Path(logs_dir).resolve()
            logs_dir_path.mkdir(parents=True, exist_ok=True)
            filename = f'{logs_dir_path / filename}'

        handler = FileHandler(filename, delay=True)
        handler.setFormatter(Formatter('%(asctime)s | %(name)20s | %(levelname)8s | %(message)s'))
        self.logger.addHandler(handler)
