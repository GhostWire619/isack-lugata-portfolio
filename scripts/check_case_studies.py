"""Guard against lost case content, broken assets, and repeated hero galleries."""
from html.parser import HTMLParser
from pathlib import Path
import json
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
data = json.loads((ROOT / 'content/portfolio.json').read_text(encoding='utf8'))


class Case(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = 0
        self.chapters = 0
        self.media = False
        self.hero_images = []
        self.images = []
        self.related = []
        self.paragraph = None
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'h1': self.headings += 1
        if 'case-chapter' in classes: self.chapters += 1
        if tag == 'figure' and 'case-media' in classes: self.media = True
        if tag == 'img':
            self.images.append(attrs['src'])
            if self.media: self.hero_images.append(attrs['src'])
        if tag == 'a' and 'more-work-card' in classes: self.related.append(attrs['href'])
        if tag == 'p': self.paragraph = ''

    def handle_data(self, text):
        if self.paragraph is not None: self.paragraph += text

    def handle_endtag(self, tag):
        if tag == 'figure': self.media = False
        if tag == 'p' and self.paragraph is not None:
            self.paragraphs.append(self.paragraph.strip())
            self.paragraph = None


for project in data['projects']:
    raw = (DIST / (project['slug'] + '.html')).read_text(encoding='utf8')
    page = Case()
    page.feed(raw)
    assert page.headings == 1 and page.chapters == 3, project['slug']
    assert len(page.hero_images) == 1, project['slug']
    assert set(page.related) == {'/' + p['slug'] for p in data['projects'] if p['slug'] != project['slug']}
    assert len(page.related) == len(set(page.related))
    for paragraph in project['story']:
        assert paragraph in page.paragraphs, (project['slug'], 'Missing contribution narrative')
        assert page.paragraphs.count(paragraph) == 1, (project['slug'], 'Repeated paragraph')
    for image in page.images:
        assert image.startswith('/assets/') and (DIST / urlsplit(image).path.lstrip('/')).is_file(), image
    assert 'data-framer-name="project stack"' not in raw
print('All seven case studies preserve every story paragraph once, use one hero image, and link to six different projects with valid assets.')
