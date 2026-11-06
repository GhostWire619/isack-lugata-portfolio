"""Replace the captured project grid with the showcase, on both sides of hydration.

The server HTML and the page module must match exactly or React discards the whole page,
so the same cards leave both. The showcase sits in a slot React leaves alone, and a small
component with no output keeps the site's router reachable, all it needs from React.
"""
from pathlib import Path
import json
import subprocess

from bs4 import BeautifulSoup

from showcase_markup import render_showcase


DIST = Path(__file__).resolve().parents[1] / 'dist'
COLUMNS = ('framer-1mdtcpj', 'framer-oy8a34')
SHOWCASE_HOST = 'framer-oy8a34'
ROUTER_BRIDGE = (
    'function PortfolioRouterBridge(){const router=ce();'
    'window.__portfolioNavigate=route=>router.navigate(route,void 0,{});return null}\n'
)


def strip_grid_html(path, showcase):
    soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
    for class_name in COLUMNS:
        soup.select_one(f'.framer-lvzy8y > .{class_name}').clear()
    # In the page itself, the deck paints with the first frame instead of arriving after hydration.
    soup.select_one(f'.framer-lvzy8y > .{SHOWCASE_HOST}').append(BeautifulSoup(showcase, 'html.parser'))
    path.write_text(str(soup), encoding='utf8', newline='\n')


def strip_grid_module(path):
    js = path.read_text(encoding='utf8')
    assert 'ut as ce' in js, 'useRouter import changed'
    for index, class_name in reversed(list(enumerate(COLUMNS))):
        marker = f'className:`{class_name}`,children:['
        marker_at = js.index(marker)
        start = marker_at + len(marker)
        end = js.index(']}),', js.index('YjyOs65XK:', start))
        # In the last column that marker closes the grid too; keep the column's own closer.
        if js[end - 3:end] == ']})':
            end -= 3
        if class_name == SHOWCASE_HOST:
            # React neither compares nor replaces what is inside dangerouslySetInnerHTML,
            # which leaves the prebuilt deck alone through hydration.
            js = js[:marker_at] + f'className:`{class_name}`,' + 'dangerouslySetInnerHTML:{__html:``},suppressHydrationWarning:!0' + js[end + 1:]
        else:
            js = js[:start] + 'l(PortfolioRouterBridge,{})' + js[end:]
    js += '\n' + ROUTER_BRIDGE
    # A syntax slip here would stall the whole site silently, so fail the build instead.
    subprocess.run(['node', '--check', '--input-type=module'], input=js.encode('utf8'), check=True, capture_output=True)
    path.write_text(js, encoding='utf8', newline='\n')


def update_about(html_path, module_path):
    html = html_path.read_text(encoding='utf8')
    soup = BeautifulSoup(html, 'html.parser')
    row = soup.select_one('.framer-rqn961')
    if row:
        html = html.replace(str(row), '', 1)
    html_path.write_text(html.replace('Previous leadership role', '2025 – 2026'), encoding='utf8', newline='\n')

    js = module_path.read_text(encoding='utf8')
    start = js.find('s(`div`,{className:`framer-rqn961`,')
    if start != -1:
        end = js.index('s(`div`,{className:`framer-zehhw4`,', start)
        js = js[:start] + js[end:]
    module_path.write_text(js.replace('Previous leadership role', '2025 – 2026'), encoding='utf8', newline='\n')


if __name__ == '__main__':
    modules = DIST / 'assets' / 'framerusercontent.com' / 'sites'
    strip_grid_module(next(modules.rglob('IqnWV9by*.mjs')))
    showcase = render_showcase(json.loads((DIST.parent / 'content/portfolio.json').read_text(encoding='utf8'))['projects'])
    for page in ('index.html', 'test-1.html'):
        strip_grid_html(DIST / page, showcase)
    update_about(DIST / 'about.html', next(modules.rglob('1PtofGw*.mjs')))
