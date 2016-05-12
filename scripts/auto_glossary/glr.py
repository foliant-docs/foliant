# -*- coding: utf-8 -*-
__all__ = ["GLRParser"]

from glrengine import GLRScanner, GLRAutomaton, GLRSplitter, morph_parser


class GLRParser(object):
    DEFAULT_PARSER = {
        "word": r"[\w\d_-]+",
        "number": r"[\d]+",
        "space": r"[\s]+",
        "newline": r"[\n]+",
        "dot": r"[\.]+",
        "comma": r"[,]+",
        "colon": r"[:]+",
        "percent": r"[%]+",
        "quote": r"[\"\'«»`]+",
        "brace": r"[\(\)\{\}\[\]]+",
    }

    DEFAULT_PARSER_DISCARD_NAMES = ["space"]

    DEFAULT_GRAMMAR = """
        Word = word
        Word = noun
        Word = adj
        Word = verb
        Word = pr
        Word = dpr
        Word = num
        Word = adv
        Word = pnoun
        Word = prep
        Word = conj
        Word = prcl
        Word = lat
    """

    def __init__(self, grammar, root="S", dictionaries=None, parser=None, debug=False):
        grammar_rules = u"%s\n%s" % (grammar, self.DEFAULT_GRAMMAR)
        if dictionaries:
            # превращает {k: [a, b, c]} -> "k = 'a' | 'b' | 'c'"
            for dict_name, dict_words in dictionaries.items():
                morphed = []
                for word in dict_words:
                    morphed.append(morph_parser.normal(word))
                grammar_rules += u"\n%s = '%s'" % (dict_name, "' | '".join(morphed))

        if debug:
            print grammar_rules

        parser_rules = self.DEFAULT_PARSER
        parser_rules.update({"discard_names": self.DEFAULT_PARSER_DISCARD_NAMES})
        if parser:
            parser_rules.update(parser)

        self.splitter = GLRSplitter()
        self.scanner = GLRScanner(**parser_rules)
        self.glr = GLRAutomaton(
            start_sym=root,
            grammar=grammar_rules,
            scanner=self.scanner,
            debug=debug
        )

    def parse(self, text):
        result = []
        for sentence in self.splitter(text):
            result += self.glr(sentence)
        return result


# TODO:
# нормализация слов в кавычках
