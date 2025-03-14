import re
import os
from importlib import import_module
from shutil import copytree, copy
from pathlib import Path
from datetime import date
from logging import Logger
from glob import glob
from foliant.utils import spinner
from typing import Union, List

class BaseBackend():
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

            except ModuleNotFoundError as module_not_found:
                raise ModuleNotFoundError(
                    f'Preprocessor {preprocessor_name} is not installed'
                ) from module_not_found

            except Exception as exception:
                raise RuntimeError(
                    f'Failed to apply preprocessor {preprocessor_name}: {exception}'
                ) from exception

    @staticmethod
    def partial_copy(
        source: Union[str, Path, List[Union[str, Path]]],
        destination: Union[str, Path],
        root: Union[str, Path]
    ) -> None:
        """
        Copies files, a list of files, or files matching a glob pattern to the specified folder.
        Creates all necessary directories if they don't exist.

        :param source: A file path, a list of file paths, or a glob pattern (as a string or Path object).
        :param destination: Target folder (as a string or Path object).
        :param root: Base folder to calculate relative paths (optional). If not provided, the parent directory of the source is used.
        """
        # Convert destination to a Path object
        destination_path = Path(destination)

        def extract_first_header(file_path):
            """Extracts the first first-level header from the Markdown file."""
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    match = re.match(r'^#\s+(.*)', line)
                    if match:
                        return match.group(0)  # Returns the header
            return None  # If the header is not found

        def copy_files_without_content(src_dir, dst_dir):
            """Copies files, leaving only the first-level header."""
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            for file_root, _, files in os.walk(src_dir):
                for file_name in files:
                    src_file_path = os.path.join(file_root, file_name)
                    dirs = os.path.relpath(file_root, src_dir)
                    dst_file_path = Path(os.path.join(dst_dir, dirs, file_name))
                    dst_file_path.parent.mkdir(parents=True, exist_ok=True)
                    if file_name.endswith('.md'):
                        header = extract_first_header(src_file_path)
                        if header:
                            with open(dst_file_path, 'w', encoding='utf-8') as dst_file:
                                dst_file.write(header + '\n')
                    else:
                        copy(src_file_path, dst_file_path)

        copy_files_without_content(root, destination)
        # Handle case where source is a list of files
        if isinstance(source, str) and ',' in source:
            print( source)
            source = source.split(',')
        if isinstance(source, list):
            files_to_copy = []
            for item in source:
                item_path = Path(item)
                if not item_path.exists():
                    raise FileNotFoundError(f"Source '{item}' not found.")
                files_to_copy.append(item_path)
        else:
            # Convert source to a Path object if it's a string
            if isinstance(source, str):
                source_path = Path(source)
            else:
                source_path = source

            # Check if the source is a glob pattern
            if isinstance(source, str) and ('*' in source or '?' in source or '[' in source):
                # Use glob to find files matching the pattern
                files_to_copy = [Path(file) for file in glob(source, recursive=True)]
            else:
                # Check if the source file or directory exists
                if not source_path.exists():
                    raise FileNotFoundError(f"Source '{source_path}' not found.")
                files_to_copy = [source_path]

        # Determine the root directory for calculating relative paths
        root = Path(root)

        # Copy each file
        for file_path in files_to_copy:
            # Calculate the relative path
            relative_path = file_path.relative_to(root)

            # Full path to the destination file
            destination_file_path = destination_path / relative_path

            # Create directories if they don't exist
            destination_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            copy(file_path, destination_file_path)

    def preprocess_and_make(self, target: str) -> str:
        '''Apply preprocessors required by the selected backend and defined in the config file,
        then run the ``make`` method.

        :param target: Output format: pdf, docx, html, etc.

        :returns: Result as returned by the ``make`` method
        '''

        src_path = self.project_path / self.config['src_dir']

        if self.context['only_partial']:
            self.partial_copy(self.context['only_partial'], self.working_dir, src_path)
        else:
            copytree(src_path, self.working_dir)

        common_preprocessors = (
            *self.required_preprocessors_before,
            *self.config.get('preprocessors', ()),
            *self.required_preprocessors_after
        )

        if self.config.get('escape_code', False):
            if isinstance(self.config['escape_code'], dict):
                escapecode_preprocessor = {
                    'escapecode': self.config['escape_code'].get('options', {})
                }

            else:
                escapecode_preprocessor = 'escapecode'

            preprocessors = (
                escapecode_preprocessor,
                *common_preprocessors,
                'unescapecode'
            )

        elif self.config.get('disable_implicit_unescape', False):
            preprocessors = common_preprocessors

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
