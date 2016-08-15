import shutil, json
from pathlib import Path
import yaml
from . import gitutils, pandoc

TMP_DIR = Path("tmp")
COMBINED_SRC = "output.md"
SOURCES_DIR = "sources"
TEMPLATES_DIR = "templates"
REFERENCES_DIR = "references"
IMAGES_DIR = "images"
CONTENTS_FILE = "main.yaml"
CONFIG_FILE = "config.json"

def copy_dir_content(src, dest):
    for child in src.iterdir():
        if child.is_file():
            shutil.copy(str(child), str(dest))
        elif child.is_dir():
            shutil.copytree(str(child), str(dest/child.name))

def get_title(document_title, version):
    slug = document_title.replace(' ', '_')
    return '.'.join((slug, version)) if version else slug

def collect_source(project_dir, target_dir, src_file):
    print("Collecting source... ", end='')

    with (target_dir/src_file).open('w+') as combined_source:
        with (project_dir/CONTENTS_FILE).open() as contents_file:
            for chapter_name in yaml.load(contents_file)["chapters"]:
                chapter_file = chapter_name + ".md"
                with (project_dir/SOURCES_DIR/chapter_file).open() as chapter:
                    combined_source.write(chapter.read() + '\n')

    copy_dir_content(project_dir/SOURCES_DIR/IMAGES_DIR, target_dir)
    copy_dir_content(project_dir/TEMPLATES_DIR, target_dir)
    copy_dir_content(project_dir/REFERENCES_DIR, target_dir)

    print("Done!")

def build(target_format, project_dir):
    project_dir = Path(project_dir)

    if TMP_DIR.exists(): shutil.rmtree(str(TMP_DIR))
    TMP_DIR.mkdir(parents=True)

    cfg = json.load((project_dir/"config.json").open())
    output_title = get_title(cfg["title"], gitutils.get_version())

    collect_source(project_dir, TMP_DIR, COMBINED_SRC)

    if target_format.startswith('p'):
        output_file = output_title + ".pdf"
        pandoc.to_pdf(COMBINED_SRC, output_file, str(TMP_DIR), cfg)
        shutil.copy(str(TMP_DIR/output_file), output_file)
    elif target_format.startswith('d'):
        output_file = output_title + ".docx"
        pandoc.to_docx(COMBINED_SRC, output_file, str(TMP_DIR), cfg)
        shutil.copy(str(TMP_DIR/output_file), output_file)
    elif target_format.startswith('t'):
        output_file = output_title + ".tex"
        pandoc.to_docx(COMBINED_SRC, output_file, str(TMP_DIR), cfg)
        shutil.copy(str(TMP_DIR/output_file), output_file)
    elif target_format.startswith('m'):
        output_file = output_title + ".md"
        shutil.copy(str(TMP_DIR/COMBINED_SRC), output_file)
    else:
        raise RuntimeError("Invalid target: %s" % target_format)

    return output_file
