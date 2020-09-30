# -*- coding: utf-8 -*-
import logging
import re
import sys
import json
from tfidf.nlu import tfidf_classifier as classify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)

def predict(domain, locale, userUtterance):
    if locale == 'en':
        utter = re.sub(r'[^a-zA-Z ]', '', userUtterance)
    else:
        utter = userUtterance

    classify.initalise(domain, locale)
    combinations = classify.genUtterances(utter)
    jResult = classify.processUtterance(combinations)
    logger.info(f"Prediction: {jResult}")
    #newjResult = str(jResult).replace("'", '"').strip()
    #sys.stdout.buffer.write(newjResult.encode('utf8'))
    return jResult
