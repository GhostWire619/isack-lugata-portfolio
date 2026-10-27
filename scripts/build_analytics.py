"""Install the first-party collector in exported portfolio pages."""
import gzip
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = root / 'backend/static/sidenotes/analytics.js'
target = root / 'dist/assets/personal/analytics.js'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(source.read_bytes())
marker = '<script defer src="/assets/personal/analytics.js"></script>'
for page in (root / 'dist').rglob('*.html'):
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html:
        continue
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
print('Installed anonymous per-page analytics on portfolio pages.')
