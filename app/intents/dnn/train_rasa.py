# -*- coding: utf-8 -*-
import os
import logging
import sys
import hashlib
import json
from collections import OrderedDict
from rasa.nlu.training_data import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config
from warnings import simplefilter

simplefilter(action='ignore')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)

TRAINING_DATA = ''
CONFIG_DATA = ''
MODEL_NAME = ''
TMP_FILE = 'hashdump'

scriptDir = os.path.dirname(__file__)
prop_ = {}


def train_data(domain, locale, prop):
    prop_ = prop
    format = prop.get('format')
    dataFile = os.path.join(scriptDir, '..', 'data', domain + '_' + locale + '.' + format)
    configFile = os.path.join(scriptDir, 'config', prop.get('config_file'))
    modelFile = os.path.join(scriptDir, '..', 'models', 'dnn')
    MODEL_NAME = domain + '_' + locale

    if format == 'md' or format == 'json':
        training_data = load_data(dataFile)
        trainer = Trainer(config.load(configFile))
        if not is_config_stale(domain, locale, prop):
            trainer.train(training_data)
            trainer.persist(modelFile, fixed_model_name=MODEL_NAME)
        else:
            logger.warning("no changes found to training data, using pre-trained model")
            return json.loads('{"response":"WARNING: no changes found to training data, using pre-trained model"}')
    else:
        logger.error("unsupported format. Exiting...")
        return json.loads('{"response":"ERROR: unsupported format. Exiting..."}')

    training_examples = OrderedDict()
    INTENT = 'intent'
    for example in [e.as_dict_nlu() for e in training_data.training_examples]:
        intent = example[INTENT]
        training_examples.setdefault(intent, [])
        training_examples[intent].append(example)
    count = 0
    for x in training_examples:
        if isinstance(training_examples[x], list):
            count += len(training_examples[x])
    logger.info(f'Identified domain: {domain}')
    logger.info(f'Identified locale: {locale}')
    logger.info(f'Number of utterances for training: {count}')
    logger.info(f'Number of intents for training: {len(training_examples)}')

    message = {}
    message['domain'] = domain
    message['locale'] = locale
    message['Number of utterances'] = str(count)
    message['Number of intents'] = str(len(training_examples))
    response ={}
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
        rasaConfigFile = os.path.join(scriptDir, 'config', properties.get('config_file'))
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
