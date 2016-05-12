# -*- coding: utf-8 -*-
import re


class GLRSplitter(object):
    split_re = re.compile(r"[!?;\.]+ ", re.M | re.U | re.I)

    def clear(self, text):
        # удалить все символы из текста, кроме тех, которые точно разберет парсер
        text = re.sub(ur'[^\w\d\s\-\n\.\(\)\{\}\[\]\"\'«»`%,:_]', " ", text, flags=re.M | re.U | re.I)
        return text

    def __call__(self, text):
        text = self.clear(text)
        return self.split_re.split(text)