#!/bin/bash -ex

gunicorn -w 4 -b localhost:8080 wsgi:application
