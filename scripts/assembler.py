# -*- coding: utf-8 -*
import os
import sys
import json
import yaml
import datetime
import subprocess
import re
import fileinput
import shutil
import include_text as inc
import my_mail
import gitlab

#TODO: Open all shell sessions via subprocess

git_url_prefix = "gitlab.com"
git_path = ""

reload(sys)
# sys.setdefaultencoding('cp1251')
sys.setdefaultencoding('utf-8')

def dir_list(dir_name, subdir, *args):
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if len(args) == 0:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
        elif os.path.isdir(dirfile) and subdir:
            fileList += dir_list(dirfile, subdir, *args)
    return fileList

def combine_files(fileList, fn):
    if not os.path.exists(os.path.join(current_path,'scripts/staging')):
        os.makedirs(os.path.join(current_path,'scripts/staging'))
    output = open(os.path.join(os.path.join(current_path,'scripts/staging'),fn), 'w')
    with open(os.path.join(current_path,"main.yaml"), 'r') as main:
        contents = yaml.load(main)

        def recursive_handle(chapter):
            for name in chapter:
                chapter_content = chapter[name]
                for section in chapter_content:
                    if isinstance (section, dict):
                        combine(''.join(section.keys()))
                        recursive_handle(section)
                    elif isinstance(section, str):
                        if section.startswith('git:'):
                            section = section[4:]
                        combine(section)

        def combine(section):
            for file in fileList:
                #TODO: hash table instead of iteration
                #TODO: combine files with same names but located in different directories
                source_name, source_ext = os.path.splitext(os.path.basename(file))
                if source_name == section:
                    print section
                    output.write(open(file).read().decode('utf-8')+'\n'+'\n')

        def chapter_from_git(contents):
            git_pattern = re.compile("git:(?P<file_name>.*)")
            for chapter in contents['chapters']:
                found = git_pattern.match(chapter)
                if found:
                    if not os.path.exists(os.path.join(current_path,'sources')):
                        os.makedirs(os.path.join(current_path,'sources'))
                    file_name = found.group('file_name') + '.md'
                    c = open('config.json')
                    config = json.load(c)
                    c.close()
                    git_project = config['git_project']
                    if '/' in git_project:
                        git_project = git_project.replace('/', '%2F')
                    git_branch = config['git_branch']
                    git_private_token = config['git_private_token']

                    git = gitlab.Gitlab(git_url_prefix, token=git_private_token)
                    str_from_git = git.getrawfile(git_project, git_branch, file_name)

                    f = open(current_path + '/sources/' + file_name , 'w')
                    f.write(str(str_from_git))
                    f.close()

                    shutil.copy(current_path + '/sources/' + file_name, current_path + "/scripts/staging")

                    pic_pattern = re.compile('!\[.*[^\]]\]\((?P<pic_name>.*[^\)])\)')

                    found_pic = pic_pattern.findall(str_from_git)
                    for pic in found_pic:
                        git_path = pic
                        image = git.getfile(git_project, git_path, git_branch)
                        content = image['content']
                        img = open(current_path + '/scripts/staging/' + pic, "wb")
                        img.write(content.decode('base64'))
                        img.close()
                        img = open(current_path + '/sources/' + pic, "wb")
                        img.write(content.decode('base64'))
                        img.close()

        try:
            chapter_from_git(contents)
        except:
            pass
    fileList = dir_list(search_dir, True, 'md')
    recursive_handle(contents)
    output.close()
    main.close()

def config_handler():
    config_data = open(os.path.join(current_path,'scripts/config.json'))
    #config_data = open(os.path.join(current_path,'config.json'))
    config = json.load(config_data)
    config_data.close()
    send_to_pandoc = dict()

    variable_string = ""

    for key in config:
        #TODO: Remove strict naming
        if key == "git_project":
            continue
        elif key == "git_private_token":
            continue
        elif key == "git_branch":
            continue
        elif key == "lang":
            if config[key] == "russian":
                send_to_pandoc["russian"] = "true"
            if config[key] == "english":
                send_to_pandoc["english"] = "true"
        elif key == "title_page":
            if config[key].lower() in ['true', '1']:
                send_to_pandoc[key] = "true"
        elif key == "toc":
            if config[key].lower() in ['true', '1']:
                send_to_pandoc[key] = "true"
        elif key == "tof":
            if config[key].lower() in ['true', '1']:
                send_to_pandoc[key] = "true"
        elif key == "type":
            if config[key].lower() not in ['none', '']:
                send_to_pandoc[key] = config[key]
        elif key == "alt_doc_type":
            if config[key].lower() not in ['none', '']:
                send_to_pandoc[key] = config[key]
        elif key == "version":
            if config[key].strip().lower() == 'auto':
                send_to_pandoc[key] =  get_version_counter()
            elif config[key].lower() not in ['none', '']:
                send_to_pandoc[key] = config[key]
        elif key == "second_title":
            if config[key].lower() not in ['none', '']:
                send_to_pandoc[key] = config[key]
        elif key == "date":
            if config[key].lower() in ['true', '1']:
                send_to_pandoc[key] = "true"
        elif key == "template":
            template=config[key]
        else:
            send_to_pandoc[key] = config[key]

    for key in send_to_pandoc:
        variable_string = "--variable {0}=\"{1}\" {2}".format(key, send_to_pandoc[key], variable_string).strip()
    return variable_string, template

def replace_text(file,search_exp,replace_exp):
    for line in fileinput.input(file, inplace=1):
        if search_exp in line:
            line = line.replace(search_exp,replace_exp)
        sys.stdout.write(line)

def replace_text_re(file,search_exp,replace_exp):
    for line in fileinput.input(file, inplace=1):
        line = re.sub(search_exp, r'{0}'.format(replace_exp), line)
        sys.stdout.write(line)

def docx_preprocessor(output_file):
    replace_text(output_file,'.eps','.png')
    replace_text_re(output_file, '<!-- DOCX: (.*) -->', '\\1')
    replace_text(output_file,'\\begin{mdframed}[style=redbar]','')
    replace_text(output_file,'\\end{mdframed}','')

def run_pandoc(file_type, variable_string, template):
    #TODO: Bilatex references handling
    output_file = os.path.join(os.path.join(current_path,'scripts/staging'),fn)
    if file_type == "p":
        pandoc_launch = "cd {0}/scripts/staging; pandoc -o output.pdf -f markdown_strict+simple_tables+multiline_tables+grid_tables+pipe_tables+table_captions+fenced_code_blocks+line_blocks+definition_lists+all_symbols_escapable+strikeout+superscript+subscript+lists_without_preceding_blankline+implicit_figures+raw_tex+citations+tex_math_dollars+header_attributes+auto_identifiers+startnum+footnotes+inline_notes+fenced_code_attributes+intraword_underscores+yaml_metadata_block -t latex --template={0}/scripts/template/{2}.tex --no-tex-ligatures --smart --normalize --listings --latex-engine=xelatex {1} output.md;".format(current_path, variable_string, template)
        os.popen(pandoc_launch)
    elif file_type == "d":
        docx_preprocessor(output_file)
        pandoc_launch = 'cd {0}/scripts/staging; pandoc -o output.docx -f markdown_strict+simple_tables+multiline_tables+grid_tables+pipe_tables+table_captions+fenced_code_blocks+line_blocks+definition_lists+all_symbols_escapable+strikeout+superscript+subscript+lists_without_preceding_blankline+implicit_figures+raw_tex+citations+tex_math_dollars+header_attributes+auto_identifiers+startnum+footnotes+inline_notes+fenced_code_attributes+intraword_underscores+yaml_metadata_block --template={0}/scripts/template/{2}.tex --no-tex-ligatures --smart --normalize --listings --latex-engine=xelatex --reference-docx={0}/scripts/ref.docx --toc --toc-depth=4 {1} output.md;'.format(current_path, variable_string, template)
        os.popen(pandoc_launch)
    elif file_type == "g":
        version_counter = get_version_counter()
        with open(output_file, 'r') as original: data = original.read()
        with open(output_file, 'w') as modified: modified.write('_Version of the document: ' + version_counter + '.' + datetime.date.today().strftime('%d-%m-%Y') + data)
        original.close()
        modified.close()
        docx_preprocessor(output_file)
        pandoc_launch = "cd {0}/scripts/staging; pandoc -o output.docx -f markdown_strict+simple_tables+multiline_tables+grid_tables+pipe_tables+table_captions+fenced_code_blocks+line_blocks+definition_lists+all_symbols_escapable+strikeout+superscript+subscript+lists_without_preceding_blankline+implicit_figures+raw_tex+citations+tex_math_dollars+header_attributes+auto_identifiers+startnum+footnotes+inline_notes+fenced_code_attributes+yaml_metadata_block --template={0}/scripts/template/{2}.tex --no-tex-ligatures --smart --normalize --latex-engine=xelatex --reference-docx={0}/scripts/ref-simple.docx {1} output.md;".format(current_path, variable_string, template)
        os.popen(pandoc_launch)
    elif file_type == "t":
        pandoc_launch = "cd {0}/scripts/staging; pandoc -o output.tex -f markdown_strict+simple_tables+multiline_tables+grid_tables+pipe_tables+table_captions+fenced_code_blocks+line_blocks+definition_lists+all_symbols_escapable+strikeout+superscript+subscript+lists_without_preceding_blankline+implicit_figures+raw_tex+citations+tex_math_dollars+header_attributes+auto_identifiers+startnum+footnotes+inline_notes+fenced_code_attributes+yaml_metadata_block -t latex --template={0}/scripts/template/{2}.tex --no-tex-ligatures --smart --normalize --listings --latex-engine=xelatex {1} --bibliography=refs.bib --csl=gost.csl output.md;".format(current_path, variable_string, template)
        os.popen(pandoc_launch)

def get_version_counter():
    #TODO: rework with using config settings
    cmd_version_counter = "cd {0}; git rev-list --count master".format(current_path)
    process = subprocess.Popen(cmd_version_counter, stdout=subprocess.PIPE, stderr=None, shell=True)
    version_counter = '1.' + process.communicate()[0].replace("\n", "")
    return version_counter

current_path = sys.argv[1]
user_input = sys.argv[2]
search_dir = os.path.join(current_path,'sources')
fn = "output.md"
combine_files(dir_list(search_dir, True, 'md'), fn)

try:
    str_list = inc.process_file(current_path + '/scripts/staging/' + fn)
    inc.write_lines_to_file(str_list)
except:
    pass
pandoc_params, template = config_handler()
run_pandoc(user_input, pandoc_params, template)
login, passw, dest, title = my_mail.email_fields_from_config()
if len(login) > 0:
    output = current_path + '/scripts/staging/output.pdf'
    my_mail.send_email(login, passw, dest, title, output)

#TODO: Automatic seqdiag generation
#TODO: pipeline of handlers
#TODO: regexps for smooth typography
#TODO: regexps for trailing spaces
#TODO: drag out latex specific handlers like  \begin and \end