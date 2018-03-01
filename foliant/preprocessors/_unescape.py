import re

from foliant.utils import get_available_tags
from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pattern = re.compile(
            rf'\<\<(?P<tag>.+)'+
            rf'(\s(?P<options>.*?))?\>'+
            rf'(?P<body>.*?)\</(?P=tag)\>',
            flags=re.MULTILINE|re.DOTALL
        )

    def process_escaped_tags(self, content: str) -> str:
        '''Unescape escaped tags, i.e. remove leading ``<`` from each tag definition.

        :param content: Markdown content

        :returns: Markdown content without escaped tags
        '''

        def _sub(escaped_tag):
            return escaped_tag.group(0)[1:]

        return self.pattern.sub(_sub, content)

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.process_escaped_tags(content))
