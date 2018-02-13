#!/usr/bin/env python3

import json
import os
import uuid

from flask import abort
from flask import Flask
from flask import jsonify
from flask import request

application = Flask(__name__)


@application.route('/api/v1')
def index():
    return jsonify(['/api/v1/result', '/readiness', '/liveness'])


@application.route('/api/v1/analsis-result', methods=['POST'])
def post_analysis_result():
    if not request.json:
        abort(400)

    file_name = str(uuid.uuid4()) + '.json'
    with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], 'analysis-' + file_name), 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Result stored to file %r", file_name)
    # TODO: 202
    return jsonify({'id': file_name})


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():
    if not request.json:
        abort(400)

    file_name = str(uuid.uuid4()) + '.json'
    with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], 'solver-' + file_name), 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Result stored to file %r", file_name)
    # TODO: 202
    return jsonify({'id': file_name})


@application.route('/readiness')
def get_readiness():
    return jsonify(None)


@application.route('/liveness')
def get_liveness():
    # TODO: extend - check database connection
    return jsonify(None)


if __name__ == '__main__':
    application.run()
