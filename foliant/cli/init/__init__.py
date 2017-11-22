'''New project generator for Foliant doc buidler.'''

from pathlib import Path
from shutil import copytree

from cliar import Cliar, set_help, set_arg_map, set_metavars
from prompt_toolkit import prompt
from slugify import slugify

from foliant.utils import spinner


class Cli(Cliar):
    @set_arg_map({'project_title': 'name'})
    @set_metavars({'project_title': 'NAME'})
    @set_help(
        {
            'project_title': 'Name of the Foliant project',
            'quiet': 'Hide all output accept for the result. Useful for piping.'
        }
    )
    def init(self, project_title='', quiet=False):
        '''Generate new Foliant project.'''

        if not project_title:
            project_title = prompt('Enter the project name: ')

        project_path = Path(slugify(project_title))

        template_path = Path(__file__).parent / '_project_template'

        result = None

        with spinner('Generating Foliant project', quiet):
            copytree(template_path, project_path)

            foliant_yml_path = project_path / 'foliant.yml'

            with open(foliant_yml_path, encoding='utf8') as foliant_yml:
                foliant_yml_content = foliant_yml.read()

            with open(foliant_yml_path, 'w', encoding='utf8') as foliant_yml:
                foliant_yml.write(foliant_yml_content.format(project_title=project_title))

            result = project_path.absolute()

        if result:
            if not quiet:
                print('─────────────────────')
                print(f'Project "{project_title}" created in {result}')
            else:
                print(result)

        else:
            exit(1)
