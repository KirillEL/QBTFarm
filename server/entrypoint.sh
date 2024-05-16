#!/bin/sh
export FLASK_APP=/server/standalone.py
exec python3 -m flask run --host 0.0.0.0 --port 1234 --with-threads