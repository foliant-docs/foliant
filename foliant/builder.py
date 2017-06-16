from __future__ import print_function

"""Document builder for foliant. Implements "build" subcommand."""

import sys
import os, shutil, json
from os.path import join
from datetime import date

import yaml

from . import gitutils, pandoc, uploader, seqdiag, includes


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
        with open(
            join(project_dir, "main.yaml"),
            encoding="utf8"
        ) as contents_file:
            for chapter_name in yaml.load(contents_file)["chapters"]:
                chapter_file = chapter_name + ".md"
                with open(
                    join(project_dir, "sources", chapter_file),
                    encoding="utf8"
                ) as chapter:
                    src.write(
                        includes.process_includes(
                            chapter.read(),
                            join(project_dir, "sources"),
                            target_dir,
                            cfg
                        ) + "\n"
                    )

    copy_dir_content(join(project_dir, "sources", "images"), target_dir)
    copy_dir_content(join(project_dir, "templates"), target_dir)
    copy_dir_content(join(project_dir, "references"), target_dir)

    print("Done!")


def build(target_format, project_dir):
    """Convert source Markdown to the target format using Pandoc."""

    tmp_dir = "foliantcache"
    src_file = "output.md"

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    cfg = json.load(open(join(project_dir, "config.json"), encoding="utf8"))
    output_title = get_title(cfg)

    collect_source(project_dir, tmp_dir, src_file, cfg)

    seqdiag.process_diagrams(tmp_dir, src_file)

    if target_format.startswith('p'):
        output_file = output_title + ".pdf"
        pandoc.to_pdf(src_file, output_file, tmp_dir, cfg)
        shutil.copy(join(tmp_dir, output_file), output_file)
    elif target_format.startswith('d'):
        output_file = output_title + ".docx"
        pandoc.to_docx(src_file, output_file, tmp_dir, cfg)
        shutil.copy(join(tmp_dir, output_file), output_file)
    elif target_format.startswith('o'):
        output_file = output_title + ".odt"
        pandoc.to_odt(src_file, output_file, tmp_dir, cfg)
        shutil.copy(join(tmp_dir, output_file), output_file)
    elif target_format.startswith('t'):
        output_file = output_title + ".tex"
        pandoc.to_tex(src_file, output_file, tmp_dir, cfg)
        shutil.copy(join(tmp_dir, output_file), output_file)
    elif target_format.startswith('m'):
        output_file = output_title + ".md"
        shutil.copy(join(tmp_dir, src_file), output_file)
    elif target_format.startswith('g'):
        output_file = output_title + ".docx"
        pandoc.to_docx(src_file, output_file, tmp_dir, cfg)
        uploader.upload(join(tmp_dir, output_file))
    else:
        raise RuntimeError("Invalid target: %s" % target_format)

    return output_file
