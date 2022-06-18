'''Various utilities used here and there in the Foliant code.'''

import pkg_resources
import time

from contextlib import contextmanager
from importlib import import_module
from logging import Logger
from pathlib import Path
from pkgutil import iter_modules
from shutil import rmtree
from traceback import format_exc
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Type


def get_available_tags() -> Set[str]:
    '''Extract ``tags`` attribute values from installed
    ``foliant.preprocessors.*.Preprocessor`` classes.

    :returns: Set of tags
    '''

    preprocessors_module = import_module('foliant.preprocessors')

    result = set()

    for importer, modname, _ in iter_modules(preprocessors_module.__path__):
        if modname == 'base':
            continue

        result.update(importer.find_module(modname).load_module(modname).Preprocessor.tags)

    return result


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
        if modname == 'base':
            continue

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


def get_foliant_packages() -> List[str]:
    '''Get the list of installed Foliant-related packages with their versions.

    :returns: List of names and versions of the packages of Foliant core and extensions
    '''

    # pylint: disable=not-an-iterable

    foliant_packages = []
    all_packages = pkg_resources.working_set

    for package in all_packages:
        if package.key == 'foliant':
            foliant_core_version = package.version

        elif package.key.startswith('foliantcontrib.'):
            foliant_packages.append(
                f'{package.key.replace("foliantcontrib.", "", 1)} {package.version}'
            )

    foliant_packages = sorted(foliant_packages)
    foliant_packages.insert(0, f'foliant {foliant_core_version}')

    return foliant_packages


def output(text: str, quiet=False):
    '''Outputs the text to STDOUT in non-quiet mode

    :param text: Message to output
    '''

    if not quiet:
        print(text, flush=True)


@contextmanager
def spinner(text: str, logger: Logger, quiet=False, debug=False):
    '''Decoration for long running processes.

    :param text: Message to output
    :param logger: Logger to capture the error if it occurs
    :param quiet: If ``True``, messages will be hidden
    :param debug: If ``True``, show full tracebacks
    '''

    # pylint: disable=broad-except

    try:
        starttime = time.time()
        logger.info(text)

        if not quiet:
            print(text, end='... ', flush=True)

        yield

        if not quiet:
            elapsed = round(time.time() - starttime, 3)
            print(f'Done in {elapsed}s', flush=True)

    except Exception as exception:
        exception_traceback = format_exc()

        logger.error(exception_traceback)

        if not quiet:
            if debug:
                print(exception_traceback)

            else:
                print(str(exception))


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
