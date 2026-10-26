"""Check the generated SEO contract using only Python's standard library."""
from html.parser import HTMLParser
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
data = json.loads((ROOT / 'content/portfolio.json').read_text(encoding='utf8'))
origin = data['siteUrl'].rstrip('/')


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonical = []
        self.title = ''
        self.title_open = False
        self.ld_open = False
        self.ld = ''
        self.graphs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            key = attrs.get('name', attrs.get('property'))
            self.meta.setdefault(key, []).append(attrs.get('content', ''))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs['href'])
        if tag == 'title':
            self.title_open = True
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.ld_open = True
            self.ld = ''

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title_open = False
        if tag == 'script' and self.ld_open:
            self.graphs.append(json.loads(self.ld))
            self.ld_open = False

    def handle_data(self, text):
        if self.title_open:
            self.title += text
        if self.ld_open:
            self.ld += text


expected = ['/', '/about', '/robotics'] + ['/' + p['slug'] for p in data['projects']]
descriptions = set()
titles = set()
for route in expected:
    file = 'index' if route == '/' else route.lstrip('/')
    raw = (DIST / (file + '.html')).read_text(encoding='utf8')
    head = Head()
    head.feed(raw)
    assert head.canonical == [origin + route], (route, head.canonical)
    assert 'Isack Lugata' in head.title
    assert head.title not in titles
    titles.add(head.title)
    assert len(head.meta['description']) == 1
    description = head.meta['description'][0]
    assert 60 <= len(description) <= 200, (route, len(description))
    assert description not in descriptions
    descriptions.add(description)
    assert head.meta['og:url'] == [origin + route]
    assert head.meta['og:title'] == [head.title]
    assert head.meta['twitter:title'] == [head.title]
    assert head.meta['robots'] == ['index, follow, max-image-preview:large']
    image = head.meta['og:image'][0]
    assert image.startswith(origin + '/assets/') and not image.endswith('.svg')
    assert (DIST / image.removeprefix(origin + '/')).is_file()
    assert len(head.graphs) == 1
    graph = head.graphs[0]['@graph']
    person = next(n for n in graph if n['@type'] == 'Person')
    assert person['alternateName'] == data['fullName']
    assert person['telephone'] == data['whatsapp']
    assert data['instagram'] in person['sameAs']
    assert person['homeLocation']['address']['addressCountry'] == 'TZ'
    assert any(n['@type'] in ['ProfilePage', 'WebPage'] and n['url'] == origin + route for n in graph)
    assert 'daniel-sun-portfolio-replica' not in raw

sitemap = ET.parse(DIST / 'sitemap.xml')
locations = [n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(locations) == {origin + route for route in expected}
assert len(locations) == len(expected)
robots = (DIST / 'robots.txt').read_text(encoding='utf8')
assert 'User-agent: *\nAllow: /' in robots
assert 'Sitemap: ' + origin + '/sitemap.xml' in robots
auxiliary = Head()
auxiliary.feed((DIST / 'test-1.html').read_text(encoding='utf8'))
assert auxiliary.meta['robots'] == ['noindex, follow']
assert auxiliary.canonical == [origin + '/']
print('SEO checks passed for', len(expected), 'pages: canonical URLs, unique metadata, real images, structured identity, sitemap and indexing rules.')
