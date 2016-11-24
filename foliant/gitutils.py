""""Wrapper around a few git commands. Used by builder to determin document
version.
"""

import shlex, subprocess

def get_version():
    """Generate document version based on git tag and number of revisions."""

    components = []

    try:
        components.append(
            subprocess.check_output(shlex.split("git describe --abbrev=0"))
            .strip().decode()
        )
        components.append(
            subprocess.check_output(shlex.split("git rev-list --count master"))
            .strip().decode()
        )
    except:
        pass

    return '.'.join(components) if components else None
