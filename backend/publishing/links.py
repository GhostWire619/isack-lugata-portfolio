"""Clickable article references without accepting arbitrary HTML from AI."""
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit
from django.utils.html import escape, urlize

MARKDOWN_LINK = re.compile(r'\[([^\]\n]{1,300})\]\(((?:https?://|mailto:)(?:[^\s<>()]|\([^\s<>()]*\)){1,2048})\)')
EMPHASIS = re.compile(r'\*\*([^*\n]{1,500})\*\*|(?<!\*)\*([^*\n]{1,500})\*(?!\*)|(?<!\w)\+\+([^+\n]{1,500})\+\+(?!\w)')


def inline_emphasis(text):
    parts, start = [], 0
    for match in EMPHASIS.finditer(text):
        parts.append(str(urlize(text[start:match.start()], autoescape=True)))
        tag, label = ('strong', match[1]) if match[1] is not None else ('em', match[2]) if match[2] is not None else ('u', match[3])
        parts.append(f'<{tag}>{escape(label)}</{tag}>')
        start = match.end()
    parts.append(str(urlize(text[start:], autoescape=True)))
    return ''.join(parts)


def inline_links(text):
    parts, start = [], 0
    for match in MARKDOWN_LINK.finditer(text):
        try:
            url = urlsplit(match[2])
            valid = ((url.scheme in {'http', 'https'} and url.hostname and not url.username and not url.password)
                or (url.scheme == 'mailto' and '@' in url.path))
        except ValueError:
            valid = False
        if not valid:
            continue
        parts.append(inline_emphasis(text[start:match.start()]))
        parts.append(f'<a href="{escape(match[2])}">{escape(match[1])}</a>')
        start = match.end()
    parts.append(inline_emphasis(text[start:]))
    return ''.join(parts)


def paragraph_html(text):
    return '<p>' + inline_links(text).replace('\n\n', '</p><p>').replace('\n', '<br/>') + '</p>'


class ArticleLinkParser(HTMLParser):
    """Apply text linking only after Wagtail has rendered its trusted rich text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.excluded = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())
        if tag in {'a', 'code', 'pre', 'script', 'style'}:
            self.excluded.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.parts.append(f'</{tag}>')
        if tag in self.excluded:
            self.excluded.remove(tag)

    def handle_data(self, data):
        self.parts.append(str(escape(data)) if self.excluded else inline_links(data))


def link_article_html(html):
    parser = ArticleLinkParser()
    parser.feed(html)
    parser.close()
    return ''.join(parser.parts)
