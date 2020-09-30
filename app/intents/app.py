# -*- coding: utf-8 -*-
import logging
import os
from train_model import process_ as t_process
from predict_model import process_ as p_process
import re
from flask import Flask, jsonify
from flask import request, abort, make_response
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stderrLogger = logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(stderrLogger)

app = Flask(__name__)
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5001
scriptDir = os.path.dirname(__file__)


# read url parameters from URL
# e.g. http://127.0.0.1:5001/train?domain=trip&locale=en
@app.route('/train', methods=['GET'])
def train_query():
    if not (request.args.get('domain')):
        logging.error("missing domain parameter")
        abort(404)
    if (request.args.get('locale')):
        lang = request.args.get('locale')
    else:
        lang = 'en'
    domain = request.args.get('domain')
    return make_response(jsonify(t_process(domain, lang)), 200,
                         {'Content-Type': 'application/json; charset=utf-8'})


# read url parameters from URL
# e.g. http://127.0.0.1:5001/predict?domain=trip&locale=en&userUtterance=Book my ticket
@app.route('/predict', methods=['GET'])
def predict_query():
    if not (request.args.get('domain') or request.args.get('userUtterance')):
        logging.error("missing parameters")
        abort(404)
    if (request.args.get('locale')):
        lang = request.args.get('locale')
    else:
        lang = 'en'
    query = request.args.get('userUtterance')
    if lang == 'en':
        query = re.sub(r'[^a-zA-Z ]', '', query)
    domain = request.args.get('domain')
    return make_response(jsonify(p_process(domain, lang, query)), 200,
                         {'Content-Type': 'application/json; charset=utf-8'})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'response': 'ERROR: Please check your query parameter'}), 404,
                         {'Content-Type': 'application/json; charset=utf-8'})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run(debug=False, host=SERVER_HOST, port=SERVER_PORT, threaded=True)
