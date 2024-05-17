#!/usr/bin/env bash

HOST=$1
shift
PORT=$1
shift
TIMEOUT=60

echo "Waiting for $HOST:$PORT to be ready..."

until timeout 1 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT"; do
    echo "Waiting for $HOST:$PORT..."
    sleep 1
done

echo "$HOST:$PORT is ready!"
exec "$@"
