#!/usr/bin/env python3

import functools
import json
import os
import uuid

from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect

from thoth.storages import AnalysisResultsStore
from thoth.storages import SolverResultsStore


application = Flask(__name__)


@application.route('/')
def index():
    return redirect('/api/v1')


@application.route('/api/v1')
def api_v1():
    return jsonify([
        '/api/v1/adviser-result',
        '/api/v1/analysis-result',
        '/api/v1/result',
        '/api/v1/result/<document-id>',
        '/api/v1/solver-result',
        '/liveness',
        '/readiness',
    ])


@application.route('/api/v1/analysis-result', methods=['POST'])
def post_analysis_result():
    document_id = 'analysis-' + str(uuid.uuid4())
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Analysis result stored to file %r", file_path)

    # For now duplicate storing to Ceph
    adapter = AnalysisResultsStore()
    adapter.connect()
    adapter.store_document(request.json)

    # TODO: unify document_id with the one stored on Ceph
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():
    document_id = 'solver-' + str(uuid.uuid4())
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Solver result stored to file %r", file_path)

    # For now duplicate storing to Ceph
    adapter = SolverResultsStore()
    adapter.connect()
    adapter.store_document(request.json)

    # TODO: unify document_id with the one stored on Ceph
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/adviser-result', methods=['POST'])
def post_adviser_result():
    document_id = 'adviser-' + str(uuid.uuid4())
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Adviser result stored to file %r", file_path)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/result/<document_id>', methods=['GET'])
def get_result(document_id):
    try:
        with open(os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], document_id + '.json'), 'r') as input_file:
            content = input_file.read()
    except FileNotFoundError:
        return jsonify({'error': "File with id %r was not found" % document_id}),\
               404, {'ContentType': 'application/json'}

    return content, 200, {'ContentType': 'application/json'}


@application.route('/api/v1/result', methods=['GET'])
def get_result_listing():
    file_type = request.args.get('type', None)

    if file_type not in ('solver', 'analysis', 'adviser', None):
        return jsonify({'error': "Unknown file type listing requested %r, "
                                 "should be one of (solver, analysis, adviser)"}),\
               400, {'ContentType': 'application/json'}

    files = os.listdir(os.environ['THOTH_PERSISTENT_VOLUME_PATH'])
    if file_type:
        files = [file_name for file_name in files if file_name.startswith(file_type)]

    files = [file_name[:-len('.json')] for file_name in files if file_name.endswith('.json')]
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
