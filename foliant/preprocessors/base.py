import re
from logging import Logger
from typing import Dict
import yaml
OptionValue = int or float or bool or str


class BasePreprocessor():
    '''Base preprocessor. All preprocessors must inherit from this one.'''

    # pylint: disable=too-many-instance-attributes

    defaults = {}
    tags = ()

    @staticmethod
    def get_options(options_string: str) -> Dict[str, OptionValue]:
        '''Get a dictionary of typed options from a string with XML attributes.

        :param options_string: String of XML attributes

        :returns: Dictionary with options
        '''

        if not options_string:
            return {}

        option_pattern = re.compile(
            r'(?P<key>[A-Za-z_:][0-9A-Za-z_:\-\.]*)=(\'|")(?P<value>.+?)\2',
            flags=re.DOTALL
        )

        return {
            option.group('key'): yaml.load(option.group('value'), yaml.Loader)
            for option in option_pattern.finditer(options_string)
        }

    def __init__(self, context: dict, logger: Logger, quiet=False, debug=False, options={}):
        # pylint: disable=dangerous-default-value
        # pylint: disable=too-many-arguments

        self.project_path = context['project_path']
        self.config = context['config']
        self.context = context
        self.logger = logger
        self.quiet = quiet
        self.debug = debug
        self.options = {**self.defaults, **options}

        self.working_dir = self.project_path / self.config['tmp_dir']

        if self.tags:
            self.pattern = re.compile(
                rf'(?<!\<)\<(?P<tag>{"|".join(self.tags)})' +
                r'(\s(?P<options>[^\<\>]*))?\>' +
                r'(?P<body>.*?)\<\/(?P=tag)\>',
                flags=re.DOTALL
            )

    def apply(self):
        '''Run the preprocessor against the project directory. Must be implemented
        by every preprocessor.
        '''

        raise NotImplementedError
