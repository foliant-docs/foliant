import os
from pathlib import Path
import yaml

TMP_DIR = "tmp"

def collect_source(project_path, target_dir, src_file):
    print("Collecting source... ", end='')

    with (target_dir/src_file).open('w+') as combined_source:
        with (project_path/"main.yaml").open() as contents_file:
            for chapter_name in yaml.load(contents_file)["chapters"]:
                chapter_file = chapter_name + ".md"
                with (project_path/"sources"/chapter_file).open() as chapter:
                    combined_source.write(chapter.read() + '\n')

def build(target_format, project_path):
    if not Path(TMP_DIR).exists:
        os.makedirs(TMP_DIR)

    collect_source(Path(project_path), Path(TMP_DIR), "output.md")

    return "output"
