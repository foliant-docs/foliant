# -*- coding: utf-8 -*-
import re


def gram_label(value, tokens, i):
    return value in tokens[i][3]


def reg_l_all_label(value, tokens, i):
    return tokens[i][4].islower()


def reg_h_first_label(value, tokens, i):
    return tokens[i][4].istitle()


def reg_h_all_label(value, tokens, i):
    return tokens[i][4].isupper()


def regex_label(value, tokens, i):
    return bool(re.match(value, tokens[i][4]))


def agr_gnc_label(value, tokens, i):
    one = tokens[i][3]
    another = tokens[i+int(value)][3]
    return (one.case == another.case or not one.case or not another.case) \
        and (one.gender == another.gender or not one.gender or not another.gender) \
        and (one.number == another.number or not one.number or not another.number)


def agr_nc_label(value, tokens, i):
    one = tokens[i][3]
    another = tokens[i+int(value)][3]

    return (one.case == another.case or not one.case or not another.case) \
        and (one.number == another.number or not one.number or not another.number)


def agr_c_label(value, tokens, i):
    one = tokens[i][3]
    another = tokens[i+int(value)][3]

    return one.case == another.case or not one.case or not another.case


def agr_gn_label(value, tokens, i):
    one = tokens[i][3]
    another = tokens[i+int(value)][3]

    return (one.gender == another.gender or not one.gender or not another.gender) \
        and (one.number == another.number or not one.number or not another.number)


def agr_gc_label(value, tokens, i):
    one = tokens[i][3]
    another = tokens[i+int(value)][3]

    return (one.gender == another.gender or not one.gender or not another.gender) \
        and (one.case == another.case or not one.case or not another.case)


LABELS_CHECK = {
    "gram": gram_label,
    "reg-l-all": reg_l_all_label,
    "reg-h-first": reg_h_first_label,
    "reg-h-all": reg_h_all_label,
    "agr-gnc": agr_gnc_label,
    "agr-nc": agr_nc_label,
    "agr-c": agr_c_label,
    "agr-gn": agr_gn_label,
    "agr-gc": agr_gc_label,
    "regex": regex_label
}