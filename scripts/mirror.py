"""Capture the public portfolio and its runtime dependencies without redesigning it."""
import concurrent.futures
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
ORIGIN = 'https://danielsun.space'
ASSET_HOSTS = {'framerusercontent.com', 'fonts.gstatic.com', 'lottie.host'}
URL_RE = re.compile(r'https?://[^\s"\'`<>\\)]+')
MODULE_RE = re.compile(r'["\'`]((?:\./|\.\./)[^"\'`\s]+\.(?:mjs|js|json|wasm))["\'`]')
records = {}
failures = {}
texts = {}

def local_path(url):
    p = urllib.parse.urlsplit(html.unescape(url))
    path = p.path
    if p.query:
        stem, dot, ext = path.rpartition('.')
        suffix = hashlib.sha256(p.query.encode()).hexdigest()[:12]
        path = stem + '-' + suffix + dot + ext if dot else path + '-' + suffix
    return '/assets/' + p.netloc + path

def fetch(url):
    req = urllib.request.Request(html.unescape(url), headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, timeout=90)
    except urllib.error.HTTPError as exc:
        if exc.code != 404 or urllib.parse.urlsplit(url).hostname != 'danielsun.space':
            raise
        response = exc
    with response:
        return response.read(), response.headers.get('Content-Type', '')

def discover(text, base):
    found = {html.unescape(m.group(0).rstrip(';,}')) for m in URL_RE.finditer(text)}
    found = {u for u in found if urllib.parse.urlsplit(u).hostname in ASSET_HOSTS and Path(urllib.parse.urlsplit(u).path).suffix}
    found.update(urllib.parse.urljoin(base, m.group(1)) for m in MODULE_RE.finditer(text))
    return {u for u in found if '/node_modules/' not in urllib.parse.urlsplit(u).path}

def asset(url):
    target = DIST / local_path(url).lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    cache = ROOT / '.mirror-cache' / local_path(url).lstrip('/')
    if cache.exists():
        data = cache.read_bytes()
        content_type = ''
    else:
        data, content_type = fetch(url)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(data)
        target.write_bytes(data)
    textual = target.suffix.lower() in {'.mjs', '.js', '.css', '.json', '.svg'}
    text = data.decode('utf-8') if textual else None
    return url, target, len(data), text

def clean(text):
    # Keep original visitors' analytics and editor tooling out of the local copy.
    text = re.sub(r'<script[^>]+src="https://events\.framer\.com/[^>]*></script>', '', text)
    text = re.sub(r'<link[^>]+href="https://framer\.com/edit/[^>]*>', '', text)
    for url in sorted(records, key=len, reverse=True):
        replacement = local_path(url)
        text = text.replace(url, replacement).replace(html.escape(url, quote=True), replacement)
    return text

def main():
    DIST.mkdir(parents=True, exist_ok=True)
    sitemap = fetch(ORIGIN + '/sitemap.xml')[0].decode()
    pages = [u for u in re.findall(r'<loc>(.*?)</loc>', sitemap) if not u.endswith('/llms.txt')]
    pending = set()
    for url in pages:
        raw = fetch(url)[0].decode('utf-8')
        slug = urllib.parse.urlsplit(url).path.strip('/')
        target = DIST / (slug + '.html' if slug else 'index.html')
        texts[target] = raw
        pending.update(discover(raw, url))
        print('Page:', slug or 'home', flush=True)
    while pending:
        batch = pending - records.keys() - failures.keys()
        if not batch:
            break
        pending = set()
        print('Downloading', len(batch), 'assets...', flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            tasks = {pool.submit(asset, u): u for u in batch}
            for task in concurrent.futures.as_completed(tasks):
                url = tasks[task]
                try:
                    url, target, size, text = task.result()
                    records[url] = {'path': local_path(url), 'bytes': size}
                    if text is not None:
                        texts[target] = text
                        pending.update(discover(text, url))
                except Exception as exc:
                    failures[url] = str(exc)
                    print('Failed:', url, str(exc), flush=True)
    for target, text in texts.items():
        target.write_text(clean(text), encoding='utf-8')
    (ROOT / 'asset-manifest.json').write_text(json.dumps({'origin': ORIGIN, 'pages': pages, 'assets': records, 'failures': failures}, indent=2), encoding='utf-8')
    print('Complete:', len(pages), 'pages,', len(records), 'assets,', sum(r['bytes'] for r in records.values()) // 1048576, 'MB,', len(failures), 'failures', flush=True)

if __name__ == '__main__':
    main()
