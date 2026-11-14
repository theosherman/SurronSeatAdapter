#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${BUILD123D_PYTHON:-$HOME/.local/share/venvs/surron-build123d/bin/python}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/surron-build123d-cache}"
exec "$python_bin" "$project_dir/adapter.py" "$@"
