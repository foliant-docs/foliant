# -*- coding: utf-8 -*-
from glr import GLRParser
import re
import io
import os

input_doc = 'text.md'
dict_name = 'dict.md'

mdash = '—'.decode('utf-8')
gloss_name = ('## Глоссарий\n\n').decode('utf-8')

heading_pattern = re.compile('(^#{1,5}\s.*)')
key_pattern = (r'(.*) — (.*)')

def_dict = {}
all_dicts = []
terms = []

f = open(dict_name, 'r')
lines = f.readlines()
index = 0
for line in lines:

    found = heading_pattern.search(line)
    if found:
        section = found.group(0)

    key = re.match(key_pattern, line)
    if key:
        def_dict[str(index)] = unicode(key.group(2), 'utf-8')
        dict_ = {}
        dict_[u"TEXT"] = [unicode(key.group(1), "utf-8")]
        terms.append(key.group(1))
        parent_dict = {
            'dict': dict_,
            'index': str(index),
            'section': unicode(section, 'utf-8')
        }

        all_dicts.append(parent_dict)
        index += 1
f.close()

grammar = u"""
   S = TEXT
"""

def get_text(fname):
    global f, text, line
    file_as_str = ""
    f = open(fname, 'r')
    text = f.readlines()
    for line in text:
        file_as_str += line + ' '
    f.close()
    return unicode(file_as_str, 'utf-8')[1:]


if os.path.isfile('glossary.md'):
    os.remove('glossary.md')

f2 = io.open('glossary.md', 'a', encoding='utf-8')
f2.write(gloss_name)

sec_check = None

for d in all_dicts:
    if ' ' not in d['dict']['TEXT'][0]:
        glr = None
        text = None

        glr = GLRParser(grammar, dictionaries=d['dict'], debug=False)
        text = get_text(input_doc)
        result = glr.parse(text)
        if len(result) != 0:
            word = d['dict']['TEXT'][0]
            value = def_dict[d['index']]
            if d['section'] != sec_check:
                sec = d['section']
                sec_check = sec
                f2.write('%s\n\n%s\n:    %s %s\n\n' % (sec, word, mdash, value))
            else:
                f2.write('%s\n:    %s %s\n\n' % (word, mdash, value))
    else:
        text = get_text(input_doc).lower()
        key = (d['dict']['TEXT'][0]).lower()
        phrase = re.search(key, text)
        if phrase:
            word = d['dict']['TEXT'][0]
            value = def_dict[d['index']]
            if d['section'] != sec_check:
                sec = d['section']
                sec_check = sec
                f2.write('%s\n\n%s\n:    %s %s\n\n' % (sec, word, mdash, value))
            else:
                f2.write('%s\n:    %s %s\n\n' % (word, mdash, value))
            
f2.close()

"""
new_terms = []

for term in terms:
    new_term = unicode(term, 'utf-8')
    new_terms.append(new_term)

f4 = open('glossary.md', 'a')
f4.write('## Это нашел не парсер\n\n')
f4.close()

for term in new_terms:
    if term.lower() in (get_text(input_doc)).lower() and term.lower() not in (get_text('glossary.md')).lower():
        f3 = io.open('glossary.md', 'a', encoding='utf-8')
        f3.write('%s\n\n' % term)
        f3.close()
"""
