import foliant
from foliant import utils

def test_get_available_tags():
    '''Check that no tags are registered in vanilla Foliant.'''

    assert utils.get_available_tags() == set()


def test_get_available_config_parsers():
    '''Check that there are exactly two builtin config parsers: path and include.'''

    parsers = utils.get_available_config_parsers()

    assert set(parsers.keys()) == {'path', 'include'}
    assert issubclass(parsers['path'], foliant.config.base.BaseParser)

def test_get_available_clis():
    '''Check that there's exactly one default CLI with a single ``make`` command.'''

    clis = utils.get_available_clis()

    assert set(clis.keys()) == {'make'}

    for cli_type in clis.values():
        assert issubclass(cli_type, foliant.cli.base.BaseCli)
