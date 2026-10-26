"""Install the authorized ads.txt record and verification-only homepage metadata.

This never adds advertising scripts to portfolio pages. Journal ad serving is
controlled separately in Studio after an ad unit and Google CMP are configured.
"""
import gzip
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
record = (root / 'content/ads.txt').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'google\.com, pub-\d{16}, DIRECT, f08c47fec0942fa0', record)
(root / 'dist/ads.txt').write_text(record + '\n', encoding='utf-8', newline='\n')
publisher = 'ca-' + record.split(',')[1].strip()
page = root / 'dist/index.html'
html = page.read_text(encoding='utf-8')
html = re.sub(r'<meta\b[^>]*name=["\']google-adsense-account["\'][^>]*>', '', html)
html = html.replace('</head>', f'<meta name="google-adsense-account" content="{publisher}"></head>', 1)
page.write_text(html, encoding='utf-8', newline='\n')
if page.with_suffix('.html.gz').exists():
    page.with_suffix('.html.gz').write_bytes(gzip.compress(html.encode('utf-8'), compresslevel=9, mtime=0))
if page.with_suffix('.html.br').exists():
    import brotli
    page.with_suffix('.html.br').write_bytes(brotli.compress(html.encode('utf-8')))
print('Installed ads.txt and homepage verification metadata; portfolio advertising stays off.')
