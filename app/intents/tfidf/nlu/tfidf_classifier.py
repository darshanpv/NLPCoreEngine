# -*- coding: utf-8 -*-
import os
import re
import codecs
import _pickle as cPickle
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')

domain = ""
locale = ""
intent = None
utterance = None
tfidfVec = None
svd = None
trainLSA = None
stops = None

scriptDir = os.path.dirname(__file__)


def initalise(domain_, locale_):
    global domain
    global locale
    global intent
    global utterance
    global tfidfVec
    global svd
    global trainLSA
    global stops

    domain = domain_
    locale = locale_

    picklePath = os.path.join(scriptDir, '..', '..', 'models', 'tfidf', domain + '_' + locale + '_')
    intent = cPickle.load(open(picklePath + 'intent.m', 'rb'))
    utterance = cPickle.load(open(picklePath + 'utterance.m', 'rb'))
    tfidfVec = cPickle.load(open(picklePath + 'tfidfVec.m', 'rb'))
    svd = cPickle.load(open(picklePath + 'svd.m', 'rb'))
    trainLSA = cPickle.load(open(picklePath + 'trainLSA.m', 'rb'))
    stopwordFile = os.path.join(scriptDir, '..', '..', '..', 'dictionary', 'stopwords_' + locale + '.txt')
    arrayWords = []
    stopWords = []
    sList = [line.rstrip('\n') for line in codecs.open((stopwordFile), 'r+', 'utf-8')]
    for line in sList:
        if line != "":
            arrayWords.append(line.split(','))
    for a_word in arrayWords:
        for s_word in a_word:
            if (re.sub(' ', '', s_word)) != "":
                stopWords.append(s_word)
    extraStopWords = set(stopWords)

    if locale == 'ar':
        stops = set(stopwords.words('arabic')) | extraStopWords
    elif locale == 'da':
        stops = set(stopwords.words('danish')) | extraStopWords
    elif locale == 'en':
        stops = set(stopwords.words('english')) | extraStopWords
    elif locale == 'es':
        stops = set(stopwords.words('spanish')) | extraStopWords
    elif locale == 'hi':
        stops = extraStopWords
    elif locale == 'mr':
        stops = extraStopWords
    elif locale == 'nl':
        stops = set(stopwords.words('dutch')) | extraStopWords
    elif locale == 'sv':
        stops = set(stopwords.words('swedish')) | extraStopWords
    else:
        stops = set(stopwords.words('english')) | extraStopWords


def stopwordRemover(utterance):
    word_tokens = word_tokenize(utterance)
    return ' '.join([w for w in word_tokens if not w in stops])


def replace_nth(string, sub, repl, nth):
    find = string.find(sub)
    i = find != -1
    while find != -1 and i != nth:
        find = string.find(sub, find + 1)
        i += 1
    if i == nth:
        return string[:find] + repl + string[find + len(sub):]
    return string


def wordReplacer(utter, matchedDict, combinations):
    matchedDict = matchedDict.copy()
    while (len(matchedDict) > 0):
        replacement = matchedDict.popitem()
        for wordReplacement in replacement[1]['synonym']:
            new_utter = utter.replace(replacement[0], wordReplacement)
            combinations.append(new_utter)
            wordReplacer(new_utter, matchedDict, combinations)


def genSentences(utter, matchedDict, combinations):
    matchedDict = matchedDict.copy()
    while (len(matchedDict) > 0):
        replacement = matchedDict.popitem()
        for count in range(replacement[1]['count']):
            for wordReplacement in replacement[1]['synonym']:
                new_utter = replace_nth(utter, replacement[0], wordReplacement, count + 1)
                combinations.append(new_utter)
                wordReplacer(new_utter, matchedDict, combinations)


def processUtterance(utter):
    scoreList = {}
    idList = {}
    for query in utter:
        query = stopwordRemover(query.lower())
        query = [query]
        test = tfidfVec.transform(query).toarray()
        LSATest = svd.transform(test)
        cosineSimilarities = linear_kernel(LSATest, trainLSA).flatten()
        related_docs_indices = cosineSimilarities.argsort()[::-1]
        for i in range(len(related_docs_indices)):
            fID = related_docs_indices[i]
            fScore = cosineSimilarities[fID]
            fIntent = intent[related_docs_indices[i]]
            if (fIntent in scoreList):
                scoreList[fIntent] = max(fScore, scoreList[fIntent])
                if (fScore > cosineSimilarities[idList.get(fIntent)]):
                    idList[fIntent] = fID
            else:
                scoreList[fIntent] = fScore
                idList[fIntent] = fID
    orderedIntents = sorted(scoreList, key=scoreList.get, reverse=True)
    intent_, score_, utterance_ = [], [], []
    intent_.append(orderedIntents[0])
    intent_.append(orderedIntents[1])
    intent_.append(orderedIntents[2])
    score_.append("{:.2f}".format(scoreList[orderedIntents[0]]))
    score_.append("{:.2f}".format(scoreList[orderedIntents[1]]))
    score_.append("{:.2f}".format(scoreList[orderedIntents[2]]))
    utterance_.append(utterance[idList.get(orderedIntents[0])])
    utterance_.append(utterance[idList.get(orderedIntents[1])])
    utterance_.append(utterance[idList.get(orderedIntents[2])])
    entities_ = []
    intent_ranking_ = [{"name": p, "confidence": q, "utterance": r} for p, q, r in zip(intent_, score_, utterance_)]
    intent_top_ = {"name": intent_[0], "confidence": score_[0]}
    # build JSON response
    response = {}
    response['intent'] = intent_top_
    response['entities'] = entities_
    response['intent_ranking'] = intent_ranking_
    response['text'] = utter[0].strip('"')
    return response


def genUtterances(utter):
    matched = {}
    utteranceSet = set(utter.split())

    synonymFile = os.path.join(scriptDir, '..', '..', '..', 'dictionary', 'synonyms_' + locale + '.txt')
    with codecs.open(synonymFile, 'r', 'utf-8')as rawSynonymsFileobj:
        rawSynonyms = rawSynonymsFileobj.read()
        rawSynonyms = rawSynonyms.split('\n')
    synonymsList = []
    for i in rawSynonyms:
        synonymsList.append(i.split(','))

    for synonym in synonymsList:
        for word in set(synonym) & utteranceSet:
            count = utter.split().count(word)
            matched[word] = {'synonym': list(set(synonym) - set([word])), 'count': count}
    combinations = [utter]
    genSentences(utter, matched, combinations)
    combinations.sort()
    return combinations
