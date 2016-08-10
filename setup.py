from setuptools import setup, find_packages

import foliant as pkg


try:
    long_description = open("README.rst").read()

except:
    long_description = pkg.__doc__


setup(
    name=pkg.__name__,
    description=pkg.__description__,
    long_description=long_description,
    author=pkg.__author__,
    author_email=pkg.__author_email__,
    version=pkg.__version__,
    url="https://github.com/foliant-docs/foliant",
    packages=find_packages(exclude=["docs"]),
    install_requires=[
        "PyDrive",
        "PyYAML",
        "requests",
        "cherrypy",
        "cliar"
    ],
    license="MIT",
    entry_points={
        "console_scripts": [
            "foliant=foliant.cli:main"
        ]
    }
)
