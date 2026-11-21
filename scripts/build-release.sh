#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname -- "$0")/.."
python_bin="${BUILD123D_PYTHON:-python}"

node prepare-wheel-scan.mjs
"$python_bin" adapter.py --no-imprint
"$python_bin" adapter.py
"$python_bin" split_adapter.py
"$python_bin" butterfly_keys.py
"$python_bin" latch.py
"$python_bin" prepare_sherman_p.py
"$python_bin" -m unittest discover -s tests
node validate-mounting-ceilings.mjs
"$python_bin" -m scripts.preview_stl
"$python_bin" -m scripts.package_release
