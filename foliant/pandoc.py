"""Wrapper around Pandoc. Used by builder."""

from __future__ import print_function

import sys
import subprocess
from . import gitutils

PANDOC_PATH = "pandoc"

FROM_PARAMS = "-f markdown_strict+simple_tables+multiline_tables+grid_tables+\
pipe_tables+table_captions+fenced_code_blocks+line_blocks+definition_lists+\
all_symbols_escapable+strikeout+superscript+subscript+\
lists_without_preceding_blankline+implicit_figures+raw_tex+citations+\
tex_math_dollars+header_attributes+auto_identifiers+startnum+footnotes+\
inline_notes+fenced_code_attributes+intraword_underscores+escaped_line_breaks"

LATEX_PARAMS = "--no-tex-ligatures --smart --normalize --listings --number-sections \
--latex-engine=xelatex"


def generate_variable(key, value):
    """Generate a ``--variable key=value`` entry."""

    return '--variable "%s"="%s"' % (key, value)

def generate_command(params, output_file, src_file, cfg, set_template=False):
    """Generate the entire Pandoc command with params to invoke."""

    params = ["-o " + output_file, FROM_PARAMS, LATEX_PARAMS, params]

    for key, value in cfg.items():
        if key in ("title", "second_title", "year", "date", "title_page", "tof", "toc"):
            params.append(generate_variable(key, value))
        elif key == "template" and set_template:
            params.append('--template="%s.tex"' % value)
        elif key == "lang":
            if value in ("russian", "english"):
                params.append(generate_variable(value, "true"))
            else:
                params.append(generate_variable("russian", "true"))
        elif key == "version":
            if value == "auto":
                version = gitutils.get_version()
                if version:
                    params.append(generate_variable(key, version))
            else:
                params.append(generate_variable(key, value))
        elif key == "company":
            params.append(generate_variable(key, value))
        elif key in ("type", "alt_doc_type"):
            if value:
                params.append(generate_variable(key, value))
        elif key == "filters":
            for filt in value:
                params.append("-F %s" % filt)
        elif key == "file_name":
            pass
        elif key == "git":
            pass
        else:
            print("Unsupported config key: %s" % key)

    return ' '.join([PANDOC_PATH] + params + [src_file])


def run(command, src_dir):
    """Invoke the Pandoc executable with the generated params."""

    print("Baking output... ", end='')
    sys.stdout.flush()

    try:
        subprocess.check_output(
            command,
            cwd=src_dir,
            stderr=subprocess.PIPE,
            shell=True
        )

        print("Done!")

    except subprocess.CalledProcessError as e:
        quit(e.stderr.decode())


def to_pdf(src_file, output_file, tmp_path, cfg):
    """Convert Markdown to PDF via Pandoc."""

    pandoc_command = generate_command(
        "-t latex",
        output_file,
        src_file,
        cfg,
        set_template=True
    )
    run(pandoc_command, tmp_path)


def to_docx(src_file, output_file, tmp_path, cfg):
    """Convert Markdown to Docx via Pandoc."""

    pandoc_command = generate_command(
        '--reference-docx="ref.docx"',
        output_file,
        src_file,
        cfg
    )
    run(pandoc_command, tmp_path)


def to_odt(src_file, output_file, tmp_path, cfg):
    """Convert Markdown to OpenDocument via Pandoc."""

    pandoc_command = generate_command(
        '--reference-odt="ref.odt"',
        output_file,
        src_file,
        cfg
    )
    run(pandoc_command, tmp_path)


def to_tex(src_file, output_file, tmp_path, cfg):
    """Convert Markdown to TeX via Pandoc."""

    pandoc_command = generate_command(
        "-t latex",
        output_file,
        src_file,
        cfg,
        set_template=True
    )
    run(pandoc_command, tmp_path)
