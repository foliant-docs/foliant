from foliant.utils import get_available_config_parsers
from foliant.config import include, path


class Parser(*get_available_config_parsers().values()):
    pass
