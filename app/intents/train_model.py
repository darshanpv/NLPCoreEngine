# -*- coding: utf-8 -*-
import sys
import json
import logging
from nlu_config import NLU_config
from tfidf import train_tfidf
from dnn import train_rasa
from warnings import simplefilter

simplefilter(action='ignore')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)


def process_(domain, locale):
    # domain = sys.argv[1]
    # locale = sys.argv[2]

    response = json.loads('{"response":"ERROR: Error during training the data"}')
    nlu_config = NLU_config()
    nlu_config._get_configuration(domain)

    if not nlu_config.isDataFileAvailable:
        logger.error("no intent data found. Exiting...")
        return response

    if nlu_config.algorithm == 'TFIDF':
        response = train_tfidf.train_data(domain, locale, nlu_config.properties)
    elif nlu_config.algorithm == 'RASA':
        response = train_rasa.train_data(domain, locale, nlu_config.properties)
    else:
        logger.error("configured algorithm is not supported. Exiting...")
    return response


if __name__ == "__main__":
    process_()
