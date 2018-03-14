#!/usr/bin/env python3
"""API service abstracting storage used in Thoth."""

import json
import os
import uuid

from flask import Flask
from flask import jsonify
from flask import request

from thoth.storages import AnalysisResultsStore
from thoth.storages import SolverResultsStore


application = Flask(__name__)


@application.route('/api/v1/analysis-result', methods=['POST'])
def post_analysis_result():
    adapter = AnalysisResultsStore()
    adapter.connect()
    adapter.store_document(request.json)

    # For now duplicate storing onto PV
    document_id = AnalysisResultsStore.get_document_id(request.json)
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Analysis result stored to file %r", file_path)

    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():
    adapter = SolverResultsStore()
    adapter.connect()
    adapter.store_document(request.json)

    # For now duplicate storing onto PV
    document_id = SolverResultsStore.get_document_id(request.json)
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Solver result stored to file %r", file_path)

    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/adviser-result', methods=['POST'])
def post_adviser_result():
    # TODO: create an adapter
    document_id = 'adviser-' + str(uuid.uuid4())
    file_path = os.path.join(os.environ['THOTH_PERSISTENT_VOLUME_PATH'], '{}.json'.format(document_id))
    with open(file_path, 'w') as output_file:
        json.dump(request.json, output_file, sort_keys=True, indent=2)

    application.logger.info("Adviser result stored to file %r", file_path)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/readiness')
def get_readiness():
    return jsonify(None)


@application.route('/liveness')
def get_liveness():
    assert os.path.isdir(os.environ['THOTH_PERSISTENT_VOLUME_PATH'])
    return jsonify(None)


if __name__ == '__main__':
    application.run()
