import re
from logging import Logger
from distutils.util import strtobool
from typing import Dict
OptionValue = int or float or bool or str


class BasePreprocessor(object):
    '''Base preprocessor. All preprocessors must inherit from this one.'''

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

        def _cast_value(value: str) -> OptionValue:
            '''Attempt to convert a string to integer, float, or boolean.

            If nothing matches, return the original string.

            :param value: String to convert

            :returns: Converted value or original string
            '''

            value = value.strip('"')

            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    try:
                        return bool(strtobool(value))
                    except ValueError:
                        return value

        option_pattern = re.compile(
            r'(?P<key>[A-Za-z_:][0-9A-Za-z_:\-\.]*)="(?P<value>.+?)"',
            flags=re.DOTALL
        )

        return {
            option.group('key'): _cast_value(option.group('value'))
            for option in option_pattern.finditer(options_string)
        }

    def __init__(self, context: dict, logger: Logger, options={}):
        # pylint: disable=dangerous-default-value

        self.project_path = context['project_path']
        self.config = context['config']
        self.context = context
        self.logger = logger
        self.options = {**self.defaults, **options}

        self.working_dir = self.project_path / self.config['tmp_dir']

        if self.tags:
            self.pattern = re.compile(
                rf'(?<!\<)\<(?P<tag>{"|".join(self.tags)})' +
                rf'(\s(?P<options>[^\<\>]*))?\>' +
                rf'(?P<body>.*?)\<\/(?P=tag)\>',
                flags=re.DOTALL
            )

    def apply(self):
        '''Run the preprocessor against the project directory. Must be implemented
        by every preprocessor.
        '''

        raise NotImplementedError
