from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, Client, override_settings
from django.utils import timezone
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from PIL import Image
from wagtail.images import get_image_model
from wagtail.models import PageViewRestriction
from .models import JournalIndexPage, ArticlePage, Category
from django.urls import reverse
from wagtail.test.utils.form_data import nested_form_data, streamfield, rich_text


TEST_STORAGE = {'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}}


@override_settings(STORAGES=TEST_STORAGE)
class PublishingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('bootstrap_journal', verbosity=0)
        cls.journal = JournalIndexPage.objects.first()
        cls.category = Category.objects.get(slug='technology')
    def make_article(self, slug='public-article', publish=True, **kwargs):
        page = self.journal.add_child(instance=ArticlePage(title=slug.replace('-', ' ').title(), slug=slug,
            intro='A real article introduction about technology and publishing.', live=False,
            category=self.category, body=[('heading', 'A clear heading'),
                ('paragraph', '<p>Complete readable article text, returned in the initial HTML.</p>')], **kwargs))
        revision = page.save_revision()
        if publish:
            revision.publish()
        return ArticlePage.objects.get(pk=page.pk)
    def test_publication_and_unpublishing_control_all_public_surfaces(self):
        live = self.make_article()
        draft = self.make_article('secret-draft', publish=False)
        for url in ['/blog/', '/blog/feed/', '/sitemap.xml']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            self.assertContains(response, live.title if url != '/sitemap.xml' else live.slug)
            self.assertNotContains(response, draft.slug)
            self.assertNotContains(response, draft.title)
        self.assertEqual(self.client.get('/blog/secret-draft/').status_code, 404)
        response = self.client.get('/blog/public-article/')
        self.assertContains(response, 'Complete readable article text')
        self.assertContains(response, 'application/ld+json')
        self.assertContains(response, 'rel="canonical"')
        live.unpublish()
        self.assertEqual(self.client.get('/blog/public-article/').status_code, 404)
        self.assertNotContains(self.client.get('/blog/feed/'), live.title)
    def test_private_articles_do_not_leak_into_feed_search_or_sitemap(self):
        private = self.make_article('private-article')
        PageViewRestriction.objects.create(page=private, restriction_type='login')
        for url in ['/blog/', '/blog/?q=private', '/blog/feed/', '/sitemap.xml']:
            self.assertNotContains(self.client.get(url), private.slug)
            self.assertNotContains(self.client.get(url), private.title)
    def test_editing_a_draft_preserves_the_current_live_revision(self):
        article = self.make_article('revision-example')
        article.intro = 'Unpublished replacement introduction.'
        revision = article.save_revision()
        response = self.client.get('/blog/revision-example/')
        self.assertNotContains(response, 'Unpublished replacement introduction.')
        self.assertContains(response, 'A real article introduction')
        revision.publish()
        self.assertContains(self.client.get('/blog/revision-example/'), 'Unpublished replacement introduction.')

    def test_existing_plain_text_references_become_links_without_republishing(self):
        article = self.make_article('clickable-references')
        article.body = [('paragraph', '<p>Visit https://example.com/reference or [the report](https://example.org/report).</p>')]
        article.save_revision().publish()
        response = self.client.get('/blog/clickable-references/')
        self.assertContains(response, 'href="https://example.com/reference"')
        self.assertContains(response, '<a href="https://example.org/report">the report</a>', html=True)
    def test_search_topic_filter_and_safe_search_markup(self):
        self.make_article('searchable-example')
        other = Category.objects.get(slug='science')
        page = self.make_article('different-subject')
        page.category = other
        page.save_revision().publish()
        response = self.client.get('/blog/?category=technology&q=searchable')
        self.assertContains(response, 'Searchable Example')
        self.assertNotContains(response, 'Different Subject')
        self.assertContains(response, 'noindex,follow')
        response = self.client.get('/blog/', {'q': '"><script>alert(1)</script>'})
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, 'No articles match')
    def test_pagination_does_not_repeat_the_featured_article(self):
        for i in range(13):
            self.make_article(f'article-{i}')
        first = self.client.get('/blog/')
        second = self.client.get('/blog/?page=2')
        first_ids = {p.pk for p in first.context['articles']}
        second_ids = {p.pk for p in second.context['articles']}
        self.assertFalse(first_ids & second_ids)
        self.assertEqual(len(first_ids | second_ids | {first.context['featured'].pk}), 13)
    def test_scheduled_revision_remains_private_until_the_scheduler_runs(self):
        page = self.make_article('scheduled-article', publish=False)
        page.go_live_at = timezone.now() + timedelta(days=1)
        revision = page.save_revision()
        revision.publish()
        self.assertFalse(ArticlePage.objects.get(pk=page.pk).live)
        self.assertEqual(self.client.get('/blog/scheduled-article/').status_code, 404)
        past = timezone.now() - timedelta(minutes=1)
        revision.refresh_from_db()
        revision.approved_go_live_at = past
        revision.content['go_live_at'] = past.isoformat()
        revision.save()
        call_command('publish_scheduled', verbosity=0)
        self.assertTrue(ArticlePage.objects.get(pk=page.pk).live)
        self.assertEqual(self.client.get('/blog/scheduled-article/').status_code, 200)
    def test_uploaded_cover_generates_responsive_compressed_images(self):
        with TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            output = BytesIO()
            Image.new('RGB', (1800, 1200), '#42643a').save(output, 'JPEG')
            image = get_image_model().objects.create(title='Cover image', file=SimpleUploadedFile('cover.jpg', output.getvalue(), content_type='image/jpeg'))
            self.make_article('illustrated-article', cover=image, cover_alt='A green test illustration')
            response = self.client.get('/blog/illustrated-article/')
            self.assertContains(response, 'image/avif')
            self.assertContains(response, '.webp')
            self.assertContains(response, 'srcset=')
            self.assertContains(response, 'A green test illustration')
            self.assertTrue(image.renditions.filter(filter_spec__contains='format-webp').exists())


@override_settings(STORAGES=TEST_STORAGE)
class AdminSecurityTests(TestCase):
    def setUp(self):
        call_command('bootstrap_journal', verbosity=0)
        self.user = get_user_model().objects.create_superuser(username='test-owner', email='owner@example.test', password='Only-for-automated-tests-123!')
    def test_password_login_routes_to_second_factor(self):
        response = self.client.post('/admin/login/', {'username': 'test-owner', 'password': 'Only-for-automated-tests-123!'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(self.client.get('/admin/'), '/security/verify/', fetch_redirect_response=False)
    def test_repeated_bad_passwords_are_throttled(self):
        for _ in range(5):
            response = self.client.post('/admin/login/', {'username': 'test-owner', 'password': 'Incorrect-password-123!'})
        self.assertEqual(response.status_code, 429)
    def test_unverified_owner_can_sign_out(self):
        self.client.force_login(self.user)
        self.client.post('/admin/logout/')
        self.assertNotIn('_auth_user_id', self.client.session)
    def test_admin_requires_password_and_a_second_factor(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get('/admin/')
        self.assertRedirects(response, '/security/verify/', fetch_redirect_response=False)
        response = self.client.get('/security/verify/')
        self.assertContains(response, 'Secure your publishing account')
        self.assertIn('no-store', response['Cache-Control'])
        device = TOTPDevice.objects.get(user=self.user)
        token = str(totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits)).zfill(device.digits)
        response = self.client.post('/security/verify/', {'token': token})
        self.assertContains(response, 'Keep a way back in')
        self.assertEqual(len(response.context['codes']), 10)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
    def test_recovery_code_is_single_use(self):
        TOTPDevice.objects.create(user=self.user, confirmed=True)
        backup = StaticDevice.objects.create(user=self.user, name='Journal recovery')
        code = StaticToken.random_token()
        StaticToken.objects.create(device=backup, token=code)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/security/verify/', {'token': code}).status_code, 302)
        self.assertFalse(StaticToken.objects.filter(device=backup, token=code).exists())
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.post('/security/verify/', {'token': code})
        self.assertContains(response, 'could not be verified')
        self.assertRedirects(self.client.get('/admin/'), '/security/verify/', fetch_redirect_response=False)
    def test_verification_requires_csrf_and_does_not_expose_account_setup_anonymously(self):
        anonymous = self.client.get('/security/verify/')
        self.assertEqual(anonymous.status_code, 302)
        self.assertFalse(TOTPDevice.objects.exists())
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.user)
        self.assertEqual(protected.post('/security/verify/', {'token': '000000'}).status_code, 403)
    def test_invalid_codes_do_not_confirm_an_authenticator(self):
        self.client.force_login(self.user)
        self.client.get('/security/verify/')
        response = self.client.post('/security/verify/', {'token': 'not-a-valid-code'})
        self.assertContains(response, 'could not be verified')
        self.assertFalse(TOTPDevice.objects.get(user=self.user).confirmed)

    def login_verified(self):
        self.client.force_login(self.user)
        device = TOTPDevice.objects.create(user=self.user, confirmed=True)
        session = self.client.session
        session['otp_device_id'] = device.persistent_id
        session.save()

    def test_editor_is_discoverable_and_ready_to_write(self):
        self.login_verified()
        dashboard = self.client.get('/admin/')
        self.assertContains(dashboard, 'Your articles')
        self.assertContains(dashboard, 'Write an article')
        self.assertContains(dashboard, '/admin/articles/new/')
        redirect = self.client.get('/admin/articles/new/')
        self.assertEqual(redirect.status_code, 302)
        form = self.client.get(redirect.url)
        self.assertContains(form, 'Write your article')
        self.assertContains(form, 'Search &amp; sharing')
        self.assertContains(form, 'data-a11y-dialog-show="schedule-publishing-dialog"')
        self.assertContains(form, 'journal-editor-actions')
        self.assertContains(form, 'name="action-publish"')
        self.assertEqual(form.context['form'].instance.body[0].block_type, 'paragraph')

    def test_owner_can_save_and_publish_an_article_through_the_actual_editor(self):
        self.login_verified()
        journal = JournalIndexPage.objects.first()
        add_url = self.client.get('/admin/articles/new/').url
        data = nested_form_data({'title': 'My first article', 'slug': 'my-first-article',
            'intro': 'An introduction written through the actual publishing form.', 'author_name': 'Isack Lugata',
            'body': streamfield([('paragraph', rich_text('<p>This is my article, written in the editor.</p>'))]),
            'action-save-draft': 'Save draft', 'next': '/admin/articles/'})
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None))
        self.assertIn('/edit/?next=/admin/articles/', response.url)
        article = ArticlePage.objects.get(slug='my-first-article')
        self.assertFalse(article.live)
        self.assertEqual(self.client.get('/blog/my-first-article/').status_code, 404)
        self.assertContains(self.client.get('/admin/?status=draft'), 'My first article')
        data.pop('action-save-draft')
        data['action-publish'] = 'Publish'
        response = self.client.post(reverse('wagtailadmin_pages:edit', args=[article.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/articles/')
        article.refresh_from_db()
        self.assertTrue(article.live)
        self.assertContains(self.client.get('/blog/my-first-article/'), 'This is my article, written in the editor.')

    def test_write_destination_survives_two_factor_verification(self):
        self.client.force_login(self.user)
        self.client.get('/admin/articles/new/')
        self.client.get('/security/verify/')
        device = TOTPDevice.objects.get(user=self.user)
        token = str(totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits)).zfill(device.digits)
        response = self.client.post('/security/verify/', {'token': token})
        self.assertContains(response, 'href="/admin/articles/new/"')
