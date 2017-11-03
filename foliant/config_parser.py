'''Parser for ``foliant.yml`` config file.'''

from pathlib import Path

from yaml import load, add_constructor


DEFAULTS = {
    'src_dir': Path('./src'),
    'tmp_dir': Path('./__folianttmp__')
}

def parse(project_path: Path, config_file_name: str) -> dict:
    '''Parse the config file into a Python dict. Missing values are populated
    with defaults, paths are converted to ``pathlib.Paths``.

    :param project_path: Project path
    :param config_file_name: Config file name (almost certainly ``foliant.yml``)

    :returns: Dictionary representing the YAML tree
    '''

    def _resolve_path_tag(_, node) -> str:
        path = Path(node.value).expanduser()
        return (project_path / path).absolute().resolve().as_posix()

    add_constructor('!path', _resolve_path_tag)

    with open(project_path/config_file_name) as config_file:
        config = {**DEFAULTS, **load(config_file)}

        config['src_dir'] = Path(config['src_dir']).expanduser()
        config['tmp_dir'] = Path(config['tmp_dir']).expanduser()

        return config
