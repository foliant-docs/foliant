from setuptools import setup, find_packages

from foliant import __version__ as foliant_version


SHORT_DESCRIPTION = 'Modular, Markdown-based documentation generator that makes \
pdf, docx, html, and more.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliant',
    version=foliant_version,
    url='https://github.com/foliant-docs/foliant',
    download_url='https://pypi.org/project/foliant',
    license='MIT',
    author='Konstantin Molchanov',
    author_email='moigagoo@live.com',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'PyYAML',
        'cliar>=1.1.9',
        'halo>=0.0.10',
        'prompt_toolkit'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points={
        'console_scripts': [
            'foliant=foliant.cli:entry_point'
        ]
    }
)
