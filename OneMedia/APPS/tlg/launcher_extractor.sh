#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

source ono_venv/bin/activate
nohup python3 extractor/extractor.py > nohup_extractor.log &