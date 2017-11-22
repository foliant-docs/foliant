'''Various utilities used here and there in the Foliant code.'''

from contextlib import contextmanager
from pkgutil import iter_modules
from importlib import import_module
from shutil import rmtree
from pathlib import Path
from typing import Dict, Tuple, Type

from halo import Halo


def get_available_config_parsers() -> Dict[str, Type]:
    '''Get the names of the installed ``foliant.config`` submodules and the corresponding
    ``Parser`` classes.

    Used for construction of the Foliant config parser, which is a class that inherits
    from all ``foliant.config.*.Parser`` classes.

    :returns: Dictionary with submodule names as keys as classes as values
    '''

    config_module = import_module('foliant.config')

    result = {}

    for importer, modname, _ in iter_modules(config_module.__path__):
        if modname == 'base':
            continue

        result[modname] = importer.find_module(modname).load_module(modname).Parser

    return result


def get_available_clis() -> Dict[str, Type]:
    '''Get the names of the installed ``foliant.cli`` submodules and the corresponding
    ``Cli`` classes.

    Used for construction of the Foliant CLI, which is a class that inherits
    from all ``foliant.cli.*.Cli`` classes.

    :returns: Dictionary with submodule names as keys as classes as values
    '''

    cli_module = import_module('foliant.cli')

    result = {}

    for importer, modname, _ in iter_modules(cli_module.__path__):
        result[modname] = importer.find_module(modname).load_module(modname).Cli

    return result


def get_available_backends() -> Dict[str, Tuple[str]]:
    '''Get the names of the installed ``foliant.backends`` submodules and the corresponding
    ``Backend.targets`` tuples.

    Used in the interactive backend selection prompt to list the available backends
    and to check if the selected target can be made with the selected backend.

    :returns: Dictionary of submodule names as keys and target tuples as values

    '''

    backends_module = import_module('foliant.backends')

    result = {}

    for importer, modname, _ in iter_modules(backends_module.__path__):
        if modname == 'base':
            continue

        result[modname] = importer.find_module(modname).load_module(modname).Backend.targets

    return result


@contextmanager
def spinner(text: str, quiet=False):
    '''Spinner decoration for long running processes.

    :param text: The spinner's caption
    :param quiet: If ``True``, the spinner is hidden
    '''

    halo = Halo(text, enabled=not quiet)
    halo.start()

    try:
        yield

        if not quiet:
            halo.succeed()
        else:
            halo.stop()

    except Exception as exception:
        if not quiet:
            halo.fail(exception)
        else:
            halo.stop()


@contextmanager
def tmp(tmp_path: Path, keep_tmp=False):
    '''Clean up tmp directory before and after running a code block.

    :param tmp_path: Path to the tmp directory
    :param keep_tmp: If ``True``, skip the cleanup
    '''

    rmtree(tmp_path, ignore_errors=True)

    yield

    if not keep_tmp:
        rmtree(tmp_path, ignore_errors=True)
