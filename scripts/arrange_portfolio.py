"""Keep the captured HTML and its hydrated components in the same order."""
from pathlib import Path
import re

from bs4 import BeautifulSoup


DIST = Path(__file__).resolve().parents[1] / 'dist'
LEFT = ('globoexpats', 'wakili-msomi', 'ecofy', 'habitek')
RIGHT = ('falco', 'tanstack-tanzania', 'osher-market', 'placeholder')
COLUMNS = (('framer-1mdtcpj', LEFT), ('framer-oy8a34', RIGHT))


def arrange_home(path):
    html = path.read_text(encoding='utf8')
    soup = BeautifulSoup(html, 'html.parser')
    groups = {route: [] for route in LEFT + RIGHT}
    columns = []
    for class_name, order in COLUMNS:
        column = soup.select_one(f'.framer-lvzy8y > .{class_name}')
        columns.append((column, str(column), order))
        for variant in column.find_all(recursive=False):
            route = variant.select_one('a[href]')['href'].lstrip('./')
            if route == 'habitek' and class_name == 'framer-oy8a34':
                route = 'placeholder'
            groups[route].append(variant.extract())
    for column, original, order in columns:
        for route in order:
            column.extend(groups[route])
        html = html.replace(original, str(column), 1)
    path.write_text(html, encoding='utf8', newline='\n')


def arrange_home_module(path):
    js = path.read_text(encoding='utf8')
    names = dict(zip(LEFT + RIGHT[:-1], (
        'GloboExpats', 'Wakili Msomi', 'Ecofy Africa', 'Habitek',
        'Falco Finance', 'TanStack Tanzania', 'Osher Market',
    )))
    groups = {}
    columns = []
    for class_name, order in COLUMNS:
        start = js.index(f'className:`{class_name}`,children:[') + len(f'className:`{class_name}`,children:[')
        end = js.index(']}),', js.index('YjyOs65XK:', start))
        cards = js[start:end].split(',l(M,{links:[')
        cards[1:] = ['l(M,{links:[' + card for card in cards[1:]]
        assert len(cards) == len(order), class_name
        columns.append((start, end, order))
        for card in cards:
            title = re.search(r'RehjAvB2r:`([^`]+)`', card)[1]
            route = next(route for route, name in names.items() if name == title)
            if route == 'habitek' and class_name == 'framer-oy8a34':
                route = 'placeholder'
            groups[route] = card
    for start, end, order in reversed(columns):
        js = js[:start] + ','.join(groups[route] for route in order) + js[end:]
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
    arrange_home_module(next(modules.rglob('IqnWV9by*.mjs')))
    for page in ('index.html', 'test-1.html'):
        arrange_home(DIST / page)
    update_about(DIST / 'about.html', next(modules.rglob('1PtofGw*.mjs')))
