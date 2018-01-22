#!/usr/bin/env bash

set -ex

cd /usr/local/bin/
exec gunicorn -w 4 -b 0.0.0.0:35000 api_v1:app
