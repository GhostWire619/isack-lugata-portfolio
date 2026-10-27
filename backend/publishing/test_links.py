from django.test import SimpleTestCase
from bs4 import BeautifulSoup
from .links import paragraph_html, link_article_html


class ArticleLinkTests(SimpleTestCase):
    def test_named_links_and_plain_urls_preserve_query_strings(self):
        html = paragraph_html('Read [the source](https://example.com/report?a=1&b=2), then https://example.org/docs.\n\nNext paragraph.')
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual([(link.text, link['href']) for link in soup.select('a')], [
            ('the source', 'https://example.com/report?a=1&b=2'), ('https://example.org/docs', 'https://example.org/docs')])
        self.assertEqual(len(soup.select('p')), 2)

    def test_does_not_accept_html_or_javascript_links(self):
        html = paragraph_html('<script>alert(1)</script> [bad](javascript:alert(1)) <img src=x onerror=alert(1)>')
        soup = BeautifulSoup(html, 'html.parser')
        self.assertFalse(soup.select('script,img,a'))
        self.assertIn('<script>', soup.text)

    def test_existing_links_are_not_nested_and_code_is_not_linked(self):
        original = '<p><strong>Source:</strong> <a href="https://example.com">https://example.com</a> &amp; https://other.example/?x=1&amp;y=2</p><pre><code>https://code.example</code></pre>'
        rendered = link_article_html(original)
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertEqual(len(soup.select('a')), 2)
        self.assertFalse(soup.select('a a, code a'))
        self.assertEqual(soup.select('a')[1]['href'], 'https://other.example/?x=1&y=2')
        self.assertIsNotNone(soup.select_one('strong'))
        self.assertEqual(link_article_html(rendered), rendered)

    def test_encoded_html_stays_text_and_urls_with_parentheses_work(self):
        rendered = link_article_html('<p>&lt;script&gt;bad&lt;/script&gt; [Reference](https://example.com/wiki/Topic_(detail))</p>')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertFalse(soup.select('script'))
        self.assertEqual(soup.select_one('a')['href'], 'https://example.com/wiki/Topic_(detail)')
