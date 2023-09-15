#!/bin/bash

while true; do
    source /home/sz/RePolyA/venv/bin/activate
    python ui_cpp.py 8899
    echo "ui_cpp crashed with exit code $?. Respawning..." >&2
    sleep 1
done
