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
    return jsonify([
        '/api/v1/analysis-result',
        '/api/v1/result',
        '/api/v1/result/<file-id>',
        '/api/v1/solver-result',
        '/liveness',
        '/readiness',
    ])


@application.route('/api/v1/analysis-result', methods=['POST'])
def post_analysis_result():
    if not request.json:
        abort(400)

    file_name = str(uuid.uuid4()) + '.json'
    with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], 'analysis-' + file_name), 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Analysis result stored to file %r", file_name)
    return jsonify({'id': file_name}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():
    if not request.json:
        abort(400)

    file_name = str(uuid.uuid4()) + '.json'
    with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], 'solver-' + file_name), 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Solver result stored to file %r", file_name)
    return jsonify({}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/result/<file_id>', methods=['GET'])
def get_result(file_id):
    try:
        with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], file_id), 'r') as input_file:
            content = input_file.read()
    except FileNotFoundError:
        return jsonify({'error': "File with id %r was not found" % file_id}), 404, {'ContentType': 'application/json'}

    return content, 200, {'ContentType': 'application/json'}


@application.route('/api/v1/result', methods=['GET'])
def get_result_listing():
    file_type = request.args.get('type', None)

    if file_type not in ('solver', 'analysis', None):
        return jsonify({'error': "Unknown file type listing requested %r, should be one of (solver, analysis)"}),\
               400, {'ContentType': 'application/json'}

    files = os.listdir(os.environ['THOTH_PERSISTENT_VOLUME_PATH'])
    if file_type:
        files = [file_name for file_name in files if file_name.startswith(file_type)]

    return jsonify({'files': files}), 200, {'ContentType': 'application/json'}


@application.route('/readiness')
def get_readiness():
    return jsonify(None)


@application.route('/liveness')
def get_liveness():
    assert os.path.isdir(os.environ['THOTH_PERSISTENT_VOLUME_PATH'])
    return jsonify(None)


if __name__ == '__main__':
    application.run()
