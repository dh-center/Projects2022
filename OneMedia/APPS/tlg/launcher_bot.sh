#!/bin/bash

PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONPATH

source ono_venv/bin/activate
nohup python3 bot/bot.py &