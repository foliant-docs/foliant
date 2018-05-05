from pathlib import Path
from shutil import move, rmtree
from datetime import date
from filecmp import dircmp

from foliant.cli import Foliant


class TestPreBackend(object):
    tests_path = Path(__file__).absolute().parent
    test_project_dir_name = 'pre-backend-test-project'
    reference_dir_name = 'pre-backend-test-projec-reference'

    def setup(self):
        '''Build ``pre`` target from the sample project and put it into the tests dir.'''

        self.result_dir_name = Foliant().make(
            'pre',
            project_path=self.tests_path/self.test_project_dir_name,
            quiet=True
        )

        self.result_path = self.tests_path / self.result_dir_name

        rmtree(self.result_path, ignore_errors=True)
        move(Path(self.result_dir_name), self.result_path)

    def test_dir_name(self):
        '''Check that the result is built into a directory with the right name.'''

        title_part = self.test_project_dir_name.replace('-', ' ').title().replace(' ', '_')
        date_part  = date.today().isoformat()

        assert self.result_dir_name == f'{title_part}-{date_part}.pre'

    def test_compare_with_reference(self):
        '''Check that the result is the same as the reference.'''

        assert not dircmp(self.result_path, self.tests_path/self.reference_dir_name).diff_files

    def teardown(self):
        rmtree(self.result_path)
