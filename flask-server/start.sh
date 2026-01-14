#!/bin/sh

python populatedb.py && \
exec python server.py
