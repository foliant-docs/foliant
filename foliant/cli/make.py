'''Main CLI repsonsible for the ``make`` command.'''

from pathlib import Path
from importlib import import_module
from logging import DEBUG, WARNING
from typing import List

from cliar import set_arg_map, set_metavars, set_help
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

from foliant.config import Parser
from foliant.utils import spinner, get_available_backends, tmp
from foliant.cli.base import BaseCli


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
    @set_arg_map({'backend': 'with', 'project_path': 'path', 'config_file_name': 'config'})
    @set_metavars({'target': 'TARGET', 'backend': 'BACKEND'})
    @set_help(
        {
            'target': 'Target format: pdf, docx, html, etc.',
            'backend': 'Backend to make the target with: Pandoc, MkDocs, etc.',
            'project_path': 'Path to the Foliant project',
            'config_file_name': 'Name of config file of the Foliant project',
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

        self.logger.setLevel(DEBUG if debug else WARNING)

        self.logger.info('Build started.')

        available_backends = get_available_backends()

        if backend:
            if backend not in available_backends:
                print(
                    f'Backend {backend} not found. '
                    + f'Available backends are {", ".join(available_backends.keys())}.'
                )
                exit(1)

            if target not in available_backends[backend]:
                print(f'Backend {backend} cannot make {target}.')
                exit(1)

        else:
            matching_backends = [
                backend
                for backend, targets in available_backends.items()
                if target in targets
            ]

            if not matching_backends:
                print(f'No backend available for {target}.')
                exit(1)

            elif len(matching_backends) == 1:
                backend = matching_backends[0]

            else:
                try:
                    backend = prompt(
                        f'Please pick a backend from {matching_backends}: ',
                        completer=WordCompleter(matching_backends),
                        validator=BackendValidator(matching_backends)
                    )

                except KeyboardInterrupt:
                    return

        with spinner('Parsing config', self.logger, quiet):
            try:
                config = Parser(project_path, self.logger, config_file_name).parse()

            except FileNotFoundError as exception:
                config = None
                raise FileNotFoundError(f'{exception} not found')

            except Exception as exception:
                config = None
                raise type(exception)(f'Invalid config: {exception}')

        if config is None:
            self.logger.critical('Config parsing failed.')
            exit(1)

        context = {
            'target': target,
            'backend': backend
        }

        backend_module = import_module(f'foliant.backends.{backend}')

        self.logger.debug(f'Imported backend {backend_module}.')

        with tmp(project_path/config['tmp_dir'], keep_tmp):
            result = backend_module.Backend(
                project_path,
                self.logger,
                config,
                context,
                quiet
            ).preprocess_and_make(target)

        if result:
            self.logger.info(f'Result: {result}')

            if not quiet:
                print('─────────────────────')
                print(f'Result: {result}')
            else:
                print(result)

            return result

        else:
            self.logger.critical('No result returned by backend.')
            exit(1)
