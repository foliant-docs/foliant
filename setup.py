from setuptools import setup, find_packages

import foliant


def readme():
    try:
        with open("README.rst", encoding="utf8") as f:
            return f.read()
    except IOError:
        pass

setup(
    name="foliant",
    version=foliant.__version__,
    url="https://github.com/foliant-docs/foliant",
    download_url="https://pypi.org/project/foliant",
    license="MIT",
    author="Konstantin Molchanov",
    author_email="moigagoo@live.com",
    description="Markdown-based, Pandoc-powered documentation generator.",
    long_description=readme(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    platforms="any",
    install_requires=[
        "PyDrive>=1.2.1",
        "docopt",
        "seqdiag",
        "colorama",
        "PyYAML"
    ],
    entry_points={
        "console_scripts": [
            "foliant=foliant.cli:main"
        ]
    }
)
