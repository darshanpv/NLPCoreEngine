# -*- coding: utf-8 -*-
import sys
from nltk import word_tokenize
from nltk.stem.isri import ISRIStemmer
from nltk.stem import SnowballStemmer
from tfidf.nlu import hindi_nlu
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')

locale = ""


def initialise(locale_):
    global locale
    locale = locale_


def stemTokenize(text):
    global locale
    if locale == 'ar':
        stemmer = ISRIStemmer()
        return [stemmer.stem(w) for w in word_tokenize(text)]
    elif locale == 'da':
        stemmer = SnowballStemmer('danish')
        return [stemmer.stem(w) for w in word_tokenize(text)]
    elif locale == 'en':
        stemmer = SnowballStemmer('english')
        return [stemmer.stem(w) for w in word_tokenize(text)]
    elif locale == 'es':
        stemmer = SnowballStemmer('spanish')
        return [stemmer.stem(w) for w in word_tokenize(text)]
    elif locale == 'hi':
        t = hindi_nlu.Processor(text)
        t.tokenize()
        return [t.generate_stem_words(w) for w in t.tokens]
    elif locale == 'mr':
        t = hindi_nlu.Processor(text)
        t.tokenize()
        return [t.generate_stem_words(w) for w in t.tokens]
    elif locale == 'nl':
        stemmer = SnowballStemmer('dutch')
        return [stemmer.stem(w) for w in word_tokenize(text)]
    elif locale == 'sv':
        stemmer = SnowballStemmer('swedish')
        return [stemmer.stem(w) for w in word_tokenize(text)]
    else:
        stemmer = SnowballStemmer('english')
        return [stemmer.stem(w) for w in word_tokenize(text)]
