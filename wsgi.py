#!/usr/bin/env python3
# thoth-result-api
# Copyright(C) 2018, 2019 Fridolin Pokorny
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
from thoth.common import logger_setup
from thoth.common import OpenShift
from thoth.storages import AdvisersResultsStore
from thoth.storages import AnalysisResultsStore
from thoth.storages import BuildLogsAnalysisResultsStore
from thoth.storages import DependencyMonkeyReportsStore
from thoth.storages import GraphDatabase
from thoth.storages import PackageAnalysisResultsStore
from thoth.storages import ProvenanceResultsStore
from thoth.storages import SolverResultsStore
from thoth.storages import __version__ as thoth_storages_version


__version__ = "0.6.1" + "+thoth_storage." + thoth_storages_version


init_logging()
application = Flask(__name__)

_LOGGER = logging.getLogger("thoth.result_api")
_OPENSHIFT = OpenShift()


@application.route("/api/v1/adviser-result", methods=["POST"])
def post_adviser_result():  # Ignore PyDocStyleBear
    adapter = AdvisersResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    if request.form.get("origin"):
        url = request.form.get("origin")
        service = _get_service_from_url(url)
        _OPENSHIFT.schedule_kebechet_run_results(
            url=url,
            service=service,
            analysis_id=document_id,
        )
    _LOGGER.info("Adviser result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/analysis-result", methods=["POST"])
def post_analysis_result():  # Ignore PyDocStyleBear
    adapter = AnalysisResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Analyzer result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/buildlogs-analysis-result", methods=["POST"])
def post_buildlogs_analysis_result():  # Ignore PyDocStyleBear
    adapter = BuildLogsAnalysisResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Build Logs Analyzer result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/dependency-monkey-report", methods=["POST"])
def post_dependency_monkey_report():  # Ignore PyDocStyleBear
    adapter = DependencyMonkeyReportsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Dependency Monkey report stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/package-analysis-result", methods=["POST"])
def post_package_analysis_result():  # Ignore PyDocStyleBear
    adapter = PackageAnalysisResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Package Analyzer result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/provenance-checker-result", methods=["POST"])
def post_provenance_result():  # Ignore PyDocStyleBear
    adapter = ProvenanceResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    if request.form.get("origin"):
        url = request.form.get("origin")
        service = _get_service_from_url(url)
        _OPENSHIFT.schedule_kebechet_run_results(
            url=url,
            service=service,
            analysis_id=document_id,
        )
    _LOGGER.info("Provenance result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@application.route("/api/v1/solver-result", methods=["POST"])
def post_solver_result():  # Ignore PyDocStyleBear
    adapter = SolverResultsStore()
    adapter.connect()
    document_id = adapter.store_document(request.json)
    _LOGGER.info("Solver result stored with document_id %r", document_id)
    return jsonify({"document_id": document_id}), 201, {"ContentType": "application/json"}


@logger_setup("werkzeug", logging.WARNING)
@logger_setup("botocore.vendored.requests.packages.urllib3.connectionpool", logging.WARNING)
@application.route("/liveness")
def get_liveness():  # Ignore PyDocStyleBear
    adapter = SolverResultsStore()
    adapter.connect()
    adapter.ceph.check_connection()
    return jsonify({"status": "ready", "version": __version__}), 200, {"ContentType": "application/json"}


@logger_setup("werkzeug", logging.WARNING)
@logger_setup("botocore.vendored.requests.packages.urllib3.connectionpool", logging.WARNING)
@application.route("/readiness")
def get_readiness():  # Ignore PyDocStyleBear
    return jsonify({"status": "ready", "version": __version__}), 200, {"ContentType": "application/json"}


def _get_service_from_url(url: str):
    return url.split("/")[2].split(".")[0]


if __name__ == "__main__":
    _LOGGER.info(f"Result API v{__version__} starting...")
    application.run(port=8080)
