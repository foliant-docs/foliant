# -*- coding: utf-8 -*

import requests
import io
import json
import sys

current_path = sys.argv[1]

testrail_url = 'testrails.restr.im'

letters = [u'А', u'Б', u'В', u'Г', u'Д', u'Е', u'И', u'К', u'Л', u'М', u'Н', u'О', u'П', u'Р']


def fields_from_config():
    c = open(current_path + '/scripts/testrail_config.json')
    config = json.load(c)
    c.close()
    for key in config:
        if key == 'device':
            device = config[key]
        if key == 'version':
            version = config[key]
        if key == 'project':
            project = config[key]
        if key == 'suite':
            suite = config[key]
        if key == 'login':
            login = config[key]
        if key == 'pass':
            passw = config[key]
    return device, version, project, suite, login, passw


device, version, project, suite, login, passw = fields_from_config()

if project or suite or login or passw == '':
    quit()

obj = io.open(current_path + '/sources/object.md', 'w', encoding='utf-8')
obj.write(u'# Объект испытаний\n\n')
obj.write(
    u'Объектом испытаний является приложение «Интерактивное ТВ» для телевизоров {0:s}, поддерживающих технологию Smart TV.\n\n'.format(
        device))
obj.close()

ver = io.open(current_path + '/sources/version.md', 'w', encoding='utf-8')
ver.write(u'## Версия объекта испытаний\n\n')
ver.write(u'В ходе испытаний используется версия приложения {0:s}.\n\n'.format(version))
ver.close()

f = open(current_path + '/sources/test_cases.md', 'w')
f.write('# Программа испытаний\n\n')
f.close

f2 = io.open(current_path + '/sources/addendum.textile', 'w', encoding='utf-8')
f2.write(u'**Протокол испытаний**\n\n')
f2.write(u'**Приложение «Интерактивное ТВ» для телевизоров {0:s}**\n\n'.format(device))
f2.write(u'**Версия приложения {0:s}**\n\n'.format(version))
f2.write(u'|_. № теста|_. Название|_. Статус|_. Замечания|\n')
f2.close()

f = io.open(current_path + '/sources/test_cases.md', 'a', encoding='utf-8')  # щепотка черной магии
f.close


def get_sections(prj, suite, login, passw):
    sec_list = []
    url = 'http://{0}//index.php?/api/v2/get_sections/{1}&suite_id={2}'.format(testrail_url, str(prj), str(suite))
    response = requests.get(url, auth=(login, passw), headers={'content-type': 'application/json'})
    response = response.json()
    for sec in response:
        sec_dict = {}
        sec_dict['sec_id'] = sec['id']
        sec_dict['sec_name'] = sec['name']
        sec_list.append(sec_dict)
    return sec_list


def get_cases(prj, suite, sec_list, login, passw):
    all_cases = []
    for sec in sec_list:
        section = sec['sec_id']
        url = 'http://{0}//index.php?/api/v2/get_cases/{1}&suite_id={2}&section_id={3}'.format(testrail_url, str(prj),
                                                                                               str(
                                                                                                   suite), str(section))
        response = requests.get(url, auth=(login, passw), headers={'content-type': 'application/json'})
        response = response.json()
        all_cases.append(response)
    return all_cases


def get_case(case_id, sec_list, login, passw):
    global flag
    global letter_id
    global num
    global letter

    url = 'http://{0}//index.php?/api/v2/get_case/{1}'.format(testrail_url, str(case_id))
    response = requests.get(url, auth=(login, passw), headers={'content-type': 'application/json'})
    response = response.json()
    tag = response['custom_tp']
    f = io.open(current_path + '/sources/test_cases.md', 'a', encoding='utf-8')
    if tag:
        f2 = io.open(current_path + '/sources/addendum.textile', 'a', encoding='utf-8')
        section = response['section_id']
        for sec in sec_list:
            if sec['sec_id'] == section:
                if flag == 0:
                    letter = letters[letter_id]
                    sec_name = sec['sec_name'] + u' (' + letter + u')'
                    f.write(u'## {0:s}\n\n'.format(sec_name))
                    f2.write(u'|{0:s}|'.format(letter))
                    f2.write(u'{0:s}|||\n'.format(sec['sec_name']))
                    flag = 1
                    letter_id += 1
                title = response['title']
                precondition = response['custom_preconds']
                steps = response['custom_steps']
                expected = response['custom_expected']
                steps_separated = response[
                    'custom_steps_separated']  # list with dicts with two keys "content", "expected"

                title_with_num = title + u' (' + letter + u'%d' % num + u')'
                f.write(u'### {0:s}\n\n'.format(title_with_num))
                f2.write(u'|{0:s}'.format(letter))
                f2.write(u'{0:s}|'.format(num))
                f2.write(u'{0:s}|||\n'.format(title))
                num += 1
                if precondition:
                    f.write(u'**Предусловие**\n\n')
                    f.write(u'{0:s}\n\n'.format(precondition))
                f.write(u'**Сценарий**\n\n')
                if steps_separated:
                    for field in range(len(steps_separated)):
                        steps_detail = steps_separated[field]['content']
                        expected_detail = steps_separated[field]['expected']
                        f.write(u'{0:s}\n\n'.format(steps_detail))
                        if field == (len(steps_separated) - 1):
                            f.write(u'**Ожидаемый результат**\n\n{0:s}\n\n'.format(expected_detail))
                        else:
                            f.write(u'    *Промежуточный результат*: {0:s}\n\n'.format(expected_detail))

                else:
                    f.write(u'{0:s}\n\n'.format(steps))
                    f.write(u'**Ожидаемый результат**\n\n{0:s}\n\n'.format(expected))

                f.close()
                f2.close()


sec_list = get_sections(project, suite, login, passw)
sec_cases = get_cases(project, suite, sec_list, login, passw)
letter_id = 0
for sec in sec_cases:
    num = 1
    flag = 0
    for case in sec:
        get_case(case['id'], sec_list, login, passw)

f2 = io.open(current_path + '/sources/addendum.textile', 'a', encoding='utf-8')
f2.close()
