"""A Gremlin server adapter communicating via a web socket."""

from functools import wraps
import logging
import os

from gremlin_python.structure.graph import Graph
from gremlin_python.driver import serializer
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

_LOGGER = logging.getLogger(__name__)


def requires_connection(method):
    """Wrapper to ensure that the connection is instantiated lazily on first request."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            self.connect()
        return method(self, *args, **kwargs)

    return wrapper


class GremlinServer(object):
    """A Gremlin server adapter communicating via a web socket."""

    DEFAULT_GREMLIN_SERVER_HOST = 'localhost'
    DEFAULT_GREMLIN_SERVER_PORT = 8182

    def __init__(self):
        """Initialize Gremlin server database adapter."""
        self.g = None
        self.gremlin_server_host = os.getenv('GREMLIN_SERVER_HOST', self.DEFAULT_GREMLIN_SERVER_HOST)
        self.gremlin_server_port = os.getenv('GREMLIN_SERVER_PORT', self.DEFAULT_GREMLIN_SERVER_PORT)

    def is_connected(self):
        """Check if we are connected to a remote Gremlin server."""
        # TODO: this will require some logic to be sure that the connection is healthy.
        return self.g is not None

    def connect(self):
        """Connect to a graph database via a websocket, use GraphSONSerializersV2d0."""
        graph = Graph()
        # Make sure Gremlin uses correct serializer so data are transferred correctly. Otherwise Gremlin
        # fails silently.
        self.g = graph.traversal().withRemote(
            DriverRemoteConnection(
                'ws://{}:{}/gremlin'.format(self.gremlin_server_host, self.gremlin_server_port),
                'g',
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
        )

    def _get_or_create(self, ecosystem: str, package_name: str, package_version: str) -> int:
        """Create a node if not exists, otherwise return id of an existing one."""
        nodes = self.g.V().hasLabel('package').\
            has('ecosystem', ecosystem).\
            has('package_name', package_name).\
            has('package_version', package_version).id().toList()

        if len(nodes) > 0:
            if len(nodes) > 1:
                _LOGGER.error("Multiple nodes for same package found, package %r, version %r, nodes: %s",
                              package_name, package_version, nodes)
            return nodes[0]

        node_id = self.g.addV('package').\
            property('ecosystem', 'pypi').\
            property('package_name', package_name).\
            property('package_version', package_version).\
            id().\
            toList()[0]

        return node_id

    @requires_connection
    def store_pypi_package(self, package_name: str, package_version: str, dependencies: list) -> None:
        """Store the given PyPI package into the graph database and construct dependency graph based on dependencies."""
        # TODO: we assume that all of these queries succeed
        package_id = self._get_or_create('pypi', package_name, package_version)

        for dependency in dependencies:
            dependency_name = dependency['package_name']
            for dependency_version in dependency['resolved_versions']:
                dependency_id = self._get_or_create('pypi', dependency_name, dependency_version)
                # TODO: check if the given edge does not exist
                self.g.V(package_id).\
                    addE('depends_on').\
                    property('version_range', dependency['required_version'] or '*').\
                    to(self.g.V(dependency_id)).\
                    iterate()

    def store_pypi_solver_result(self, solver_result):
        """Store results of Thoth's PyPI dependency solver."""
        for entry in solver_result['tree']:
            self.store_pypi_package(entry['package_name'], entry['package_version'], entry['dependencies'])
