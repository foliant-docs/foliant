'''Test the builtin ``_unescape`` preprocessor that turns escaped tags
(``<<tag></tag>``) into unescaped ones (``<tag></tag>``) in output without
processing them.
'''

from logging import Logger
from pathlib import Path

from foliant.preprocessors import _unescape


class TestUnescape(object):
    preprocessor = _unescape.Preprocessor(
        {'project_path': Path('.'), 'config': {'tmp_dir': Path('.')}},
        Logger(''),
        {}
    )

    def test_simple(self):
        '''Check that a simple escaped tag without body gets unescaped.'''

        input_text = 'Text before escaped tag. <<tag></tag> Text after escapted tag.'
        expected_text = 'Text before escaped tag. <tag></tag> Text after escapted tag.'

        assert self.preprocessor.process_escaped_tags(input_text) == expected_text

    def test_body_and_options(self):
        '''Check that an escaped tag with body and options gets unescaped.'''

        input_text = 'Text before. <<tag foo="bar">body</tag> Text after.'
        expected_text = 'Text before. <tag foo="bar">body</tag> Text after.'

        assert self.preprocessor.process_escaped_tags(input_text) == expected_text

    def test_multiline(self):
        input_text = '''Text before escaped tag.
<<tag>
    Body.
</tag>
'''
        expected_text = '''Text before escaped tag.
<tag>
    Body.
</tag>
'''
        assert self.preprocessor.process_escaped_tags(input_text) == expected_text

    def test_false_positive(self):
        '''Check that regular tags aren't unescaped.'''

        input_text = 'Text before regular tag. <tag></tag> Text after regular tag.'
        expected_text = input_text

        assert self.preprocessor.process_escaped_tags(input_text) == expected_text

    def test_tag_in_body(self):
        '''Check that escaped tag inside escaped tag is considered its body and
        therefore *not* processed.
        '''

        input_text = 'Text before. <<tag><<shmag></shmag></tag> Text after.'
        expected_text = 'Text before. <tag><<shmag></shmag></tag> Text after.'

        assert self.preprocessor.process_escaped_tags(input_text) == expected_text

    def test_unclosed(self):
        '''Check that unclosed tags are ignored'''

        input_text = 'Text before. <<tag><<shmag></shmag> Text after.'
        expected_text = 'Text before. <<tag><shmag></shmag> Text after.'

        assert self.preprocessor.process_escaped_tags(input_text) == expected_text
