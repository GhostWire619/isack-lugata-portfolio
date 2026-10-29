"""Install the shared analytics collectors in exported portfolio pages."""
import gzip
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = root / 'backend/static/sidenotes/analytics.js'
target = root / 'dist/assets/personal/analytics.js'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(source.read_bytes())
(target.parent / 'clarity.js').write_bytes((source.parent / 'clarity.js').read_bytes())
markers = ['<script defer src="/assets/personal/analytics.js"></script>',
           '<script defer src="/assets/personal/clarity.js"></script>']
for page in (root / 'dist').rglob('*.html'):
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html:
        continue
    # A single stable, square PNG favicon is readable by search crawlers.
    html = re.sub(r'<link\b(?=[^>]*\brel=[\'"](?:icon|shortcut icon|apple-touch-icon)[\'"])[^>]*>', '', html, flags=re.I)
    html = html.replace('</head>', '<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/favicon-180.png"></head>', 1)
    for marker in markers:
        if marker not in html:
            html = html.replace('</head>', marker + '</head>', 1)
    page.write_text(html, encoding='utf-8', newline='\n')
    for suffix in ['.gz', '.br']:
        compressed = Path(str(page) + suffix)
        if compressed.exists():
            if suffix == '.gz':
                compressed.write_bytes(gzip.compress(html.encode(), compresslevel=9, mtime=0))
            else:
                import brotli
                compressed.write_bytes(brotli.compress(html.encode()))
print('Installed first-party analytics, Clarity and GA4 on portfolio pages.')
