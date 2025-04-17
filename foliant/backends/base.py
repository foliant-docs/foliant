import re
import os
import frontmatter
from importlib import import_module
from shutil import copytree, copy
from pathlib import Path
from datetime import date
from logging import Logger
from glob import glob
from typing import Union, List, Set
from foliant.utils import spinner

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
        preprocessor_name = None
        preprocessor_options = {}

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
        project_path: Union[str, Path],
        root: Union[str, Path],
        destination: Union[str, Path],
    ) -> None:
        """
        Copies files, a list of files,
        or files matching a glob pattern to the specified folder.
        Creates all necessary directories if they don't exist.
        """
        destination_path = Path(destination)
        root_path = Path(root)
        image_extensions = {'.jpg', '.jpeg', '.png', '.svg', '.gif', '.bmp', '.webp'}
        image_pattern = re.compile(r'!\[.*?\]\((.*?)\)|<img.*?src=["\'](.*?)["\']', re.IGNORECASE)
        include_statement_pattern = re.compile(
            r'(?<!\<)\<(?:include)(?:\s[^\<\>]*)?\>(?P<path>.*?)\<\/(?:include)\>',
            flags=re.DOTALL
        )

        def _extract_first_header(file_path):
            """Extracts the first first-level header from the Markdown file."""
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    match = re.match(r'^#\s+(.*)', line)
                    if match:
                        return match.group(0)
            return None

        def _modify_markdown_file(
            file_path: Union[str, Path],
            dst_file_path: Union[str, Path],
            not_build: bool = True,
            remove_content: bool = True,
            keep_first_header: bool = True,
            create_frontmatter: bool = True,
            dry_run: bool = False,
        ):
            """
            Modify a Markdown file's frontmatter and content according to specified parameters.
            Uses python-frontmatter package for reliable frontmatter handling.

            Args:
                file_path: Path to the Markdown file
                not_build: Value for not_build field (None means don't modify)
                remove_content: Whether to remove the content body
                keep_first_header: Keep first H1 when removing content
                create_frontmatter: Create frontmatter if missing
                dry_run: Preview changes without writing

            Returns:
                Tuple of (modified: bool, new_content: str)

            Examples:
                # Basic usage - add not_build: true
                modified, content = modify_markdown_file("post.md")

                # Remove content but keep first header
                modify_markdown_file("post.md", remove_content=True, keep_first_header=True)

                # Dry run to preview changes
                modified, new_content = modify_markdown_file("post.md", dry_run=True)
            """
            try:
                file_path = Path(file_path)
                content = file_path.read_text(encoding='utf-8')

                # Parse document with python-frontmatter
                post = frontmatter.loads(content)
                original_content = post.content
                changes_made = False

                # Modify frontmatter if requested
                if not_build is not None:
                    if post.get('not_build') != not_build:
                        post['not_build'] = not_build
                        changes_made = True

                # Handle content modifications
                if remove_content and original_content.strip():
                    new_content = ''
                    if keep_first_header:
                        # Find first H1 header using regex
                        h1_match = re.search(r'^#\s+.+$', original_content, flags=re.MULTILINE)
                        if h1_match:
                            new_content = h1_match.group(0) + '\n'

                    if post.content != new_content:
                        post.content = new_content
                        changes_made = True

                # Create frontmatter if missing and requested
                if not has_frontmatter(post) and create_frontmatter and (not_build is not None or changes_made):
                    changes_made = True  # Adding frontmatter counts as a change

                # Return original if no changes
                if not changes_made:
                    return (False, content)

                # Serialize back to text
                output = frontmatter.dumps(post)
                if not has_frontmatter(post) and create_frontmatter:
                    output = f"---\n{output}"  # Ensure proper YAML fences

                # Dry run check
                if dry_run:
                    return (True, output)

                # Write changes
                dst_file_path.write_text(output, encoding='utf-8')
                return (True, output)

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                return (False, content)

        def has_frontmatter(post: frontmatter.Post) -> bool:
            """Check if post has existing frontmatter using python-frontmatter internals"""
            return hasattr(post, 'metadata') and (post.metadata or hasattr(post, 'fm'))

        def _find_referenced_images(file_path: Path) -> Set[Path]:
            """Finds all image files referenced in the given file."""
            image_paths = set()
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                for match in image_pattern.findall(content):
                    for group in match:
                        if group:
                            image_path = Path(file_path).parent / Path(group)
                            if image_path.suffix.lower() in image_extensions:
                                image_paths.add(image_path)
            return image_paths

        def _copy_files_without_content(src_dir: str, dst_dir: str):
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
                        _modify_markdown_file(src_file_path, dst_file_path)
                    # else:
                    #     if Path(src_file_path).suffix.lower() not in image_extensions:
                    #         copy(src_file_path, dst_file_path)

        def _copy_files_recursive(files_to_copy: List):
            """Recursively copies files and their dependencies."""
            referenced_images = set()

            for file_path in files_to_copy:
                if file_path.is_relative_to(root_path):
                    relative_path = file_path.relative_to(root_path)
                    destination_file_path = destination_path / relative_path
                    destination_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Find and copy includes
                    include_paths = []
                    match_includes = re.findall(include_statement_pattern,
                                                file_path.read_text(encoding='utf-8'))
                    for path in match_includes:
                        _path = Path(path)
                        if not _path.exists():
                            _path = relative_path / path
                        if _path.exists():
                            include_paths.append(_path)
                        _copy_files_recursive(include_paths)

                    # Find referenced images
                    referenced_images.update(_find_referenced_images(file_path))

                    # Copy the file
                    copy(file_path, destination_file_path)

            # Copy referenced images
            for image_path in referenced_images:
                src_image_path = Path(image_path).relative_to(root_path)
                dst_image_path = destination_path / src_image_path
                dst_image_path.parent.mkdir(parents=True, exist_ok=True)

                if Path(image_path).exists():
                    copy(image_path, dst_image_path)

        # Basic logic
        _copy_files_without_content(root_path, destination_path)
        if isinstance(source, str) and ',' in source:
            source = source.split(',')
        if isinstance(source, list):
            files_to_copy = []
            for item in source:
                item_path = Path(project_path, item)
                if item_path.exists():
                    files_to_copy.append(item_path)
        else:
            if isinstance(source, str):
                source_path = Path(source)
            else:
                source_path = source

            if isinstance(source, str) and ('*' in source or '?' in source or '[' in source):
                files_to_copy = [Path(file) for file in glob(source, recursive=True)]
            else:
                if source_path.exists():
                    files_to_copy = [source_path]
        _copy_files_recursive(files_to_copy)

    def preprocess_and_make(self, target: str) -> str:
        '''Apply preprocessors required by the selected backend and defined in the config file,
        then run the ``make`` method.

        :param target: Output format: pdf, docx, html, etc.

        :returns: Result as returned by the ``make`` method
        '''

        src_path = self.project_path / self.config['src_dir']
        # multiprojectcache_dir = os.path.join(self.project_path, '.multiprojectcache')

        if self.context['only_partial']:
            # if os.path.isdir(multiprojectcache_dir) and target == "pre":
            self.partial_copy(self.context['only_partial'],  self.project_path, src_path, self.working_dir)
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
