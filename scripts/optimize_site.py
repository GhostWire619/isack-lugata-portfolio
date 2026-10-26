"""Reduce transfers without changing image geometry or the captured layouts."""
from pathlib import Path
from io import BytesIO
from urllib.parse import urlsplit
import base64
import gzip
import hashlib
import json
import re
from PIL import Image
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
TEXT = {'.html', '.css', '.js', '.mjs', '.json', '.svg', '.xml', '.txt'}
VERSION = re.compile(r'\?v=[a-f0-9]{16}')
before_svg = after_svg = 0
before_raster = after_raster = 0
cache = {}
mapping = {}
cache_dir = ROOT / '.performance-cache'
cache_dir.mkdir(exist_ok=True)


def encode_webp(raw):
    key = hashlib.sha256(b'webp-q88-alpha-v3' + raw).hexdigest()
    if key in cache:
        return cache[key]
    saved = cache_dir / (key + '.webp')
    skipped = cache_dir / (key + '.skip')
    if saved.exists():
        cache[key] = saved.read_bytes()
        return cache[key]
    if skipped.exists():
        cache[key] = None
        return None
    with Image.open(BytesIO(raw)) as image:
        rgba = image.convert('RGBA')
        alpha = rgba.getextrema()[3][0] < 255
        image = rgba if alpha else rgba.convert('RGB')
        buffer = BytesIO()
        # Preserve dimensions and full-quality transparency. Flat logos usually
        # compress best losslessly; complex shaded frames benefit from quality 92.
        previous = cache_dir / (hashlib.sha256(b'webp-q88-alpha-v2' + raw).hexdigest() + '.webp')
        if previous.exists():
            candidate = previous.read_bytes()
        else:
            image.save(buffer, 'WEBP', lossless=alpha, quality=88, method=6)
            candidate = buffer.getvalue()
        if alpha and len(raw) > 80000:
            buffer = BytesIO()
            image.save(buffer, 'WEBP', quality=92, alpha_quality=100, method=6)
            if len(buffer.getvalue()) < len(candidate) * .7:
                candidate = buffer.getvalue()
    result = candidate if len(candidate) < len(raw) * .9 else None
    if result:
        saved.write_bytes(result)
    else:
        skipped.touch()
    cache[key] = result
    return result


for path in DIST.rglob('*'):
    if path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
        continue
    original = path.read_bytes()
    if len(original) < 16000:
        continue
    optimized = encode_webp(original)
    if not optimized:
        continue
    output = path.with_name(path.stem + '.opt.webp')
    output.write_bytes(optimized)
    mapping['/' + path.relative_to(DIST).as_posix()] = '/' + output.relative_to(DIST).as_posix()
    before_raster += len(original)
    after_raster += len(optimized)
print('Optimized', len(mapping), 'raster assets.', flush=True)

embedded = re.compile(r'data:image/(png|jpe?g|svg\+xml);base64,([A-Za-z0-9+/=]+)')
svg_cache = {}


def optimize_svg(raw):
    if raw in svg_cache:
        return svg_cache[raw]
    def replace_image(match):
        decoded = base64.b64decode(match.group(2))
        if match.group(1) == 'svg+xml':
            nested = optimize_svg(decoded.decode('utf8'))
            return 'data:image/svg+xml;base64,' + base64.b64encode(nested.encode()).decode()
        encoded = encode_webp(decoded)
        return 'data:image/webp;base64,' + base64.b64encode(encoded).decode() if encoded else match.group()
    result = embedded.sub(replace_image, raw)
    svg_cache[raw] = result
    return result


for path in DIST.rglob('*.svg'):
    raw = path.read_text(encoding='utf8')
    before_svg += len(raw.encode())
    optimized = optimize_svg(raw)
    if optimized != raw:
        path.write_text(optimized, encoding='utf8')
    after_svg += len(optimized.encode())
print('Optimized embedded photographs and screenshots in SVG artwork.', flush=True)

# Rewrite both SSR markup and client-rendered image URLs, keeping them in sync.
replacement = re.compile('|'.join(re.escape(key) for key in sorted(mapping, key=len, reverse=True)))
for path in DIST.rglob('*'):
    if path.suffix not in TEXT or path.name == 'asset-version.json':
        continue
    raw = VERSION.sub('', path.read_text(encoding='utf8'))
    optimized = replacement.sub(lambda m: mapping[m.group()], raw) if mapping else raw
    # The replaced portfolio reels must not request the original designer's MP4s.
    optimized = optimized.replace('preload:z.current?`auto`:N!==`on-mount`&&w&&!F?`none`:`metadata`', 'preload:`none`')
    path.write_text(optimized, encoding='utf8')

font_paths = [
    '/assets/framerusercontent.com/assets/nPTsv0pF51tkrOzAMoJvshgOHA.woff2',
    '/assets/framerusercontent.com/assets/bHYNJqzTyl2lqvmMiRRS6Y16Es.woff2',
]
for path in DIST.glob('*.html'):
    soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
    for tag in soup.select('link[rel="preconnect"],link[data-performance-preload]'):
        tag.decompose()
    for font in font_paths:
        soup.head.append(soup.new_tag('link', rel='preload', href=font, as_='font', type='font/woff2', crossorigin='anonymous', attrs={'data-performance-preload':'true'}))
    # Beautiful Soup's keyword helper emits "as_" literally; normalize it.
    for link in soup.select('link[as_]'):
        link['as'] = link.attrs.pop('as_')
    if soup.select_one('script[type="module"][src]'):
        base = '/assets/framerusercontent.com/sites/2Wv4lVIfy23BjKEhMEIflQ/'
        for name in ['script_main.DDonVBg0.mjs', 'framer.DCW-Gja5.mjs', 'react.DUE-xjOD.mjs', 'motion.CJbNy5E0.mjs']:
            soup.head.append(soup.new_tag('link', rel='modulepreload', href=base+name, attrs={'data-performance-preload':'true'}))
    for video in soup.select('video'):
        video['preload'] = 'none'
        video.attrs.pop('autoplay', None)
    for img in soup.select('img'):
        first_card = img.find_parent('a', href='./ecofy') or img.find_parent('a', href='./osher-market')
        hero = img.find_parent(attrs={'data-framer-name':'hero'}) or img.find_parent('figure', class_='case-media')
        if not first_card and not hero:
            img['loading'] = 'lazy'
            img['decoding'] = 'async'
        if img.get('src', '').startswith('/assets/'):
            local = DIST / urlsplit(img['src']).path.lstrip('/')
            if local.suffix in {'.webp', '.png', '.jpg', '.jpeg'} and local.is_file():
                with Image.open(local) as image:
                    width, height = image.size
                    if not img.has_attr('width') and not img.has_attr('height'):
                        img['width'], img['height'] = str(width), str(height)
                    if img.find_parent('figure', class_='case-media') and width > 1000:
                        small = local.with_name(local.stem + '.w640.webp')
                        resized = image.copy()
                        resized.thumbnail((640, 6400), Image.Resampling.LANCZOS)
                        resized.convert('RGB').save(small, 'WEBP', quality=88, method=6)
                        img['srcset'] = '/' + small.relative_to(DIST).as_posix() + ' 640w, ' + img['src'] + ' ' + str(width) + 'w'
                        img['sizes'] = '(max-width:700px) calc(100vw - 48px), 1134px'
    path.write_text(str(soup), encoding='utf8')

# One deploy token covers the entire module graph, including relative imports.
# New deploys cannot get stuck on cached, originally-hashed Framer filenames.
for path in DIST.rglob('*'):
    if path.suffix in TEXT and path.name != 'asset-version.json':
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
hasher = hashlib.sha256()
for path in sorted(DIST.rglob('*')):
    if path.is_file() and path.suffix != '.gz' and path.name != 'asset-version.json':
        hasher.update(path.relative_to(DIST).as_posix().encode())
        hasher.update(path.read_bytes())
version = hasher.hexdigest()[:16]
resource = re.compile(r'(?:/assets/|\.{1,2}/)[A-Za-z0-9_./%~-]+\.(?:mjs|js|css|woff2?|otf|ttf|svg|png|jpe?g|webp|avif|gif|json|mp4|webm)(?![A-Za-z0-9_.])')
for path in DIST.rglob('*'):
    if path.suffix not in TEXT or path.name == 'asset-version.json':
        continue
    raw = path.read_text(encoding='utf8')
    optimized = resource.sub(lambda m:m.group() + '?v=' + version, raw)
    path.write_bytes(optimized.encode('utf8'))

# Nginx serves these directly instead of spending CPU recompressing each request.
compressed_bytes = plain_bytes = 0
for old in DIST.rglob('*.gz'):
    assert old.resolve().is_relative_to(DIST.resolve())
    old.unlink()
for path in DIST.rglob('*'):
    if path.suffix not in TEXT or path.stat().st_size < 1024:
        continue
    raw = path.read_bytes()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    if len(compressed) < len(raw) * .95:
        path.with_name(path.name + '.gz').write_bytes(compressed)
        plain_bytes += len(raw)
        compressed_bytes += len(compressed)
report = {'version':version, 'optimizedRasterFiles':len(mapping), 'rasterBytesBefore':before_raster, 'rasterBytesAfter':after_raster, 'svgBytesBefore':before_svg, 'svgBytesAfter':after_svg, 'textBytesBeforeGzip':plain_bytes, 'textBytesAfterGzip':compressed_bytes, 'homepageBytes':(DIST/'index.html').stat().st_size, 'homepageGzipBytes':(DIST/'index.html.gz').stat().st_size}
(DIST/'asset-version.json').write_text(json.dumps({'version':version})+'\n', encoding='utf8')
(ROOT/'content/performance.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
print('Performance:', json.dumps(report))
