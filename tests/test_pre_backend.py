from pathlib import Path
from shutil import move, rmtree
from platform import system
from filecmp import dircmp
from datetime import date
from collections import namedtuple


Project = namedtuple('Project', ('dir_name', 'path'))


from foliant.cli import Foliant


class TestPreBackend(object):
    tests_path = Path(__file__).absolute().parent
    test_projects_path = tests_path / 'projects'
    references_path = tests_path / 'references' / ('crlf' if system() == 'Windows' else 'lf')
    test_projects = 'simple',

    def setup(self):
        self.results = {}

        for project in self.test_projects:
            result_dir_name =  Foliant().make(
                'pre',
                project_path=self.test_projects_path/project,
                quiet=True
            )

            result_path = self.tests_path / result_dir_name

            rmtree(result_path, ignore_errors=True)
            move(Path(result_dir_name), result_path)

            self.results[project] = Project(result_dir_name, result_path)

    def test_simple_dir_name(self):
        assert self.results['simple'].dir_name == f'Simple-{date.today().isoformat()}.pre'

    def test_simple_compare_with_reference(self):
        assert not dircmp(self.results['simple'].path, self.references_path/'simple').diff_files

    def teardown(self):
        for result_path in (result.path for result in self.results.values()):
            rmtree(result_path)
