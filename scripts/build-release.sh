#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname -- "$0")/.."
python_bin="${BUILD123D_PYTHON:-python}"

BUILD123D_PYTHON="$python_bin" ./build.sh --stl
"$python_bin" -m unittest discover -s tests
node validate-mounting-ceilings.mjs
"$python_bin" -m scripts.package_release
