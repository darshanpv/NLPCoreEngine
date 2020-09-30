# -*- coding: utf-8 -*-
import os
import logging
import sys
import json
from collections import OrderedDict
from warnings import simplefilter

from rasa.nlu.model import Interpreter
from rasa.nlu.training_data import load_data

simplefilter(action='ignore')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)

scriptDir = os.path.dirname(__file__)
dataFile = ""


def predict(domain, locale, userUtterance):
    modelFile = os.path.join(scriptDir, '..', 'models', 'dnn')
    global dataFile
    dataFile = os.path.join(scriptDir, '..', 'data', domain + '_' + locale + '.md')
    MODEL_NAME = domain + '_' + locale
    interpreter = Interpreter.load(os.path.join(modelFile, MODEL_NAME))
    data = interpreter.parse(userUtterance)
    intent_, score_, utterance_ = [], [], []
    intent_.append(data['intent_ranking'][0]['name'])
    intent_.append(data['intent_ranking'][1]['name'])
    intent_.append(data['intent_ranking'][2]['name'])
    score_.append("{:.2f}".format(data['intent_ranking'][0]['confidence']))
    score_.append("{:.2f}".format(data['intent_ranking'][1]['confidence']))
    score_.append("{:.2f}".format(data['intent_ranking'][2]['confidence']))
    utterance_.append(getUtterance(intent_[0]))
    utterance_.append(getUtterance(intent_[1]))
    utterance_.append(getUtterance(intent_[2]))
    entities_ = data['entities']
    text_ = data['text']
    intent_ranking_ = [{"name": p, "confidence": q, "utterance": r} for p, q, r in zip(intent_, score_, utterance_)]
    intent_top_ = {"name": intent_[0], "confidence": score_[0]}
    # build JSON response
    response = {}
    response['intent'] = intent_top_
    response['entities'] = entities_
    response['intent_ranking'] = intent_ranking_
    response['text'] = text_
    logger.info(f"Prediction: {response}")
    # newjResult = str(response).replace("'", '"').strip()
    # sys.stdout.buffer.write(newjResult.encode('utf8'))
    return response


def getUtterance(intent_):
    train_data = load_data(dataFile)
    training_examples = OrderedDict()
    INTENT = 'intent'
    for example in [e.as_dict_nlu() for e in train_data.training_examples]:
        intent = example[INTENT]
        training_examples.setdefault(intent, [])
        training_examples[intent].append(example)
    return training_examples[intent_][0]['text']
