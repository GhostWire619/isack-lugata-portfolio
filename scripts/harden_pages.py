"""Final page fixes for fast, stable loading, especially on phones.

Runs after the content steps and before optimize_site.py, which versions and compresses.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
MODULES = DIST / 'assets/framerusercontent.com/sites/2Wv4lVIfy23BjKEhMEIflQ'
HOME_PAGES = {'index.html', 'test-1.html'}

REVEAL_GATE = re.compile(r"<script>\s*document\.documentElement\.classList\.add\('__loading'\);.*?</script>", re.S)
VIEWPORT = re.compile(r'<meta[^>]*name="viewport"[^>]*>')
VIEWPORT_TAG = '<meta content="width=device-width, initial-scale=1, viewport-fit=cover" name="viewport"/>'
VIDEO_SOURCE = re.compile(r'(<video\b[^>]*?)\s+src="[^"]*"')
PLAYER_SOURCE = re.compile(r'(l\(`video`,\{(?:on[A-Za-z]+:[\w$]+,)*)src:[\w$]+,')


def harden(path):
    html = path.read_text(encoding='utf8')
    # The captured page stayed invisible until every resource had loaded. Paint it at once.
    html = REVEAL_GATE.sub('', html, count=1)
    html, viewports = VIEWPORT.subn(VIEWPORT_TAG, html, count=1)
    assert viewports == 1, path.name
    # Every video on the site is hidden by CSS; Framer's players must not download them anyway.
    html = html.replace('<head>', '<head><script>HTMLVideoElement.prototype.play=function(){return Promise.resolve()};HTMLVideoElement.prototype.load=function(){}</script>', 1)
    if path.name in HOME_PAGES:
        # The grid's space is held for the showcase from the very first paint.
        html = html.replace('</head>', "<script>document.documentElement.classList.add('showcase-on')</script></head>", 1)
    path.write_text(html, encoding='utf8', newline='\n')


def remove_video_sources():
    # Every video on the site is hidden by CSS, so nothing may be able to download one:
    # Framer's player raises preload to "auto" once it is near the viewport.
    for page in DIST.glob('*.html'):
        html = page.read_text(encoding='utf8')
        stripped = VIDEO_SOURCE.sub(r'\1', html)
        if stripped != html:
            page.write_text(stripped, encoding='utf8', newline='\n')
    for path in MODULES.glob('*.mjs'):
        module = path.read_text(encoding='utf8')
        stripped = PLAYER_SOURCE.sub(r'\1', module)
        if stripped != module:
            path.write_text(stripped, encoding='utf8', newline='\n')


def remove_editor_bar():
    # Framer's on-page editor toolbar: an external script and iframe no visitor can use.
    load = 'let{createEditorBar:e}=await import(`https://framer.com/edit/init.mjs`);return{default:e()}'
    found = 0
    for path in MODULES.glob('*.mjs'):
        module = path.read_text(encoding='utf8')
        if load in module:
            found += 1
            path.write_text(module.replace(load, 'return{default:()=>null}'), encoding='utf8', newline='\n')
    leftover = [path.name for path in MODULES.glob('*.mjs') if 'framer.com/edit/init' in path.read_text(encoding='utf8')]
    assert found and not leftover, f'Editor bar loader changed: {leftover}'


def calm_hero_dust():
    # The hero's particle canvas redraws every frame; phones get the sun without it.
    path = next(MODULES.glob('Dust*.mjs'))
    module = path.read_text(encoding='utf8')
    pause = ',t.pauseOffscreen&&!s.current)return;'
    if 'innerWidth<761' not in module:
        assert pause in module, 'Dust render loop changed'
        module = module.replace(pause, ',innerWidth<761||(t.pauseOffscreen&&!s.current))return;', 1)
        path.write_text(module, encoding='utf8', newline='\n')


pages = sorted(DIST.glob('*.html'))
for page in pages:
    if '__loading' in page.read_text(encoding='utf8') or page.name in HOME_PAGES:
        harden(page)
remove_video_sources()
remove_editor_bar()
calm_hero_dust()
print('Hardened', len(pages), 'pages.')
