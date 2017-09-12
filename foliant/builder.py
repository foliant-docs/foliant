"""Document builder for foliant. Implements "build" subcommand."""

import sys
import os, shutil, json
from os.path import join, splitext
from datetime import date

from colorama import Fore
import yaml

from . import gitutils, pandoc, uploader, diagrams, includes


SOURCES_DIR_NAME = "sources"
IMAGES_DIR_NAME = "images"
TEMPLATES_DIR_NAME = "templates"
REFERENCES_DIR_NAME = "references"
TMP_DIR_NAME = "foliantcache"
MERGED_SRC_FILE_NAME = "output.md"
CONFIG_FILE_NAME = "config.json"


def copy_dir_content(src, dest):
    """Recusrively copy directory content to another directory."""

    if not os.path.exists(src):
        return

    for child in os.listdir(src):
        if os.path.isfile(join(src, child)):
            shutil.copy(join(src, child), dest)
        elif os.path.isdir(join(src, child)):
            if os.path.exists(join(dest, child)):
                shutil.rmtree(join(dest, child))
            shutil.copytree(join(src, child), join(dest, child))


def get_version(cfg):
    """Extract version from config or generate it from git tag and revcount.
    Append current date.
    """

    components = []

    git_version = gitutils.get_version() if cfg["version"] == "auto" else cfg["version"]
    if git_version:
        components.append(git_version)

    if cfg["date"] == "true":
        components.append(date.today().strftime("%d-%m-%Y"))

    return '-'.join(components)


def get_title(cfg):
    """Generate file name from config: slugify the title and add version."""

    components = []

    file_name = cfg.get("file_name", cfg["title"].replace(' ', '_'))
    components.append(file_name)

    version = get_version(cfg)
    if version:
        components.append(version)

    return '_'.join(components)


def collect_source(project_dir, target_dir, src_file, cfg):
    """Copy .md files, images, templates, and references from the project
    directory to a temporary directory.
    """

    print("Collecting source... ", end='')
    sys.stdout.flush()

    with open(join(target_dir, src_file), 'w+', encoding="utf8") as src:
        chapters = cfg.get("chapters")

        if not chapters:
            try:
                with open(join(project_dir, "main.yaml"), encoding="utf8") as chapters_file:
                    chapters = yaml.load(chapters_file)["chapters"]

                print(
                    Fore.YELLOW
                    + "\nWarning: main.yaml is deprecated."
                    + " Use `chapters` key in config.json instead."
                )

            except FileNotFoundError:
                print(
                    Fore.RED + "\nCritical error: `chapters` key is missing in config.json."
                )
                print(Fore.RESET)
                sys.exit()

        for chapter_name in chapters:
            chapter_file = chapter_name + ".md"
            with open(
                join(project_dir, SOURCES_DIR_NAME, chapter_file),
                encoding="utf8"
            ) as chapter:
                src.write(
                    includes.process_includes(
                        chapter.read(),
                        join(project_dir, SOURCES_DIR_NAME),
                        target_dir,
                        cfg
                    ) + "\n"
                )

    copy_dir_content(join(project_dir, SOURCES_DIR_NAME, IMAGES_DIR_NAME), target_dir)
    copy_dir_content(join(project_dir, TEMPLATES_DIR_NAME), target_dir)
    copy_dir_content(join(project_dir, REFERENCES_DIR_NAME), target_dir)

    print("Done!")


def build(target_format, project_dir):
    """Convert source Markdown to the target format using Pandoc."""

    os.makedirs(TMP_DIR_NAME, exist_ok=True)

    with open(join(project_dir, CONFIG_FILE_NAME), encoding="utf8") as cfg_file:
        cfg = json.load(cfg_file)

    output_title = get_title(cfg)

    collect_source(project_dir, TMP_DIR_NAME, MERGED_SRC_FILE_NAME, cfg)
    diagrams.process_diagrams(TMP_DIR_NAME, MERGED_SRC_FILE_NAME)

    if target_format.startswith('p'):
        output_file = output_title + ".pdf"
        pandoc.to_pdf(MERGED_SRC_FILE_NAME, output_file, TMP_DIR_NAME, cfg)
        shutil.copy(join(TMP_DIR_NAME, output_file), output_file)
    elif target_format.startswith('d'):
        output_file = output_title + ".docx"
        pandoc.to_docx(MERGED_SRC_FILE_NAME, output_file, TMP_DIR_NAME, cfg)
        shutil.copy(join(TMP_DIR_NAME, output_file), output_file)
    elif target_format.startswith('o'):
        output_file = output_title + ".odt"
        pandoc.to_odt(MERGED_SRC_FILE_NAME, output_file, TMP_DIR_NAME, cfg)
        shutil.copy(join(TMP_DIR_NAME, output_file), output_file)
    elif target_format.startswith('t'):
        output_file = output_title + ".tex"
        pandoc.to_tex(MERGED_SRC_FILE_NAME, output_file, TMP_DIR_NAME, cfg)
        shutil.copy(join(TMP_DIR_NAME, output_file), output_file)
    elif target_format.startswith('m'):
        output_file = output_title + ".md"
        shutil.copy(join(TMP_DIR_NAME, MERGED_SRC_FILE_NAME), output_file)
    elif target_format.startswith('g'):
        output_file = output_title + ".docx"
        pandoc.to_docx(MERGED_SRC_FILE_NAME, output_file, TMP_DIR_NAME, cfg)
        output_file = uploader.upload(join(TMP_DIR_NAME, output_file))
    else:
        raise RuntimeError("Invalid target: %s" % target_format)

    return output_file
