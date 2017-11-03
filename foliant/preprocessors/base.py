from pathlib import Path
from time import sleep


class BasePreprocessor(object):
    '''Base preprocessor. All preprocessors must inherit from this one.'''

    defaults = {}

    def __init__(self, project_path: Path, config: dict, options={}):
        self.project_path = project_path
        self.config = config
        self.options = {**self.defaults, **options}

        self.working_dir = project_path / config['tmp_dir']

    def apply(self):
        '''Run the preprocessor against the project directory. Must be implemented
        by every preprocessor.
        '''

        raise NotImplementedError
