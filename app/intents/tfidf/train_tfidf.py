# -*- coding: utf-8 -*-
import os
import logging
import json
import re
import codecs
import pickle
import hashlib
from tfidf.nlu import stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from nltk.corpus import stopwords
from markdown import _process_data
from warnings import simplefilter

simplefilter(action='ignore')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)

scriptDir = os.path.dirname(__file__)


def train_data(domain, locale, prop):
    # check if any changes to config
    if is_config_stale(domain, locale, prop):
        logger.warning("no changes found to training data, using pre-trained model")
        return json.loads('{"response":"WARNING: no changes found to training data, using pre-trained model"}')
    else:
        pass
    datapath = os.path.join(scriptDir, 'data')
    # vectorDimension = 200
    vectorDimension = int(prop.get('vector_dimension'))
    # no_iter = 15
    no_iter = int(prop.get('no_iter'))
    format = prop.get('format')

    utterance = []
    intent = []

    if format == 'md':
        utterance, intent = _process_data(domain, locale)
        if not utterance or not intent:
            return json.loads('{"response":"ERROR: could not parse the markdown data. Exiting..."}')
    elif format == 'json':
        fileData = os.path.join(scriptDir, datapath, domain + '_' + locale + '.json')
        with codecs.open(fileData, 'r', 'utf-8')as dataFile:
            data = json.load(dataFile)
        for nameUtterances in data['tasks']:
            for utt in nameUtterances['utterances']:
                utterance.append(utt)
                intent.append(nameUtterances['name'])
    else:
        logger.error("unsupported format. Exiting...")
        return json.loads('{"response":"ERROR: unsupported format. Exiting..."}')

    myIntent = set(intent)
    stopListFile = os.path.join(scriptDir, '../..', 'dictionary', 'stopwords_' + locale + '.txt')

    arrayWords = []
    stopWords = []

    f = codecs.open(stopListFile, 'r', 'utf-8')
    lines = f.read().split("\n")
    for line in lines:
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

    stemmer.initialise(locale)
    tfidfVec = TfidfVectorizer(utterance, decode_error='ignore', stop_words=stops, ngram_range=(1, 5),
                               tokenizer=stemmer.stemTokenize)
    trainsetIdfVectorizer = tfidfVec.fit_transform(utterance).toarray()
    vLength = len(trainsetIdfVectorizer[1])
    nDimension = vectorDimension
    if vLength <= vectorDimension:
        nDimension = vLength - 1

    svd = TruncatedSVD(n_components=nDimension, algorithm='randomized', n_iter=no_iter, random_state=42)
    trainLSA = svd.fit_transform(trainsetIdfVectorizer)

    pickle_path = os.path.join(scriptDir, '..', 'models', 'tfidf', domain + '_' + locale + '_')
    fileName = pickle_path + 'utterance.m'
    fileObject = open(fileName, 'wb')
    pickle.dump(utterance, fileObject)
    fileObject.close()
    fileName = pickle_path + 'intent.m'
    fileObject = open(fileName, 'wb')
    pickle.dump(intent, fileObject)
    fileObject.close()
    fileName = pickle_path + 'tfidfVec.m'
    fileObject = open(fileName, 'wb')
    pickle.dump(tfidfVec, fileObject)
    fileObject.close()
    fileName = pickle_path + 'svd.m'
    fileObject = open(fileName, 'wb')
    pickle.dump(svd, fileObject)
    fileObject.close()
    fileName = pickle_path + 'trainLSA.m'
    fileObject = open(fileName, 'wb')
    pickle.dump(trainLSA, fileObject)
    fileObject.close()

    logger.info(f'Identified domain: {domain}')
    logger.info(f'Identified locale: {locale}')
    logger.info(f'Number of utterances for training: {len(intent)}')
    logger.info(f'Number of intents for training: {len(myIntent)}')

    message = {}
    message['domain'] = domain
    message['locale'] = locale
    message['Number of utterances'] = str(len(intent))
    message['Number of intents'] = str(len(myIntent))
    response = {}
    response['response'] = message
    return response


def is_config_stale(domain, locale, properties):
    tmpFile = os.path.join(scriptDir, '..', 'tmp', domain + '_hashdump')
    try:
        tmp = open(tmpFile, 'r')
    except IOError:
        tmp = open(tmpFile, 'a+')

    hash_original = tmp.read()
    # need to check if any changes to data, property file or rasa config file
    dataFile = os.path.join(scriptDir, '..', 'data', domain + '_' + locale + '.' + properties.get('format'))
    data_1 = open(dataFile, 'rb').read()
    data_2 = json.dumps(properties)
    if (properties.get('algorithm') == 'RASA'):
        rasaConfigFile = os.path.join(scriptDir, 'dnn', 'config', properties.get('config_file'))
        data_3 = open(rasaConfigFile, 'rb').read()
    else:
        data_3 = None
    totalData = str(data_1) + str(data_2) + str(data_3)
    hash_current = hashlib.md5(totalData.encode('utf-8')).hexdigest()
    if (hash_original == hash_current):
        return True
    else:
        tmp.close()
        tmp = open(tmpFile, 'w')
        tmp.write(hash_current)
        tmp.close()
        return False
