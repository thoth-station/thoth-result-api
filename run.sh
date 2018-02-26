#!/bin/bash -ex

THOTH_PERSISTENT_VOLUME_PATH='volume' gunicorn -w 4 -b localhost:8080 wsgi:application
