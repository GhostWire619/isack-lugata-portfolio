from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.models import Site

from .advertising import article_blocks
from .models import ArticlePage, JournalIndexPage, PublicationSettings
from .tests import TEST_STORAGE


@override_settings(STORAGES=TEST_STORAGE, DEBUG=False, SECURE_SSL_REDIRECT=False)
class AdvertisingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('bootstrap_journal', verbosity=0)
        cls.journal = JournalIndexPage.objects.first()
        cls.config = PublicationSettings.for_site(Site.objects.get(is_default_site=True))
        cls.config.adsense_enabled = True
        cls.config.adsense_cmp_ready = True
        cls.config.save()
        cls.owner = get_user_model().objects.create_superuser('ad-review', 'review@example.test', 'test-only-password')

    def article(self, slug='article-with-ads', paragraphs=8):
        self.journal.refresh_from_db()
        body = [('paragraph', '<p>' + ('Readable original article content. ' * 20) + '</p>') for _ in range(paragraphs)]
        article = self.journal.add_child(instance=ArticlePage(title=slug.replace('-', ' '), slug=slug,
            intro='A substantial original article.', live=False, body=body))
        article.save_revision().publish()
        article.refresh_from_db()
        return article

    def test_real_publisher_record_and_privacy_page(self):
        response = self.client.get('/ads.txt')
        self.assertEqual(response.content.decode(), 'google.com, pub-4911606730643023, DIRECT, f08c47fec0942fa0\n')
        self.assertTrue(response['Content-Type'].startswith('text/plain'))
        response = self.client.get('/blog/privacy/')
        self.assertContains(response, 'Privacy &amp; cookies')
        self.assertContains(response, '/blog/privacy/"')
        self.assertNotContains(response, 'pagead2.googlesyndication.com')
        self.assertContains(response, 'https://adssettings.google.com/')
        response = self.client.get('/blog/terms/')
        self.assertContains(response, 'Terms of use')
        self.assertContains(response, '/blog/terms/"')
        self.assertNotContains(response, 'pagead2.googlesyndication.com')

    def test_clarity_only_loads_on_public_production_pages(self):
        marker = 'sidenotes/clarity.js'
        for path in ['/blog/', '/blog/privacy/', '/blog/terms/']:
            self.assertContains(self.client.get(path), marker, count=1)
        self.assertNotContains(self.client.get('/admin/login/'), marker)
        with override_settings(DEBUG=True):
            self.assertNotContains(self.client.get('/blog/'), marker)
        self.client.force_login(self.owner)
        self.assertNotContains(self.client.get('/blog/'), marker)

    def test_article_has_one_loader_and_correct_units_at_text_break(self):
        article = self.article()
        response = self.client.get('/blog/article-with-ads/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pagead/js/adsbygoogle.js?client=ca-pub-4911606730643023', count=1)
        self.assertContains(response, 'data-ad-slot="1485658746"', count=1)
        self.assertContains(response, 'data-ad-slot="8873194178"', count=1)
        blocks, inline = article_blocks(article.body)
        self.assertTrue(inline)
        self.assertEqual(sum(item['ad_after'] for item in blocks), 1)
        self.assertNotContains(response, 'data-ad-slot="6247030833"')

    def test_short_article_keeps_text_uninterrupted(self):
        article = self.article(paragraphs=2)
        _, inline = article_blocks(article.body)
        self.assertFalse(inline)
        response = self.client.get('/blog/article-with-ads/')
        html = response.content.decode()
        self.assertGreater(html.index('journal-ad-horizontal'), html.index('article-end'))

    def test_square_feed_ad_only_on_content_rich_listing(self):
        self.article('one')
        self.assertNotContains(self.client.get('/blog/'), 'data-ad-slot="6247030833"')
        for slug in ['two', 'three', 'four']:
            self.article(slug)
        response = self.client.get('/blog/')
        self.assertContains(response, 'data-ad-slot="6247030833"', count=1)
        self.assertContains(response, 'pagead/js/adsbygoogle.js', count=1)

    def test_disabled_unconfirmed_development_and_staff_never_load_ads(self):
        self.article()
        for field in ['adsense_enabled', 'adsense_cmp_ready']:
            PublicationSettings.objects.filter(pk=self.config.pk).update(**{field: False})
            self.assertNotContains(self.client.get('/blog/article-with-ads/'), 'pagead2.googlesyndication.com')
            PublicationSettings.objects.filter(pk=self.config.pk).update(**{field: True})
        with override_settings(DEBUG=True):
            self.assertNotContains(self.client.get('/blog/article-with-ads/'), 'pagead2.googlesyndication.com')
        self.client.force_login(self.owner)
        self.assertNotContains(self.client.get('/blog/article-with-ads/'), 'pagead2.googlesyndication.com')

    def test_draft_preview_is_ad_free_and_settings_require_consent(self):
        article = self.article()
        request = self.client.request().wsgi_request
        request.is_preview = True
        self.assertFalse(article.get_context(request)['show_article_ad'])
        self.config.adsense_cmp_ready = False
        with self.assertRaises(ValidationError):
            self.config.full_clean()

    def test_ad_preview_is_protected_and_never_loads_ad_provider(self):
        self.article()
        response = self.client.get('/admin/advertising/preview/')
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.owner)
        response = self.client.get('/admin/advertising/preview/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/security/verify/', response.url)

    def test_long_articles_cap_breaks_at_two(self):
        article = self.article(paragraphs=28)
        rows, _ = article_blocks(article.body)
        self.assertEqual(sum(row['ad_after'] for row in rows), 2)
