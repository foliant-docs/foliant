from importlib import import_module
from shutil import copytree
from datetime import date
from logging import Logger

from foliant.utils import spinner


class BaseBackend(object):
    '''Base backend. All backends must inherit from this one.'''

    targets = ()
    required_preprocessors_before = ()
    required_preprocessors_after = ()

    def __init__(self, context: dict, logger: Logger, quiet=False, debug=False):
        self.project_path = context['project_path']
        self.config = context['config']
        self.context = context
        self.logger = logger
        self.quiet = quiet
        self.debug = debug

        self.working_dir = self.project_path / self.config['tmp_dir']

    def get_slug(self) -> str:
        '''Generate a slug from the project title and version and the current date.

        Spaces in title are replaced with underscores, then the version and the current date
        are appended.
        '''

        if 'slug' in self.config:
            return self.config['slug']

        components = []

        components.append(self.config['title'].replace(' ', '_'))

        version = self.config.get('version')
        if version:
            components.append(str(version))

        components.append(str(date.today()))

        return '-'.join(components)

    def apply_preprocessor(self, preprocessor: str or dict):
        '''Apply preprocessor.

        :param preprocessor: Preprocessor name or a dict of the preprocessor name and its options
        '''

        if isinstance(preprocessor, str):
            preprocessor_name, preprocessor_options = preprocessor, {}
        elif isinstance(preprocessor, dict):
            (preprocessor_name, preprocessor_options), = (*preprocessor.items(),)

        with spinner(
            f'Applying preprocessor {preprocessor_name}',
            self.logger,
            self.quiet,
            self.debug
        ):
            try:
                preprocessor_module = import_module(f'foliant.preprocessors.{preprocessor_name}')
                preprocessor_module.Preprocessor(
                    self.context,
                    self.logger,
                    self.quiet,
                    self.debug,
                    preprocessor_options
                ).apply()

            except ModuleNotFoundError:
                raise ModuleNotFoundError(f'Preprocessor {preprocessor_name} is not installed')

            except Exception as exception:
                raise type(exception)(
                    f'Failed to apply preprocessor {preprocessor_name}: {exception}'
                )

    def preprocess_and_make(self, target: str) -> str:
        '''Apply preprocessors required by the selected backend and defined in the config file,
        then run the ``make`` method.

        :param target: Output format: pdf, docx, html, etc.

        :returns: Result as returned by the ``make`` method
        '''

        src_path = self.project_path / self.config['src_dir']

        copytree(src_path, self.working_dir)

        common_preprocessors = (
            *self.required_preprocessors_before,
            *self.config.get('preprocessors', ()),
            *self.required_preprocessors_after
        )

        if self.config.get('escape_code', False):
            preprocessors = (
                'escapecode',
                *common_preprocessors,
                'unescapecode'
            )

        else:
            preprocessors = (
                *common_preprocessors,
                '_unescape'
            )

        for preprocessor in preprocessors:
            self.apply_preprocessor(preprocessor)

        return self.make(target)

    def make(self, target: str) -> str:
        '''Make the output from the source. Must be implemented by every backend.

        :param target: Output format: pdf, docx, html, etc.

        :returns: Typically, the path to the output file, but in general any string
        '''

        raise NotImplementedError
