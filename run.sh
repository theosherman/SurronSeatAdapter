#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${BUILD123D_PYTHON:-$HOME/.local/share/venvs/surron-build123d/bin/python}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/surron-build123d-cache}"

if [[ $# -gt 0 && ! ( $# -eq 1 && $1 == --stl ) ]]; then
  exec "$python_bin" "$project_dir/adapter.py" "$@"
fi

cd "$project_dir"
node prepare-wheel-scan.mjs
rm -f -- exports/adapter-body{,-split-front,-split-rear,-pre-imprint,-M[0-9][0-9]}.{step,stl} \
  exports/{butterfly-key-top,butterfly-key-cavity,latch}.{step,stl} \
  exports/sherman-p-prepared/{body-original,body-scaled,front-handle,rear-handle,merged}.{step,stl} \
  exports/preview.html exports/*.preview.html exports/SurronSeatAdapter.zip{,.tmp}
"$python_bin" adapter.py "$@"
"$python_bin" split_adapter.py "$@"
"$python_bin" butterfly_keys.py "$@"
"$python_bin" latch.py "$@"
if [[ $# -eq 0 ]]; then
  "$python_bin" prepare_sherman_p.py --preview-only
else
  "$python_bin" prepare_sherman_p.py
fi
"$python_bin" -m scripts.preview_stl
if [[ $# -eq 0 ]]; then
  rm -f -- exports/sherman-p-prepared/merged.stl
  rmdir exports/sherman-p-prepared 2>/dev/null || true
fi
