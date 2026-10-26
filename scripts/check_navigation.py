"""Guard the single-router navigation and matching project hydration shell."""
from pathlib import Path
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
MODULES = DIST / 'assets/framerusercontent.com/sites/2Wv4lVIfy23BjKEhMEIflQ'
from integrate_case_router import ROUTES

navigation = (DIST / 'assets/personal/navigation.js').read_text(encoding='utf8')
css = (DIST / 'assets/personal/navigation.css').read_text(encoding='utf8')
assert 'location.assign' not in navigation
assert 'stopImmediatePropagation' not in navigation
assert '@view-transition' not in css and 'transition-bridge' not in css
for slug, (route_id, filename) in ROUTES.items():
    soup = BeautifulSoup((DIST / (slug + '.html')).read_text(encoding='utf8'), 'html.parser')
    root = soup.select_one('[data-framer-root].portfolio-case-root')
    assert root and root.select_one('.case-shell') and root.select_one('.case-footer'), slug
    assert root.find_previous_sibling().get('data-framer-html-style') == '', slug
    assert root.find_next_sibling().get('id') == 'overlay', slug
    assert route_id in soup.select_one('#main')['data-framer-hydrate-v2'], slug
    module = (MODULES / filename).read_text(encoding='utf8')
    assert 'makeCasePage(' in module and re.search(r'PortfolioCase\d as default', module), slug
adapter = (MODULES / 'portfolio-cases.mjs').read_text(encoding='utf8')
assert 'router.navigate(' in adapter and "id:'overlay'" in adapter
assert not (DIST / 'assets/personal/navigation-boot.js').exists()
print('Navigation checks passed: one router, matching case hydration shells, no forced reloads or screen wipes.')
