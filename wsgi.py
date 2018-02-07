#!/usr/bin/env python3

import json

from flask import abort
from flask import Flask
from flask import jsonify
from flask import request

application = Flask(__name__)


@application.route('/')
def index():
    return jsonify(['/v1/result', '/readiness', '/liveness'])


@application.route('/v1/result', methods=['POST'])
def post_result():
    if not request.json:
        abort(400)
    # Print to console for now.
    print(json.dumps(request.json))
    return jsonify(None)


@application.route('/readiness')
def get_readiness():
    # TODO: extend - check database connection
    return jsonify(None)


@application.route('/liveness')
def get_liveness():
    # TODO: extend - check database connection
    return jsonify(None)


if __name__ == '__main__':
    application.run()
