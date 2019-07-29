from pathlib import Path
from logging import Logger

from yaml import load, Loader


class BaseParser(object):
    _defaults = {
        'src_dir': Path('./src'),
        'tmp_dir': Path('./__folianttmp__')
    }

    def __init__(self, project_path: Path, config_file_name: str, logger: Logger):
        self.project_path = project_path
        self.config_path = project_path / config_file_name
        self.logger = logger.getChild('cfg')

    def parse(self) -> dict:
        '''Parse the config file into a Python dict. Missing values are populated
        with defaults, paths are converted to ``pathlib.Paths``.

        :param project_path: Project path
        :param config_file_name: Config file name (almost certainly ``foliant.yml``)

        :returns: Dictionary representing the YAML tree
        '''

        self.logger.info('Parsing started.')

        with open(self.config_path, encoding='utf8') as config_file:
            config = {**self._defaults, **load(config_file, Loader)}

            config['src_dir'] = Path(config['src_dir']).expanduser()
            config['tmp_dir'] = Path(config['tmp_dir']).expanduser()

            self.logger.info(f'Parsing completed.')

            self.logger.debug(f'Config: {config}')

            if not config.get('escape_code', False):
                self.logger.warning(
                    'Working in backward compatibility mode. ' +
                    'To get rid of this warning, enable the escape_code config option'
                )

            return config
