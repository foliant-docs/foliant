import re
from pickle import load

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors._stash import Preprocessor as StashPreprocessor


class Preprocessor(BasePreprocessor):
    defaults = StashPreprocessor.defaults
    tags = 'stash',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(self.project_path/self.options['stash_file'], 'rb') as stash_file:
            self._stash = load(stash_file, encoding='utf8')

    def process_stashes(self, content: str) -> str:
        def _sub(stash_block):
            return self._stash[stash_block.group('body')]

        return self.pattern.sub(_sub, content)

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.process_stashes(content))

        (self.project_path / self.options['stash_file']).unlink()
