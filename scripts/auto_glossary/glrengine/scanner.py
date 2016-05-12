# -*- coding: utf-8 -*-
import re
from itertools import chain


def token_line_col(text, tok):
    """
        Converts the token offset into (line, column) position.
        First character is at position (1, 1).
    """
    line = text.count('\n', 0, tok[2]) + 1
    offset = text.rfind('\n', 0, tok[2])
    if offset == -1:
        column = tok[2] + 1
    else:
        column = tok[2] - offset
    return line, column

check_groups = re.compile('[(][?]P=(\w+)[)]')


class GLRScanner(object):
    def __init__(self, **tokens):
        self.re = re.compile('', re.M | re.U | re.I)
        self.tokens = {}
        self.state_enter = {}
        self.state_leave = {}
        self.state_discard = {None: {'discard_names': set(),
                                     'discard_values': set()}}
        #self.discard_names = set()
        #self.discard_values = set()
        self.add(**tokens)

    def add(self, **tokens):
        """
            Each named keyword is a token type and its value is the
            corresponding regular expression. Returns a function that iterates
            tokens in the form (type, value) over a string.

            Special keywords are discard_names and discard_values, which specify
            lists (actually any iterable is accepted) containing tokens names or
            values that must be discarded from the scanner output.
        """
        for d in ('discard_values', 'discard_names'):
            if d in tokens:
                for s in self.state_discard:
                    self.state_discard[s][d].update(tokens[d])
                del tokens[d]

        # Check there is no undefined group in an assertion
        for k, v in tokens.iteritems():
            bad_groups = filter(lambda g: g not in tokens,
                                check_groups.findall(v))
            if bad_groups:
                print "Unknown groups", bad_groups
        pattern_gen = ('(?P<%s>%s)' % (k, v) for k, v in tokens.iteritems())
        if self.re.pattern:
            pattern_gen = chain((self.re.pattern,), pattern_gen)
        self.re = re.compile('|'.join(pattern_gen), re.M | re.U | re.I)
        self.tokens.update(tokens)
        return self

    def state(self, state_name, enter_tokens, leave_tokens, **discard):
        for tok in enter_tokens:
            self.state_enter[tok] = state_name
        for tok in leave_tokens:
            self.state_leave[tok] = state_name
        self.state_discard[state_name] = {
            'discard_names': set(),
            'discard_values': set()
        }
        for d in ('discard_values', 'discard_names'):
            if d in discard:
                self.state_discard[state_name][d].update(discard[d])
            self.state_discard[state_name][d].update(self.state_discard[None][d])
        return self

    def must_publish_token(self, state, tokname, tokvalue):
        return (tokname not in self.state_discard[state]['discard_names']
                and
                tokvalue not in self.state_discard[state]['discard_values'])

    def __call__(self, text):
        """
            Iteratively scans through text and yield each token
        """
        pos = 0
        states = [None]
        while True:
            m = self.re.match(text, pos)
            if not m:
                break

            pos = m.end()
            tokname = m.lastgroup

            try:
                tokvalue = m.group(tokname)
            except IndexError, ie:
                print "No such group", tokname

            tokpos = m.start()
            if tokname in self.state_leave and states[-1] == self.state_leave[tokname]:
                states.pop()

            if tokname in self.state_enter:
                states.append(self.state_enter[tokname])

            if self.must_publish_token(states[-1], tokname, tokvalue):
                yield tokname, tokvalue, tokpos

        if pos != len(text):
            msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (pos, len(text), text, text[pos:pos + 3])
            print msg
            raise ScannerException(msg)


def make_scanner(**tokens):
    return GLRScanner(**tokens)


class ScannerException(Exception):
    pass
