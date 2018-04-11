#!/usr/bin/env python3
"""API service abstracting storage used in Thoth."""

import logging

from flask import Flask
from flask import jsonify
from flask import request

from thoth.common import init_logging
from thoth.storages import AnalysisResultsStore
from thoth.storages import SolverResultsStore
from thoth.storages import __version__ as thoth_storages_version


__version__ = thoth_storages_version + '-results_api+dev'

init_logging()
application = Flask(__name__)

_LOGGER = logging.getLogger('thoth.result_api')


@application.route('/api/v1/analysis-result', methods=['POST'])
def post_analysis_result():
    adapter = AnalysisResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Analyzer result stored with document_id %r", document_id)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():
    adapter = SolverResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Solver result stored with document_id %r", document_id)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/adviser-result', methods=['POST'])
def post_adviser_result():
    return jsonify({'error': 'Not implemented yet'}), 500, {'ContentType': 'application/json'}


@application.route('/readiness')
def get_readiness():
    return jsonify({'status': 'ready', 'version': __version__}), 200


@application.route('/liveness')
def get_liveness():
    adapter = SolverResultsStore()
    adapter.connect()
    if not adapter.is_connected():
        raise RuntimeError("Unable to connect to the remote solver result store")

    return jsonify({'status': 'ready', 'version': __version__}), 200

if __name__ == '__main__':
    application.run()
