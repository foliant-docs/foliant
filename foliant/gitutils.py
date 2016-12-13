""""Wrapper around a few git commands. Used by builder to determin document
version.
"""

import subprocess

def get_version():
    """Generate document version based on git tag and number of revisions."""

    components = []

    try:
        components.append(
            subprocess.check_output(
                "git describe --abbrev=0",
                stderr=subprocess.PIPE,
                shell=True
            ).strip().decode()
        )
        components.append(
            subprocess.check_output(
                "git rev-list --count master",
                stderr=subprocess.PIPE,
                shell=True
            ).strip().decode()
        )
    except:
        pass

    return '.'.join(components) if components else None
