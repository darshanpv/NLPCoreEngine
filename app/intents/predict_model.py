# -*- coding: utf-8 -*-
import logging
import json
from nlu_config import NLU_config
from tfidf import predict_tfidf
from dnn import predict_rasa
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)


def process_(domain, locale, userUtterance):
    # domain = sys.argv[1]
    # locale = sys.argv[2]
    # userUtterance = sys.argv[3]
    response = json.loads('{"response":"ERROR: error during predicting the user utterance"}')
    nlu_config = NLU_config()
    nlu_config._get_configuration(domain)

    if not nlu_config.isDataFileAvailable:
        logger.error("no intent data found. Exiting...")
        return json.loads('{"response":"ERROR: no intent data found. Exiting..."}')

    if nlu_config.algorithm == 'TFIDF':
        response = predict_tfidf.predict(domain, locale, userUtterance)
    elif nlu_config.algorithm == 'RASA':
        response = predict_rasa.predict(domain, locale, userUtterance)
    else:
        logger.error("configured algorithm is not supported. Exiting...")
    return response


if __name__ == "__main__":
    process_()
