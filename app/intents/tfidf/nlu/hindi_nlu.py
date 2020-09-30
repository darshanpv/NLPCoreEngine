# -*- coding: utf-8 -*-
import codecs
import re
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')


def rreplace(string, old, new, count=None):
    string_reverse = string[::-1]
    old_reverse = old[::-1]
    new_reverse = new[::-1]
    if count:
        final_reverse = string_reverse.replace(old_reverse, new_reverse, count)
    else:
        final_reverse = string_reverse.replace(old_reverse, new_reverse)
    result = final_reverse[::-1]
    return result


class Processor():
    def __init__(self, text=None):
        if text is not None:
            self.text = text
            self.clean_text()
        else:
            self.text = None
        self.sentences = []
        self.tokens = []
        self.stemmed_word = []
        self.final_list = []

    def read_from_file(self, filename):
        f = codecs.open(filename, encoding='utf-8')
        self.text = f.read()
        self.clean_text()

    def generate_sentences(self):
        text = self.text
        self.sentences = text.split(u"।")

    def print_sentences(self, sentences=None):
        if sentences:
            for i in sentences:
                print(i)
        else:
            for i in self.sentences:
                print(i)

    def clean_text(self):
        text = self.text
        text = re.sub(r'(\d+)', r'', text)
        text = text.replace(u',', '')
        text = text.replace(u'"', '')
        text = text.replace(u'(', '')
        text = text.replace(u')', '')
        text = text.replace(u'"', '')
        text = text.replace(u':', '')
        text = text.replace(u"'", '')
        text = text.replace(u"‘‘", '')
        text = text.replace(u"’’", '')
        text = text.replace(u"''", '')
        text = text.replace(u".", '')
        text = text.replace(u"?", '')
        self.text = text

    def remove_only_space_words(self):
        tokens = filter(lambda tok: tok.strip(), self.tokens)
        self.tokens = tokens

    def hyphenated_tokens(self):
        for each in self.tokens:
            if '-' in each:
                tok = each.split('-')
                self.tokens.remove(each)
                self.tokens.append(tok[0])
                self.tokens.append(tok[1])

    def tokenize(self):
        if not self.sentences:
            self.generate_sentences()
        sentences_list = self.sentences
        tokens = []
        for each in sentences_list:
            word_list = each.split(' ')
            for w in word_list:
                if (w != ''):
                    tokens.append(w)
        self.tokens = tokens

    def print_tokens(self, print_list=None):
        if print_list is None:
            for i in self.tokens:
                print(i)
        else:
            for i in print_list:
                print(i)

    def tokens_count(self):
        return len(list(self.tokens))

    def sentence_count(self):
        return len(self.sentences)

    def len_text(self):
        return len(self.text)

    def concordance(self, word):
        if not self.sentences:
            self.generate_sentences()
        sentence = self.sentences
        concordance_sent = []
        for each in sentence:
            if word in each:
                concordance_sent.append(each.decode('utf-8'))
        return concordance_sent

    def generate_freq_dict(self):
        freq = {}
        if not self.tokens:
            self.tokenize()
        temp_tokens = self.tokens
        for each in self.tokens:
            freq[each] = temp_tokens.count(each)
        return freq

    def print_freq_dict(self, freq):
        for i in freq.keys():
            print(i, ',', freq[i])

    def generate_stem_words(self, word):
        suffixes = {1: [u"ो", u"े", u"ू", u"ु", u"ी", u"ि", u"ा"],
                    2: [u"कर", u"ाओ", u"िए", u"ाई", u"ाए", u"ने", u"नी", u"ना", u"ते", u"ीं", u"ती", u"ता", u"ाँ",
                        u"ां", u"ों", u"ें"],
                    3: [u"ाकर", u"ाइए", u"ाईं", u"ाया", u"ेगी", u"ेगा", u"ोगी", u"ोगे", u"ाने", u"ाना", u"ाते", u"ाती",
                        u"ाता", u"तीं", u"ाओं", u"ाएं", u"ुओं", u"ुएं", u"ुआं"],
                    4: [u"ाएगी", u"ाएगा", u"ाओगी", u"ाओगे", u"एंगी", u"ेंगी", u"एंगे", u"ेंगे", u"ूंगी", u"ूंगा",
                        u"ातीं", u"नाओं", u"नाएं", u"ताओं", u"ताएं", u"ियाँ", u"ियों", u"ियां"],
                    5: [u"ाएंगी", u"ाएंगे", u"ाऊंगी", u"ाऊंगा", u"ाइयाँ", u"ाइयों", u"ाइयां"], }
        tag = [1, 2, 3, 4, 5]
        tag.reverse()
        dic_hi = {}
        for w in word.split():
            try:
                pass
            except:
                pass
            flag = 0
            for L in tag:
                if flag == 1:
                    break
                if len(w) > L + 1:
                    for suf in suffixes[L]:
                        if w.endswith(suf):
                            word1 = rreplace(w, suf, '', 1)
                            dic_hi[w] = word1
                            flag = 1
                            break
            if flag == 0:
                dic_hi[w] = w
        return dic_hi[w]

    def generate_stem_dict(self):
        stem_word = {}
        if not self.tokens:
            self.tokenize()
        for each_token in self.tokens:
            temp = self.generate_stem_words(each_token)
            stem_word[each_token] = temp
            self.stemmed_word.append(temp)
        return stem_word

    def remove_stop_words(self):
        f = codecs.open("rss.txt", encoding='utf-8')
        if not self.stemmed_word:
            self.generate_stem_dict()
        stopwords = [x.strip() for x in f.readlines()]
        tokens = [i for i in self.stemmed_word if str(i) not in stopwords]
        self.final_tokens = tokens
        return tokens