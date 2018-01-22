#!/usr/bin/env python3

import json

from flask import abort
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

# TODO: use OpenShift's s2i


@app.route('/')
def index():
    return jsonify(['/v1/result', '/readiness', '/liveness'])


@app.route('/v1/result', methods=['POST'])
def post_result():
    if not request.json:
        abort(400)
    # Print to console for now.
    print(json.dumps(request.json))
    return jsonify(None)


@app.route('/readiness')
def get_readiness():
    # TODO: extend - check database connection
    return jsonify(None)


@app.route('/liveness')
def get_liveness():
    # TODO: extend - check database connection
    return jsonify(None)
