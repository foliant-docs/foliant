# -*- coding: utf-8 -*-
from itertools import ifilter, imap


def expand_item(item, R):
    rule = R[item[0]]
    return rule[1], item[1], rule[0]


def expand_itemset(itemset, R):
    return imap(lambda x: expand_item(x, R), itemset)


def expand_itemset2(itemset, R):
    for item in itemset:
        rule = R[item[0]]
        yield item[0], rule[1], item[1], rule[0]


def itemstr(item, R):
    e, i, n = expand_item(item, R)
    return ("[%s -> %s . %s" % (n, ' '.join(e[:i]), ' '.join(e[i:]))).strip() + ']'


def itemsetstr(itemset, R, label=''):
    items = map(lambda x: itemstr(x, R), sorted(itemset))
    width = reduce(lambda a, b: max(a, len(b)), items, 3)
    label = label and '[' + unicode(label) + ']' or ''
    build = ["+-%s%s-+" % (label, '-' * (width - len(label)))]
    build.extend("| %-*s |" % (width, item) for item in items)
    build.append("+-" + "-" * width + '-+')
    return '\n'.join(build)


def first(itemset, R):
    """
        Set of the tokens at the right of each dot in this item set
    """
    ret = set()
    for ruleelems, i, rulename in expand_itemset(itemset, R):
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if not e in R:
            ret.add(e)
    return ret


def follow(itemset, R):
    """
        All transitions from an item set in a dictionary [token]->item set
    """
    ret = dict()
    for ruleidx, ruleelems, i, rulename in expand_itemset2(itemset, R):
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if e not in ret:
            ret[e] = set()
        ret[e].update(closure([(ruleidx, i + 1)], R))
    return ret


def closure(itemset, R):
    """
        The epsilon-closure of this item set
    """
    C = set(itemset)
    last = -1
    visited = set()
    while len(C) != last:
        last = len(C)
        Ctmp = set()
        for item in C:
            r, i = item
            name, elems, commit = R[r]
            #elems, i, name = expand_item(item, R)
            if i == len(elems):
                continue
            if elems[i] in R and elems[i] not in visited:
                visited.add(elems[i])
                for r in R[elems[i]]:
                    Ctmp.add((r, 0))
                #Ctmp.update((r, 0) for r in R[elems[i]])
        C.update(Ctmp)
    return C


def kernel(itemset):
    """
        The kernel items in this item set
    """
    return set(ifilter(lambda (r, i): not r or i, itemset))
