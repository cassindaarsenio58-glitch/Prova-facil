#!/usr/bin/env bash
set -o errexit
apt-get update && apt-get install -y tesseract-orc tesseract-orc-por
pip install -r requirements.txt