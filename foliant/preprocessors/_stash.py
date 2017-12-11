from pathlib import Path
from uuid import uuid1
from pickle import dump

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'stash_file': Path('.stash')
    }
    tags = 'raw',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._stash_path = self.project_path / self.options['stash_file']

    def process_raw_blocks(self, content: str) -> str:
        '''Cut raw blocks from the sources and stash them in a file.
        Each block is stashed with a unique ID, so that it could be unstashed.

        :param content: Markdown content

        :returns: Markdown content with unique stash IDs instead of raw blocks
        '''

        stash = {}

        def _sub(raw_block):
            body = raw_block.group('body')
            uuid = str(uuid1())
            nonlocal stash

            stash[uuid] = body

            return f'<stash>{uuid}</stash>'

        result = self.pattern.sub(_sub, content)

        if stash:
            with open(self._stash_path, 'wb') as stash_file:
                dump(stash, stash_file)

        return result

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.process_raw_blocks(content))
