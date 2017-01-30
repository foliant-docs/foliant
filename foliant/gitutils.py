""""Wrapper around a few git commands. Used by builder to determin document
version.
"""

import sys
import subprocess
from os.path import join


def get_version():
    """Generate document version based on git tag and number of revisions."""

    components = []

    try:
        components.append(
            subprocess.check_output(
                "git describe --abbrev=0",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True
            ).strip().decode()
        )
        components.append(
            subprocess.check_output(
                "git rev-list --count master",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True
            ).strip().decode()
        )
    except:
        pass

    return '.'.join(components) if components else None


def sync_repo(repo_url, target_dir, revision="master"):
    """Clone git repository if it's not cloned yet or pull changes otherwise.
    """

    repo_name = repo_url.split('/')[-1].split('.')[0]
    repo_path = join(target_dir, repo_name)

    if subprocess.run(
        "git clone %s %s" % (repo_url, repo_path),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True
    ).returncode != 0:
        subprocess.run(
            "git pull",
            cwd=repo_path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True
        )

    subprocess.run(
        "git checkout %s" % revision,
        cwd=repo_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True
    )

    return repo_path
