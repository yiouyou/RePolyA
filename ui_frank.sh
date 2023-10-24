#!/bin/bash

while true; do
    source ~/RePolyA/venv/bin/activate
    python ui_frank.py 7799
    echo "ui_frank crashed with exit code $?. Respawning..." >&2
    sleep 1
done
