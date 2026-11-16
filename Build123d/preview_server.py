#!/usr/bin/env python3
"""Local auto-refreshing preview browser. Python standard library only."""
import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent / 'tmp'
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'}
IDENTITY = 'surron-preview-server-v1'


def preview_file(root, name):
    root = root.resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        raise ValueError('Not a preview image inside Build123d/tmp')
    return path


def latest_preview(root=ROOT):
    candidates = []
    for path in root.rglob('*'):
        if path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            path = preview_file(root, str(path.relative_to(root)))
            stat = path.stat()
            candidates.append((stat.st_mtime_ns, path, stat.st_size))
        except (ValueError, OSError):
            continue
    if not candidates:
        return None
    modified, path, size = max(candidates)
    return dict(path=path.relative_to(root.resolve()).as_posix(), version=f'{modified}-{size}')


PAGE = b'''<!doctype html><html><meta charset="utf-8"><title>Adapter previews</title>
<style>body{margin:0;background:#18232e;color:#edf3f8;font:16px system-ui}header{padding:14px 22px;display:flex;gap:24px;align-items:center}span{color:#b6c8d6;font-size:14px}main{height:calc(100vh - 66px);display:grid;place-items:center}img{max-width:98vw;max-height:calc(100vh - 75px);object-fit:contain}a{color:#a5d9ff}#empty{padding:30px}</style>
<header><strong>Adapter previews</strong><span id="status">Connecting...</span><a id="open" target="_blank" hidden>Open full size</a></header>
<main><div id="empty">Waiting for a preview in Build123d/tmp...</div><img id="preview" hidden alt="Latest adapter preview"></main>
<script>
let version='';const img=document.getElementById('preview'),status=document.getElementById('status'),empty=document.getElementById('empty'),open=document.getElementById('open');
async function refresh(){try{const r=await fetch('/api/latest',{cache:'no-store'});if(!r.ok)throw Error(r.status);const data=await r.json(),p=data.preview;
if(p){status.textContent='Watching for updates';if(version!==p.version+p.path){const url='/image?path='+encodeURIComponent(p.path)+'&v='+p.version;const next=new Image();next.onload=()=>{img.src=url;img.hidden=false;empty.hidden=true;open.href=url;open.hidden=false;version=p.version+p.path;};next.src=url;}}
else{status.textContent='Waiting for preview';img.hidden=true;empty.hidden=false;open.hidden=true;version='';}}
catch(e){status.textContent='Server disconnected - retrying...';}finally{setTimeout(refresh,1000);}}refresh();
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/':
            content, kind = PAGE, 'text/html; charset=utf-8'
        elif url.path == '/api/latest':
            content = json.dumps(dict(server=IDENTITY, pid=os.getpid(), preview=latest_preview())).encode()
            kind = 'application/json'
        elif url.path == '/image':
            try:
                path = preview_file(ROOT, parse_qs(url.query).get('path', [''])[0])
                content, kind = path.read_bytes(), mimetypes.guess_type(path)[0] or 'application/octet-stream'
            except (ValueError, OSError):
                self.send_error(404)
                return
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


def running(port):
    try:
        with urlopen(f'http://127.0.0.1:{port}/api/latest', timeout=1) as response:
            info = json.load(response)
            return info if info.get('server') == IDENTITY else None
    except (OSError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=['start', 'stop', 'status', 'serve'], default='start')
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--no-open', action='store_true', help='Do not open the browser')
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    address = f'http://127.0.0.1:{args.port}'
    if args.action == 'serve':
        with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
            server.serve_forever()
        return
    info = running(args.port)
    if args.action == 'stop':
        if info:
            os.kill(info['pid'], signal.SIGTERM)
        print('Preview server stopped.' if info else 'Preview server is not running.')
        return
    if args.action == 'status':
        print(address if info else 'Preview server is not running.')
        return
    if not info:
        with (ROOT/'preview-server.log').open('ab') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'serve', '--port', str(args.port)],
                                     stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        for _ in range(40):
            if running(args.port):
                break
            if child.poll() is not None:
                raise SystemExit(f'Could not start preview server. See {ROOT / "preview-server.log"}')
            time.sleep(.1)
        else:
            raise SystemExit('Preview server did not become ready.')
    print(f'Preview browser: {address}', flush=True)
    if not args.no_open:
        webbrowser.open(address)


if __name__ == '__main__':
    main()
