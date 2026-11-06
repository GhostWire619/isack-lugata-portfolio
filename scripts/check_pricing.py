"""Validate public prices, package fallbacks, navigation, and critical SSR content."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
import json

root = Path(__file__).resolve().parents[1]
data = json.loads((root/'content/pricing.json').read_text(encoding='utf8'))
page = BeautifulSoup((root/'dist/pricing.html').read_text(encoding='utf8'),'html.parser')
assert data['packages'][0]['price'] == 500000
assert len(page.select('h1')) == 1
assert len(page.select('.price-package')) == len(data['packages'])
assert [b['data-currency'] for b in page.select('[data-currency]')] == ['TZS','USD','EUR']
for item in data['packages'] + data['extras'] + data['care']:
    link = page.select_one(f'[data-package="{item["name"]}"]')
    assert int(link['data-package-price']) == item['price']
    query = parse_qs(urlsplit(link['href']).query)
    assert item['name'] in query['subject'][0]
    assert f'{item["price"]:,}' in query['body'][0]
assert page.select_one('a[href="/blog/"]')
for name in ['index','about','globoexpats','falco','robotics']:
    soup = BeautifulSoup((root/'dist'/f'{name}.html').read_text(encoding='utf8'),'html.parser')
    assert soup.select_one('.portfolio-extra-nav a[href="/pricing"]'), name
    assert soup.select_one('.portfolio-extra-nav a[href="/blog/"]'), name
home = BeautifulSoup((root/'dist/index.html').read_text(encoding='utf8'),'html.parser')
assert home.select_one('.framer-1mdtcpj a')['href'] == './globoexpats'
assert home.select_one('.framer-oy8a34 a')['href'] == './falco'
for card in home.select('.framer-lvzy8y a'):
    if 'More projects' in card.get_text(): assert not card.has_attr('href')
    else: assert card.get('data-project-description')
print('Pricing, currency choices, package enquiry fallbacks, navigation and server-rendered project ordering passed.')
