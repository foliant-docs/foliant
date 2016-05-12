# -*- coding: utf-8 -*-
from glrengine.normalizer import morph_parser
from glrengine.labels import LABELS_CHECK
from parser import Parser
from itertools import ifilter, chain
from stack import Stack
from scanner import token_line_col

INITIAL_TOKEN = ('#', '#', 0)


class GLRAutomaton(Parser):
    """
        A GLR parser.
    """

    def __init__(self, start_sym, grammar, scanner, dictionaries=None, debug=False):
        Parser.__init__(self, start_sym, grammar, scanner.tokens.keys())
        self.scanner = scanner
        self.dictionaries = dictionaries or {}
        self.results = []
        self.debug_mode = debug

    def __call__(self, text):
        return self.recognize(text, chain(self.scanner(text), [('$', '$', len(text))]))

    def recognize(self, text, token_stream):
        self.results = []
        tokens = morph_parser(token_stream)
        while True:
            stack = Stack(self)
            stack.shift(None, None, 0)
            stack.count_active = 1
            prev_tok = INITIAL_TOKEN
            labels_ok = True

            for token_num, token in enumerate(tokens):
                self.debug("\n\n\nNEW ITERATION. Token:", token[1])
                self.debug(token)
                if len(stack.active) == 0:
                    if not self.error_detected(text, tokens, prev_tok, stack.previously_active):
                        text, tokens = self.without_first_word(text, tokens)
                        break
                    else:
                        continue
                prev_tok = token

                # свертка
                for i, node in stack.enumerate_active():  # S.active may grow
                    state = node.data

                    # raw-слова в кавычках
                    raw_token = "'%s'" % token[1]
                    if raw_token in self.ACTION[state]:
                        for r, rule in ifilter(lambda x: x[0] == 'R', self.ACTION[state][raw_token]):
                            self.debug("- Reduce")
                            self.debug("-- Actions", self.ACTION[state][raw_token])
                            self.debug("-- Raw token", node, rule)
                            labels_ok = self.check_labels(tokens, self.R.labels[rule])
                            if not labels_ok:
                                break
                            stack.reduce(node, rule)

                    # обычные состояния
                    if labels_ok:
                        for r, rule in ifilter(lambda x: x[0] == 'R', self.ACTION[state][token[0]]):
                            self.debug("- Reduce")
                            self.debug("-- Actions", self.ACTION[state])
                            self.debug("-- Normal", node, rule)
                            labels_ok = self.check_labels(tokens, self.R.labels[rule])
                            if not labels_ok:
                                break
                            stack.reduce(node, rule)

                    # имитация конца предложения
                    if labels_ok:
                        for r, rule in ifilter(lambda x: x[0] == 'R', self.ACTION[state]["$"]):
                            self.debug("- Reduce")
                            self.debug("-- Actions", self.ACTION[state])
                            self.debug("-- EOS", node, rule)
                            labels_ok = self.check_labels(tokens, self.R.labels[rule])
                            if not labels_ok:
                                break
                            stack.reduce(node, rule)

                    self.debug("- STACK")
                    if self.debug_mode:
                        stack.dump()

                # последняя свертка не удовлетворила лейблам
                if not labels_ok:
                    self.debug("- Labels not OK")
                    text, tokens = self.without_first_word(text, tokens)
                    break

                # конец?
                if token[0] == '$':
                    acc = stack.accepts()
                    if acc:
                        self.results.append(text)
                        self.debug("- Found new result:", self.results)
                    else:
                        self.error_detected(text, tokens, token, stack.active)
                    return self.results

                # перенос
                stack.count_active = len(stack.active)
                for node in (stack.active[i] for i in xrange(len(stack.active))):
                    # из стека могут удаляться состояния, так что верхний длинный for правда оказался нужен
                    state = node.data

                    # raw-слова в кавычках
                    raw_token = "'%s'" % token[1]
                    if raw_token in self.ACTION[state]:
                        for r, state in ifilter(lambda x: x[0] == 'S',  self.ACTION[state][raw_token]):
                            self.debug("- Shift")
                            self.debug("-- Raw", node, token)
                            stack.shift(node, (token,), state)

                    # обычные состояния
                    for r, state in ifilter(lambda x: x[0] == 'S',  self.ACTION[state][token[0]]):
                        self.debug("- Shift")
                        self.debug("-- Normal", node, token)
                        stack.shift(node, (token,), state)

                    self.debug("- Stack:")
                    if self.debug_mode:
                        stack.dump()

                # слияние состояний
                stack.merge()

        return self.results

    def error_detected(self, text, tokens, cur_tok, last_states):
        line, column = token_line_col(text, cur_tok)

        lines = text.splitlines()
        if lines:
            if len(lines) > (line - 1):
                self.debug(lines[line - 1])
                self.debug('%s^' % (''.join(c == '\t' and '\t' or ' ' for c in lines[line - 1][:column - 1])))
            else:
                self.debug("at end of text")

        toks = set(kw for st in last_states for kw in self.kw_set
                       if len(self.ACTION[st.data][kw]) > 0
                          and kw not in self.R and kw != '$')

        if not toks:
            self.debug("Text", text)
            self.debug("-- Part", text[:cur_tok[2]])
            self.results.append(text[:cur_tok[2]])
            self.debug("- Found new result:", self.results)

        return False

    def check_labels(self, tokens, labels):
        self.debug("- Checking labels...", labels)
        for i in xrange(len(labels)):
            if labels[i]:
                for label_key, label_values in labels[i].iteritems():
                    for label_value in label_values:
                        self.debug("-- Check label:", label_key, label_value)
                        ok = LABELS_CHECK[label_key](label_value, tokens, i)
                        self.debug("--- ", ok)
                        if not ok:
                            return False
        return True

    def without_first_word(self, text, tokens):
        new_text = text[tokens[1][2]:]
        new_tokens = [(token[0], token[1], token[2] - tokens[1][2], token[3], token[4]) for token in tokens[1:]]
        return new_text, new_tokens

    def validate_ast(self, ast):
        return ast

    def debug(self, *args):
        if self.debug_mode:
            print " ".join(map(unicode, args))
