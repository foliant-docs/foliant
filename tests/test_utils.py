from foliant import utils


def test_get_available_tags():
    assert utils.get_available_tags() == set()

