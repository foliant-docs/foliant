"""
This module is for processing included content in md-files
"""
# -*- coding: utf-8 -*

import json
import sys
import os
import re
from subprocess import call
import gitlab

current_path = sys.argv[1]

include_pattern = re.compile(
    r'{{(?P<git_group>git:)?(?P<path_group>.[^:]+)(:"?(?P<start_head>.[^"-#]+)"?(-"?(?P<end_head>.[^"-#]+)"?)?(#(?P<level>[0-6]))?)?}}')

git_url_prefix = "gitlab.com"
git_path = ""


def git_ref_from_config():
    """
    checks if there is git reference to the project in config file
    :return: tuple of git credentials: git_project - name git project, git_branch, git_private_token - for authentication
    """
    c = open('config.json')
    config = json.load(c)
    c.close()
    git_project = config['git_project']
    if '/' in git_project:
        git_project = git_project.replace('/', '%2F')
    git_branch = config['git_branch']
    git_private_token = config['git_private_token']
    return git_project, git_branch, git_private_token


git_project, git_branch, git_private_token = git_ref_from_config()


def file_to_str_lst(file_name):
    """
    converts contents of file to list of strings, if input is already a list, the object is passed for further processing
    :param file_name: list of strings or file name
    :return: list of strings
    """
    if isinstance(file_name, list):
        return file_name
    else:
        try:
            f = open(file_name, 'r')
            file_as_str_lst = f.readlines()
            f.close()
        except:
            new_list = []
            file_as_str_lst = file_name.split('\n\n')
            for line in file_as_str_lst:
                line += '\n\n'
                new_list.append(line)
            file_as_str_lst = new_list
    return file_as_str_lst


def git_recursive_search(git_tree, file_name):
    """
    recursively finds needed file in gitlab project
    :param git_tree: a tree of git repo
    :param file_name: file to be found
    :return: path to the needed file in gitlab project
    """
    git = gitlab.Gitlab(git_url_prefix, token=git_private_token)
    git_dir_list = []
    git_repo_dict = git.getrepositorytree(git_project, ref_name=git_branch, path=git_tree)
    for git_dir in git_repo_dict:
        if git_dir['type'] == 'tree':
            git_dir_list.append(str(git_dir['name']))
        if git_dir['type'] != 'tree':
            if git_dir['name'] == file_name:
                return git_tree
    for git_dir in git_dir_list:
        if len(git_tree) == 0:
            new_path = git_dir
        else:
            new_path = git_tree + '/' + git_dir
        result = git_recursive_search(new_path, file_name)
        if result:
            return result


def get_pic_from_git(file_str):
    """
    recursively finds a picture in gitlab project and downloads it into /scripts/staging
    :param file_str: git temporary file as list of strings
    """
    git = gitlab.Gitlab(git_url_prefix, token=git_private_token)
    pic_pattern = re.compile('!\[.*[^\]]\]\((?P<pic_name>.*[^\)])\)')
    if isinstance(file_str, list):
        temp_str = ''
        for line in file_str:
            temp_str += line
        file_str = temp_str
    found = pic_pattern.findall(file_str)
    for pic in found:
        git_path = ""
        git_path = git_recursive_search(git_path, pic) + '/' + pic
        image = git.getfile(git_project, git_path, git_branch)
        content = image['content']
        img = open(current_path + '/scripts/staging/' + pic, 'wb')
        img.write(content.decode('base64'))
        img.close()


def content_by_heading(include_file_name, heading):
    """
    reads file to be included and extracts only the content starting with the given heading
    :param include_file_name: name of included file
    :param heading: starting point of the include
    :return: list of strings
    """
    needed_content = []
    heading += '\n'
    heading_found = None
    chapter_level = None
    f = file_to_str_lst(include_file_name)
    for line in f:
        if chapter_level is not None and ('#' * chapter_level) in line:
            check_include = line.count('#')
            if check_include <= chapter_level:
                break
        if heading_found is None:
            if heading in line:
                heading_found = True
                chapter_level = line.count('#')
        if heading_found is True:
            needed_content.append(line)
    return needed_content


def content_between_headings(include_file_name, h1, h2):
    """
    reads file to be included and extracts only the content starting with the first heading
    and up to the second one
    :param include_file_name: name of included file
    :param h1: starting point of the include
    :param h2: ending point of the include
    :return: list of strings
    """
    needed_content = []
    h1 += '\n'
    h2 += '\n'
    heading_start = None
    f = file_to_str_lst(include_file_name)
    for line in f:
        if h1 in line:
            heading_start = True
        if h2 in line:
            break
        if heading_start == True:
            needed_content.append(line)
    return needed_content


def set_heading_level(list_of_str, needed_level):
    """
    reads list of strings to be included and sets needed chapter levels
    taking into account the embedded structure
    :param list_of_str: list of strings from file
    :param needed_level: chapter level for setting as a string
    :return: list of strings
    """
    needed_level = int(needed_level)
    changed_headings = []
    first_found = None
    heading_pattern = re.compile('(?P<lev>^#{1,5})\s(?P<head_name>.*)')
    for line in list_of_str:
        found = heading_pattern.search(line)
        if found:
            if first_found is None:
                first_current_level = len(found.group('lev'))
                first_found = True
            if first_found is True:
                if first_current_level < needed_level:
                    gap = needed_level - first_current_level
                    current_level = len(found.group('lev'))
                    new_level = '#' * (current_level + gap)
                    heading_name = found.group('head_name')
                    line = '{0} {1}\n'.format(new_level, heading_name)
                elif first_current_level > needed_level:
                    gap = first_current_level - needed_level
                    current_level = len(found.group('lev'))
                    new_level = '#' * (current_level - gap)
                    heading_name = found.group('head_name')
                    line = '{0} {1}\n'.format(new_level, heading_name)
        changed_headings.append(line)
    return changed_headings


def process_headings(start_heading, end_heading, include_level, include_file_test):
    """
    processes headings of the included file if needed and writes changed content into a new file
    :param start_heading: string
    :param end_heading: string
    :param include_level: string
    :param include_file_test: included file name
    :return: new list of strings
    """
    new_list_of_str = []
    if start_heading and not end_heading and not include_level:
        new_list_of_str = content_by_heading(include_file_test, start_heading)

    elif start_heading and end_heading and not include_level:
        new_list_of_str = content_between_headings(include_file_test, start_heading, end_heading)

    elif start_heading and not end_heading and include_level:
        list_of_str = content_by_heading(include_file_test, start_heading)
        new_list_of_str = set_heading_level(list_of_str, include_level)

    elif start_heading and end_heading and include_level:
        list_of_str = content_between_headings(include_file_test, start_heading, end_heading)
        new_list_of_str = set_heading_level(list_of_str, include_level)

    if len(new_list_of_str) > 0:
        return new_list_of_str


def process_file(file_name):
    """
    finds included content by include_pattern and recursively processes it depending on the match found
    :param file_name: name of file with possibly included content
    :return: list of strings with included content
    """
    global git_path
    git_unabled = None
    str_list = []
    f = file_to_str_lst(file_name)
    for line in f:
        start_heading = None
        end_heading = None
        include_level = None
        found = include_pattern.search(line)
        if found:
            if found.group('git_group'):
                git_unabled = True
            if found.group('start_head'):
                start_heading = found.group('start_head')
            if found.group('end_head'):
                end_heading = found.group('end_head')
            if found.group('level'):
                include_level = found.group('level')
            if found.group('path_group'):
                include_file_name = found.group('path_group')
                if '.' not in include_file_name:
                    include_file_name += '.md'
                if '*' not in include_file_name:
                    # non-recursive search
                    include_file_test = include_file_name
                    if git_unabled is None:
                        # local search
                        if os.path.isfile(include_file_test):
                            changed = process_headings(start_heading, end_heading, include_level, include_file_test)
                        try:
                            new_str = process_file(changed)
                        except:
                            new_str = process_file(include_file_test)
                        str_list.extend(new_str)
                    if git_unabled:
                        # git-repo search
                        git_path = include_file_name
                        git = gitlab.Gitlab(git_url_prefix, token=git_private_token)
                        str_from_git = git.getrawfile(git_project, git_branch, git_path)
                        changed = process_headings(start_heading, end_heading, include_level, str_from_git)
                        if changed:
                            get_pic_from_git(changed)
                        else:
                            get_pic_from_git(str_from_git)
                        try:
                            new_str = process_file(changed)
                        except:
                            new_str = process_file(str_from_git)
                        str_list.extend(new_str)
                else:
                    if git_unabled is None:
                        # recursive local search
                        include_file_name = include_file_name[1:]
                        walk_dir = os.getcwd()
                        for root, subdirs, files in os.walk(walk_dir):
                            include_file_test = os.path.join(root, include_file_name)
                            if os.path.isfile(include_file_test):
                                changed = process_headings(start_heading, end_heading, include_level, include_file_test)
                                try:
                                    new_str = process_file(changed)
                                except:
                                    new_str = process_file(include_file_test)
                                str_list.extend(new_str)
                    if git_unabled:
                        git = gitlab.Gitlab(git_url_prefix, token=git_private_token)
                        include_file_name = include_file_name[1:]
                        file_location = git_recursive_search(git_path, include_file_name)
                        if not file_location:
                            continue
                        git_path = file_location + '/' + include_file_name
                        if git_path[0] == '/':
                            git_path = git_path[1:]
                        str_from_git = git.getrawfile(git_project, git_branch, git_path)
                        changed = process_headings(start_heading, end_heading, include_level, str_from_git)
                        if changed:
                            get_pic_from_git(changed)
                        else:
                            get_pic_from_git(str_from_git)
                        try:
                            new_str = process_file(changed)
                        except:
                            new_str = process_file(str_from_git)
                        str_list.extend(new_str)
        else:
            str_list.append(line)

    if not str_list[len(str_list) - 1].endswith('\n\n'):
        str_list.append('\n')

    return str_list


def write_lines_to_file(str_list):
    """
    writes the processed lines into the final md-file
    :param str_list: list of already processed strings
    """
    new_md = open(current_path + '/scripts/staging/output.md', 'w')
    for line in str_list:
        new_md.write(str(line))
    new_md.close()