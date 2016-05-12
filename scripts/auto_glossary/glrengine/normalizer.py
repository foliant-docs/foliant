# -*- coding: utf-8 -*-
import pymorphy2


class GLRNormalizer(object):
    TAG_MAPPER = {
        "NOUN": "noun",
        "ADJF": "adj",
        "ADJS": "adj",
        "COMP": "adj",
        "VERB": "verb",
        "INFN": "verb",
        "PRTF": "pr",
        "PRTS": "pr",
        "GRND": "dpr",
        "NUMR": "num",
        "ADVB": "adv",
        "NPRO": "pnoun",
        "PRED": "adv",
        "PREP": "prep",
        "CONJ": "conj",
        "PRCL": "prcl",
        "INTJ": "noun",
        "LATN": "lat",
        "NUMB": "num"
    }

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def __call__(self, tokens):
        results = []
        for token in tokens:
            tokname, tokvalue, tokpos = token
            orig_tokvalue = tokvalue
            tokparams = []
            if tokname == "word":
                morphed = self.morph.parse(tokvalue)
                if morphed:
                    tokvalue = morphed[0].normal_form
                    tokname = self.TAG_MAPPER.get(morphed[0].tag.POS) or tokname
                    # tokparams = unicode(morphed[0].tag).lower().split(",")
                    tokparams = morphed[0].tag
                    # print tokname, tokvalue, tokpos, tokparams, orig_tokvalue
            results.append((tokname, tokvalue, tokpos, tokparams, orig_tokvalue))
        return results

    def normal(self, word):
        morphed = self.morph.parse(word)
        if morphed:
            return morphed[0].normal_form
        return word

    def parse_tags(self, word):
        parsed = self.morph.parse(word)
        if not parsed:
            return None
        return parsed[0].tag

morph_parser = GLRNormalizer()


