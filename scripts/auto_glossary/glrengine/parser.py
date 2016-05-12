# -*- coding: utf-8 -*-
from collections import defaultdict
from itertools import izip, chain
from scanner import make_scanner
from lr import *

lr_grammar_scanner = make_scanner(
    sep='=',
    alt='[|]',
    word=r"\b\w+\b",
    raw=r"\'\w+?\'",
    whitespace=r'[ \t\r\n]+',
    minus=r'[-]',
    label=r'\<.+?\>',
    discard_names=('whitespace',)
)


def make_rules(start, grammar, kw):
    words = [start]
    labels = []
    edit_rule = '@'
    edit_rule_commit = True
    next_edit_rule_commit = True
    kw.add(edit_rule)
    for tokname, tokvalue, tokpos in lr_grammar_scanner(grammar):
        if tokname == 'minus':
            next_edit_rule_commit = False
        if tokname == 'word' or tokname == 'raw':
            words.append(tokvalue)
            labels.append(None)
            kw.add(tokvalue)
        elif tokname == 'alt':
            yield (edit_rule, tuple(words), edit_rule_commit, labels[1:-1])
            words = []
            labels = []
        elif tokname == 'sep':
            tmp = words.pop()
            yield (edit_rule, tuple(words), edit_rule_commit, labels[1:-1])
            edit_rule_commit = next_edit_rule_commit
            next_edit_rule_commit = True
            edit_rule = tmp
            words = []
            labels = [None]
        elif tokname == 'label':
            # "a=b, b=c, d" -> {"a": "b", "b": "c", "d": None}
            tokvalue = tokvalue.strip().replace(" ", "")
            label = defaultdict(list)
            for l in tokvalue[1:-1].split(","):
                key, value = tuple(l.split("=", 1) + [None])[:2]
                label[key].append(value)
            # label = dict([tuple(l.split("=", 1) + [None])[:2] for l in tokvalue[1:-1].split(",")])
            labels[-1] = label
    yield (edit_rule, tuple(words), edit_rule_commit, labels[1:-1])


class RuleSet(dict):
    def __init__(self, rules):
        dict.__init__(self)
        self.names_count = 0
        self.rules_count = 0
        self.labels = {}
        self.init(rules)

    def init(self, rules):
        epsilons = self.fill(rules)
        must_cleanup = False
        while epsilons:
            eps = epsilons.pop()
            if eps in self:
                # Rule produces something and has an epsilon alternative
                self.add_epsilon_free(eps, epsilons)
            else:
                must_cleanup |= self.remove_epsilon(eps, epsilons)
        if must_cleanup:
            rules = sorted(self[i] for i in xrange(self.rules_count) if self[i] is not None)
            epsilons = self.fill(rules)
            if epsilons:
                #print "D'oh ! I left epsilon rules in there !", epsilons
                raise Exception("There is a bug ! There is a bug ! " +
                                "Failed to refactor this grammar into " +
                                "an epsilon-free one !")

    def fill(self, rules):
        self.names_count = 0
        self.rules_count = 0
        self.clear()
        epsilons = set()
        for rulename, elems, commit, labels in rules:
            if len(elems) > 0:
                self.add(rulename, elems, commit, labels)
            else:
                epsilons.add(rulename)
        #print 'found epsilon rules', epsilons
        return epsilons

    def add(self, rulename, elems, commit, labels):
        if rulename not in self:
            self.names_count += 1
            self[rulename] = set()
        rule = (rulename, elems, commit)
        if rule not in (self[i] for i in self[rulename]):
            self[rulename].add(self.rules_count)
            self[self.rules_count] = rule
            self.labels[self.rules_count] = labels
            self.rules_count += 1

    def add_epsilon_free(self, eps, epsilons):
        #print "Adding", eps, "-free variants"
        i = 0
        while i < self.rules_count:
            if self[i] is None:
                i += 1
                continue
            rulename, elems, commit = self[i]
            if eps in elems:
                #print "... to", rulename, elems
                E = set([elems])
                old = 0
                while len(E) != old:
                    old = len(E)
                    E = E.union(elems[:i] + elems[i + 1:]
                                for elems in E
                                for i in xrange(len(elems))
                                if elems[i] == eps)
                #print "Created variants", E
                for elems in E:
                    if len(elems) == 0:
                        #print "got new epsilon rule", rulename
                        epsilons.add(rulename)
                    else:
                        self.add(rulename, elems, commit, [])
                        #
                        #
            i += 1
            #

    def remove_epsilon(self, eps, epsilons):
        must_cleanup = False
        i = 0
        while i < self.rules_count:
            if self[i] is None:
                i += 1
                continue
            rulename, elems, commit = self[i]
            if eps in elems:
                elems = tuple(e for e in elems if e != eps)
                if len(elems) == 0:
                    # yet another epsilon :/
                    self[i] = None
                    self[rulename].remove(i)
                    if not self[rulename]:
                        del self[rulename]
                    must_cleanup = True
                    epsilons.add(rulename)
                    #print "epsilon removal created new epsilon rule", rulename
                else:
                    self[i] = (rulename, elems, commit)
                    #
            i += 1
        return must_cleanup


class Parser(object):
    def __init__(self, start_sym, grammar, scanner_kw=[]):
        self.kw_set = set(scanner_kw)
        self.kw_set.add('$')
        self.R = RuleSet(make_rules(start_sym, grammar, self.kw_set))
        self.I = set((r, i) for r in xrange(self.R.rules_count)
                     for i in xrange(len(self.R[r][1]) + 1))
        self.precompute_next_items()
        self.compute_lr0()
        self.LR0 = list(sorted(self.LR0))
        self.LR0_idx = {}
        for i, s in enumerate(self.LR0):
            self.LR0_idx[s] = i
        self.initial_state = self.index(self.initial_items)
        self.compute_ACTION()

    def __str__(self):
        return '\n'.join(self.R[r][0] + ' = ' + ' '.join(self.R[r][1])
                         for r in xrange(self.R.rules_count))

    def conflicts(self):
        "Returns the list of conflicts in the ACTION table."
        return filter(lambda (i, t): len(self.ACTION[i][t]) > 1,
                      ((i, t) for i, row in enumerate(self.ACTION)
                       for t in row.iterkeys()))

    def count_conflicts(self):
        "Returns the count of conflicts in the ACTION table."
        return reduce(lambda a, b: a + (len(b) > 1 and 1 or 0),
                      (a for row in self.ACTION for a in row.itervalues()),
                      0)

    def resolve_SR_conflicts(self, favor='S'):
        for s, k in self.conflicts():
            actions = self.ACTION[s][k]
            atypes = [a[0] for a in actions]
            if 'S' in atypes and 'R' in atypes:
                self.ACTION[s][k] = [a for a in actions if a[0] == favor]

    def compute_lr0(self):
        """
            Compute the LR(0) sets.
        """
        self.LR0 = set()
        x = closure([(0, 0)], self.R)
        self.initial_items = x
        stack = [tuple(sorted(x))]
        while stack:
            x = stack.pop()
            self.LR0.add(x)
            F = follow(x, self.R)
            for t, s in F.iteritems():
                s = tuple(sorted(s))
                if s not in self.LR0:
                    stack.append(s)

    def itemstr(self, item):
        """
            Stringify an item for pretty-print.
        """
        return itemstr(item, self.R)

    def itemsetstr(self, item, label=''):
        """
            Stringify an item set for pretty-print.
        """
        return itemsetstr(item, self.R, label)

    def closure(self, s):
        """
            Compute the closure of an item set.
        """
        return tuple(sorted(closure(s, self.R)))

    def kernel(self, s):
        """
            Compute the kernel of an item set.
        """
        return kernel(s)

    def index(self, s):
        """
            Returns the index of (the closure of) item set s in the LR(0) sets list.
        """
        return self.LR0_idx[self.closure(s)]

    def compute_GOTO(self):
        """
            Compute the GOTO table.
        """
        self.GOTO = []
        for s in self.LR0:
            f = {}
            for tok, dest in follow(s, self.R).iteritems():
                f[tok] = self.LR0_idx[self.closure(dest)]
            self.GOTO.append(f)

    def init_row(self, init=None):
        """
            Initialize a row of the ACTION table.
        """
        if init is None:
            init = []
        ret = {}
        for kw in self.kw_set:
            ret[kw] = [] + init
        return ret

    def precompute_next_items(self):
        self.next_list = dict((k, set()) for k in self.R if type(k) is str or type(k) is unicode)
        for item in self.I:
            r, i = item
            n, e, c = self.R[r]
            if i > 0 and e[i - 1] in self.next_list:
                self.next_list[e[i - 1]].add(item)

    def next_items(self, item, visited=None):
        """
            Compute the yet unvisited items following the given item.
        """
        items = set()
        if visited is None:
            visited = set()
        name = self.R[item[0]][0]
        for it in self.next_list[name]:
            if it not in visited:
                r, i = it
                e = self.R[r][1]
                visited.add(it)
                if len(e) == i:
                    items.update(self.next_items(it, visited))
                else:
                    items.add(it)
        return items

    def following_tokens(self, item):
        """
            Returns all tokens following the current item.
        """
        items = self.next_items(item)
        ret = first(closure(items, self.R), self.R)
        ret.add('$')
        return ret

    def compute_ACTION(self):
        """
            Compute the ACTION/GOTO table.
        """
        self.compute_GOTO()
        self.ACTION = []
        for s, g in izip(self.LR0, self.GOTO):
            action = self.init_row()

            # свертки
            for r, i in ifilter(lambda (r, i): i == len(self.R[r][1]), s):
                if not r:
                    action['$'].append(('A',))
                else:
                    for kw in self.following_tokens((r, i)):
                        action[kw].append(('R', r))

            # переносы
            for tok, dest in g.iteritems():
                action[tok].append(('S', dest))

            # commit
            self.ACTION.append(action)

    def action_to_str(self):
        """
            Stringify the ACTION/GOTO table for pretty-print.
        """

        def ac_str(c):
            return ''.join(imap(unicode, c))

        def cell(i, kw):
            if i >= 0:
                return ','.join(map(ac_str, self.ACTION[i][kw]))
            if i < 0:
                return kw != '@' and str(kw) or ''

        def col_width(kw):
            return reduce(max, chain([(type(kw) is str or type(kw) is unicode) and len(kw) or kw],
                                     (len(cell(i, kw))
                                      for i in xrange(len(self.ACTION)))))

        col_labels = sorted(self.kw_set,
                            key=lambda x: x in self.R and '|' + x
                                          or x == '$' and '|$'
                            or x)
        col_widths = [kw != '@' and col_width(kw) or 0 for kw in col_labels]

        def row(i):
            return ' | '.join(cell(i, kw).center(cw)
                              for kw, cw in izip(col_labels, col_widths))

        header = '    | ' + row(-1) + '\n'
        return header + '\n'.join(('%3i | ' % i) + row(i)
                                  for i in xrange(len(self.ACTION)))

    def dump_sets(self):
        """
            Pretty-print all LR(0) item sets.
        """
        for i, lrset in enumerate(self.LR0):
            print self.itemsetstr(lrset, i)
            print

    def itemset(self, i):
        return self.itemsetstr(self.LR0[i], i)

    @property
    def unused_rules(self):
        check = lambda i: reduce(lambda a, b: a and i not in b, self.LR0, True)
        unused_rule_indices = set(x[0] for x in filter(check, self.I))
        return set(self.R[x][0] for x in unused_rule_indices)
