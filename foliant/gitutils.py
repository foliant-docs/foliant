import shlex, subprocess

def get_version():
    git_describe = subprocess.run(
        shlex.split("git describe --abbrev=0"),
        stdout=subprocess.PIPE
    )

    git_revlist = subprocess.run(
        shlex.split("git rev-list --count master"),
        stdout=subprocess.PIPE
    )

    components = []

    if not git_describe.returncode:
        components.append(git_describe.stdout.decode().strip())
    if not git_revlist.returncode:
        components.append(git_revlist.stdout.decode().strip())

    return '.'.join(components) if components else None
