#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# thoth-result-api
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""API service abstracting storage used in Thoth."""

import logging

from flask import Flask
from flask import jsonify
from flask import request

from thoth.common import init_logging
from thoth.storages import AnalysisResultsStore
from thoth.storages import SolverResultsStore
from thoth.storages import AdvisersResultsStore
from thoth.storages import __version__ as thoth_storages_version


__version__ = thoth_storages_version + '-results_api+dev'

init_logging()
application = Flask(__name__)

_LOGGER = logging.getLogger('thoth.result_api')


@application.route('/api/v1/analysis-result', methods=['POST'])
def post_analysis_result():  # Ignore PyDocStyleBear
    adapter = AnalysisResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Analyzer result stored with document_id %r", document_id)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/solver-result', methods=['POST'])
def post_solver_result():  # Ignore PyDocStyleBear
    adapter = SolverResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Solver result stored with document_id %r", document_id)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/api/v1/adviser-result', methods=['POST'])
def post_adviser_result():  # Ignore PyDocStyleBear
    adapter = AdvisersResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Adviser result stored with document_id %r", document_id)
    return jsonify({'document_id': document_id}), 201, {'ContentType': 'application/json'}


@application.route('/readiness')
def get_readiness():  # Ignore PyDocStyleBear
    return jsonify({'status': 'ready', 'version': __version__}), 200, {'ContentType': 'application/json'}


@application.route('/liveness')
def get_liveness():  # Ignore PyDocStyleBear
    adapter = SolverResultsStore()
    adapter.connect()
    adapter.ceph.check_connection()
    return jsonify({'status': 'ready', 'version': __version__}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    _LOGGER.info(f"Results API v{__version__} starting...")

    application.run(port=8080)
