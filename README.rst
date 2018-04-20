Thoth-core result API
=====================

This simple API service serves as a result storing API service in the `Thoth-core project <https://github.com/thoth-station/core>`_.

It's main aim is to abstract database type and database details in analyzers and pods that are run in `thoth-middeend` part. See `Thoth-core <https://github.com/thoth-station/core>`_ for more details.

The service is built using OpenShift s2i. See `s2i-python-container README <https://github.com/sclorg/s2i-python-container>`_ for more info. There is required Python 3.6 to run this application, the actual s2i build config is part of `Thoth-core OpenShift template <https://github.com/thoth-station/core/blob/master/openshift/template.yaml>`_.

