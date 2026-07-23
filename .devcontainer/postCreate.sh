#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/prepare_data.py
printf '\nEnvironment ready. Open notebooks/day_01_python_pandas_basics.ipynb.\n'
