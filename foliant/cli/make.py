'''Main CLI repsonsible for the ``make`` command.'''

from pathlib import Path
from importlib import import_module
from logging import DEBUG, WARNING
from typing import List, Dict, Tuple

from cliar import set_arg_map, set_metavars, set_help, ignore
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

from foliant.config import Parser
from foliant.utils import spinner, get_available_backends, tmp
from foliant.cli.base import BaseCli


class ConfigError(Exception):
    pass


class BackendError(Exception):
    pass


class BackendValidator(Validator):
    '''Validator for the interactive backend selection prompt.'''

    def __init__(self, available_backends: List[str]):
        super().__init__()
        self.available_backends = available_backends

    def validate(self, document):
        '''Check if the selected backend in installed.'''

        backend = document.text

        if backend not in self.available_backends:
            raise ValidationError(
                message=f'Backend {backend} not found. '
                + f'Available backends are: {", ".join(self.available_backends)}.',
                cursor_position=0
            )


class Cli(BaseCli):
    @staticmethod
    def validate_backend(backend: str, target: str) -> bool:
        '''Check that the specified backend exists and can build the specified target.'''

        available_backends = get_available_backends()

        if backend not in available_backends:
            raise BackendError(
                f'Backend {backend} not found. '
                + f'Available backends are {", ".join(available_backends.keys())}.'
            )

        if target not in available_backends[backend]:
            raise BackendError(f'Backend {backend} cannot make {target}.')

        return True

    @staticmethod
    def get_matching_backend(target: str, available_backends: Dict[str, Tuple[str]]) -> str:
        '''Get a matching backend for the specified target. If multiple backends match
        the specified target, prompt user.'''

        matching_backends = [
            backend
            for backend, targets in available_backends.items()
            if target in targets
        ]

        if not matching_backends:
            raise BackendError(f'No backend available for {target}.')

        if len(matching_backends) == 1:
            return matching_backends[0]

        try:
            return prompt(
                f'Please pick a backend from {matching_backends}: ',
                completer=WordCompleter(matching_backends),
                validator=BackendValidator(matching_backends)
            )
        except KeyboardInterrupt:
            raise BackendError('No backend specified')

    @ignore
    def get_config(
            self,
            project_path: Path,
            config_file_name: str,
            quiet=False,
            debug=False
    ) -> dict:
        with spinner('Parsing config', self.logger, quiet, debug):
            try:
                config = Parser(project_path, config_file_name, self.logger).parse()

            except FileNotFoundError as exception:
                config = None
                raise FileNotFoundError(f'{exception} not found')

            except Exception as exception:
                config = None
                raise type(exception)(f'Invalid config: {exception}')

        if config is None:
            raise ConfigError('Config parsing failed.')

        return config

    @set_arg_map({'backend': 'with', 'project_path': 'path', 'config_file_name': 'config'})
    @set_metavars({'target': 'TARGET', 'backend': 'BACKEND'})
    @set_help(
        {
            'target': 'Target format: pdf, docx, html, etc.',
            'backend': 'Backend to make the target with: Pandoc, MkDocs, etc.',
            'project_path': 'Path to the Foliant project.',
            'config_file_name': 'Name of config file of the Foliant project.',
            'quiet': 'Hide all output accept for the result. Useful for piping.',
            'keep_tmp': 'Keep the tmp directory after the build.',
            'debug': 'Log all events during build. If not set, only warnings and errors are logged.'
        }
    )
    def make(
            self,
            target,
            backend='',
            project_path=Path('.'),
            config_file_name='foliant.yml',
            quiet=False,
            keep_tmp=False,
            debug=False
        ):
        '''Make TARGET with BACKEND.'''

        # pylint: disable=too-many-arguments

        self.logger.setLevel(DEBUG if debug else WARNING)

        self.logger.info('Build started.')

        available_backends = get_available_backends()

        try:
            if backend:
                self.validate_backend(backend, target)
            else:
                backend = self.get_matching_backend(target, available_backends)

            config = self.get_config(project_path, config_file_name, quiet, debug)

        except (BackendError, ConfigError) as exception:
            self.logger.critical(str(exception))
            exit(str(exception))

        context = {
            'project_path': project_path,
            'config': config,
            'target': target,
            'backend': backend
        }

        backend_module = import_module(f'foliant.backends.{backend}')
        self.logger.debug(f'Imported backend {backend_module}.')

        with tmp(project_path/config['tmp_dir'], keep_tmp):
            result = backend_module.Backend(
                context,
                self.logger,
                quiet,
                debug
            ).preprocess_and_make(target)

        if result:
            self.logger.info(f'Result: {result}')

            if not quiet:
                print('─' * 20)
                print(f'Result: {result}')
            else:
                print(result)

        else:
            self.logger.critical('No result returned by backend')
            exit('No result returned by backend')
            return None

        return result
