# -*- coding: utf-8 -*
import os
import os.path
import sys
import include_text as inc
import assembler as asmblr
import my_mail
import shutil

reload(sys)
sys.setdefaultencoding('utf-8')

current_path = sys.argv[1]
user_input = sys.argv[2]
search_dir = os.path.join(current_path, 'sources')
fn = 'output.md'
sources_delete_check = asmblr.combine_files(asmblr.dir_list(search_dir, True, 'md'), fn)

try:
    str_list = inc.process_file(current_path + '/scripts/staging/' + fn)
    inc.write_lines_to_file(str_list)
except:
    print 'No includes found in input files'

pandoc_params, template, file_title = asmblr.config_handler()
asmblr.run_pandoc(user_input, pandoc_params, template)

version_counter = asmblr.get_version_counter()
f_title = asmblr.move_output_file(user_input, file_title, version_counter)

if sources_delete_check:
    shutil.rmtree(current_path + '/sources')

if os.path.exists(current_path + '/scripts/keys.json'):
    login, passw, dest, title = my_mail.email_fields_from_config()
    if len(login) > 0:
        os.chdir(current_path)
        output = f_title
        my_mail.send_email(login, passw, dest, f_title, output)
