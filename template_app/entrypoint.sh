#!/usr/bin/env bash

set -Eeuo pipefail

. .venv/bin/activate
# poetry run python -m streamlit run Home.py --server.port=80 --server.address=0.0.0.0
python -m pip install -r requirements.txt
python -m streamlit run Home.py --server.port=80 --server.address=0.0.0.0
