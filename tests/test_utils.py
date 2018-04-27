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

