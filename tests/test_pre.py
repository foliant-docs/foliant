from platform import system
from filecmp import dircmp
from datetime import date
from shutil import rmtree
from os import chdir
from collections import namedtuple

from pytest import fixture
from yaml import load

from foliant.cli import Foliant


BuiltProject = namedtuple('Build', ['name', 'title', 'dir_name'])


@fixture(params=['simple'])
def build_project(request, datadir):
    chdir(datadir)

    project_path = datadir / 'projects' / request.param

    result = Foliant().make(
        'pre',
        project_path=project_path,
        quiet=True
    )

    with open(project_path/'foliant.yml') as config:
        yield BuiltProject(request.param, load(config)['title'], result)


def test_dir_name(build_project):
    title_part = build_project.title.replace(' ', '_')
    date_part = date.today().isoformat()
    assert build_project.dir_name == f'{title_part}-{date_part}.pre'


def test_content(build_project, datadir):
    newline_kind = 'crlf' if system() == 'Windows' else 'lf'
    reference_path = datadir / 'references' / newline_kind / build_project.name

    assert not dircmp(build_project.dir_name, reference_path).diff_files
