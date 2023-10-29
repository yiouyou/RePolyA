#!/bin/bash

while true; do
    source ~/RePolyA/venv/bin/activate
    python ui_rag.py 7788
    echo "ui_rag crashed with exit code $?. Respawning..." >&2
    sleep 1
done
