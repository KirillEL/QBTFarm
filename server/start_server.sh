#!/bin/sh

# Use FLASK_DEBUG=True if needed

FLASK_APP=$(dirname $(readlink -f $0))/standalone.py python3 -m flask run --host 0.0.0.0 --port 8989 --with-threads --debug
