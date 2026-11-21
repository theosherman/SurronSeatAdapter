#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${BUILD123D_PYTHON:-$(command -v python3.14 || echo /opt/az/bin/python3.14)}"
if ! command -v "$python_bin" >/dev/null; then
  echo "Python 3.14 not found. Set BUILD123D_PYTHON to your shared Python executable." >&2
  exit 127
fi
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/surron-build123d-cache}"

if [[ $# -gt 0 && ! ( $# -eq 1 && ( $1 == --stl || $1 == --preview ) ) ]]; then
  exec "$python_bin" "$project_dir/adapter.py" "$@"
fi

cd "$project_dir"
exec "$python_bin" -m scripts.build_cad "$@"
