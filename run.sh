#!/usr/bin/env sh

# This script must be executed by a user with read and write access to the
# docker socket

# shellcheck disable=SC1091
. ./venv/bin/activate
. ./secret.env
export LOGGING_LEVEL=INFO
python3 src/main.py -a "$TELEGRAM_ADMIN" -t "$TELEGRAM_TOKEN"