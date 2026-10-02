#!/bin/bash
set -e
cd $(dirname "$0")

../yoyo.sh ./client.py --rass-- --stream-diagnostics \
    -- python ./server.py --name s1 --inter-file \
    -- python ./server.py --name s2
