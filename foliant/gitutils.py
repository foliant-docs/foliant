""""Wrapper around a few git commands. Used by builder to determin document
version.
"""

import subprocess
from os.path import join

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


def get_repo(repo_url, target_dir):
    """Clone git repository if it's not cloned yet or pull changes otherwise.
    """

    repo_name = repo_url.split('/')[-1].split('.')[0]
    repo_path = join(target_dir, repo_name)

    print("Fetching %s..." % repo_url, end=' ')

    if subprocess.run(
        "git clone %s %s" % (repo_url, repo_path),
        stderr=subprocess.PIPE
    ):
        subprocess.run(
            "git --work-tree %s pull origin master" % repo_path,
            stderr=subprocess.PIPE
        )

    print("Done!")


if __name__ == "__main__":
    get_repo("git@git.restr.im:docs-itv/doorstopper_itv.git", "foliantcache")
