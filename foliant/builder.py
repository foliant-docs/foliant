from __future__ import print_function

import os, shutil, json
from os.path import join
import yaml
from . import gitutils, pandoc, uploader

def copy_dir_content(src, dest):
    for child in os.listdir(src):
        if os.path.isfile(join(src, child)):
            shutil.copy(join(src, child), dest)
        elif os.path.isdir(join(src, child)):
            shutil.copytree(join(src, child), join(dest, child))

def get_title(document_title, version):
    slug = document_title.replace(' ', '_')
    return '.'.join((slug, version)) if version else slug

def collect_source(project_dir, target_dir, src_file):
    print("Collecting source... ", end='')

    with open(join(target_dir, src_file), 'w+') as src:
        with open(join(project_dir, "main.yaml")) as contents_file:
            for chapter_name in yaml.load(contents_file)["chapters"]:
                chapter_file = chapter_name + ".md"
                with open(join(project_dir, "sources", chapter_file)) as chapter:
                    src.write(chapter.read() + '\n')

    copy_dir_content(join(project_dir, "sources", "images"), target_dir)
    copy_dir_content(join(project_dir, "templates"), target_dir)
    copy_dir_content(join(project_dir, "references"), target_dir)

    print("Done!")

def build(target_format, project_dir):
    tmp_dir = "tmp"
    src_file = "output.md"

    if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    cfg = json.load(open(join(project_dir, "config.json")))
    output_title = get_title(cfg["title"], gitutils.get_version())

    collect_source(project_dir, tmp_dir, src_file)

    if target_format.startswith('p'):
        output_file = output_title + ".pdf"
        pandoc.to_pdf(src_file, output_file, tmp_dir, cfg)
        shutil.copy(join(tmp_dir, output_file), output_file)
    elif target_format.startswith('d'):
        output_file = output_title + ".docx"
        pandoc.to_docx(src_file, output_file, tmp_dir, cfg)
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
        uploader.upload(output_file)
    else:
        raise RuntimeError("Invalid target: %s" % target_format)

    shutil.rmtree(tmp_dir)

    return output_file
