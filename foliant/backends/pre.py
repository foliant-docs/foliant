from shutil import copytree, rmtree

from foliant.backends.base import BaseBackend


class Backend(BaseBackend):
    '''Backend that just applies its preprocessors and returns a project
    that doesn't need any further preprocessing.
    '''

    targets = ('pre',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pre_config = self.config.get('backend_config', {}).get('pre', {})

        self._preprocessed_dir_name = f'{self._pre_config.get("slug", self.get_slug())}.pre'

        self.logger = self.logger.getChild('pre')

        self.logger.debug(f'Backend inited: {self.__dict__}')

    def make(self, target: str) -> str:
        rmtree(self._preprocessed_dir_name, ignore_errors=True)
        copytree(self.working_dir, self._preprocessed_dir_name)

        return self._preprocessed_dir_name
