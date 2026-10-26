"""Check compressed output integrity and versioned asset dependencies."""
from pathlib import Path
from urllib.parse import urlsplit
import gzip
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
version = json.loads((DIST / 'asset-version.json').read_text())['version']
assert re.fullmatch('[a-f0-9]{16}', version)
assert (DIST / 'index.html.gz').stat().st_size < 65536
compressed_count = 0
for packed in DIST.rglob('*.gz'):
    plain = packed.with_name(packed.name[:-3])
    assert plain.is_file(), packed
    assert gzip.decompress(packed.read_bytes()) == plain.read_bytes(), packed
    compressed_count += 1
for svg in DIST.rglob('*.svg'):
    ET.parse(svg)
imports = re.compile(r'["`](\.{1,2}/[^"`]+\.mjs(?:\?[^"`]*)?)["`]')
module_count = 0
for module in DIST.rglob('*.mjs'):
    text = module.read_text(encoding='utf8')
    for dependency in imports.findall(text):
        parsed = urlsplit(dependency)
        assert parsed.query == 'v=' + version, (module.name, dependency)
        assert (module.parent / parsed.path).resolve().is_file(), (module.name, dependency)
    module_count += 1
for name in ['index', 'about', 'ecofy']:
    html = (DIST / (name + '.html')).read_text(encoding='utf8')
    assert 'as="font"' in html and 'rel="preload"' in html
    assert '?v=' + version in html
    assert 'preload="metadata"' not in html
    assert 'portfolio-transition-bridge' not in html
    assert 'portfolio-navigation-boot' not in html
print('Performance checks passed:', compressed_count, 'valid gzip files,', module_count, 'versioned modules, valid SVGs and a homepage under 64 KB compressed.')
