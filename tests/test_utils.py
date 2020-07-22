'''Test utils behind Foliant's extension framework. '''

import foliant
from foliant import utils

def test_get_available_tags():
    '''Check that no tags are registered in vanilla Foliant.'''

    assert utils.get_available_tags() == set()


def test_get_available_config_parsers():
    '''Check that there are exactly two builtin config parsers: path and include.'''

    parsers = utils.get_available_config_parsers()

    assert set(parsers.keys()) == {'env', 'path', 'include'}

    for parser_class in parsers.values():
        assert issubclass(parser_class, foliant.config.base.BaseParser)

def test_get_available_clis():
    '''Check that there's exactly one default CLI with a single ``make`` command.'''

    clis = utils.get_available_clis()

    assert set(clis.keys()) == {'make'}

    for cli_class in clis.values():
        assert issubclass(cli_class, foliant.cli.base.BaseCli)

def test_get_available_backends():
    '''Check that vanilla Foliant ships only with `pre` backend, which makes `pre` target.'''

    assert utils.get_available_backends() == {'pre': ('pre',)}
