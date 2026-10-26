import hashlib
import base64
from io import BytesIO
from tempfile import TemporaryDirectory
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from PIL import Image

from .models import ArticlePage, MCPConnection, MCPDraftRequest
from .tests import TEST_STORAGE


@override_settings(STORAGES=TEST_STORAGE, PUBLIC_URL='http://localhost:8001')
class MCPTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('bootstrap_journal', verbosity=0)
        cls.owner = get_user_model().objects.create_superuser('mcp-owner', 'mcp@example.test', 'test-only-password')

    def setUp(self):
        self.media = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media.name)
        self.media_override.enable()
        self.addCleanup(self.media.cleanup)
        self.addCleanup(self.media_override.disable)
        self.connection, self.token = MCPConnection.issue(user=self.owner, name='Test', can_write=True,
            expires_at=timezone.now() + timedelta(hours=1))
        self.client = Client(enforce_csrf_checks=True)

    def rpc(self, method, params=None, token=None, **headers):
        return self.client.post('/mcp/', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or {}}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + (token or self.token), **headers)

    def draft(self, **changes):
        args = {'request_key': 'example-1', 'title': 'An MCP draft', 'intro': 'Created over MCP.',
            'category_slug': 'technology', 'sections': [{'type': 'paragraph', 'text': 'A useful paragraph. <script>alert(1)</script>'}]}
        args.update(changes)
        return self.rpc('tools/call', {'name': 'create_article_draft', 'arguments': args}).json()['result']

    def test_handshake_and_tools(self):
        data = self.rpc('initialize', {'protocolVersion': '2025-11-25'}).json()['result']
        self.assertEqual(data['protocolVersion'], '2025-11-25')
        self.assertIn('tools', data['capabilities'])
        names = [tool['name'] for tool in self.rpc('tools/list').json()['result']['tools']]
        self.assertIn('create_article_draft', names)
        self.assertNotIn('publish_article', names)
        self.assertEqual(self.client.get('/mcp/').status_code, 405)

    def test_draft_is_private_escaped_and_retry_safe(self):
        first = self.draft()
        self.assertFalse(first['isError'])
        article_id = first['structuredContent']['article']['id']
        self.assertFalse(ArticlePage.objects.get(pk=article_id).live)
        self.assertEqual(self.client.get('/blog/an-mcp-draft/').status_code, 404)
        self.assertNotContains(self.client.get('/blog/feed/'), 'An MCP draft')
        second = self.draft()
        self.assertTrue(second['structuredContent']['reused'])
        self.assertEqual(second['structuredContent']['article']['id'], article_id)
        self.assertEqual(MCPDraftRequest.objects.count(), 1)
        self.assertTrue(self.draft(title='Different title')['isError'])
        body = self.rpc('tools/call', {'name': 'get_article', 'arguments': {'article_id': article_id}}).json()
        text = body['result']['structuredContent']['article']['body'][0]['value']
        self.assertIn('&lt;script&gt;', text)
        self.assertNotIn('<script>', text)

    def test_invalid_content_does_not_create_pages(self):
        for changes in [{'sections': []}, {'title': '  '}, {'category_slug': 'no-such-category'}, {'live': True}]:
            self.assertTrue(self.draft(**changes)['isError'])
        self.assertFalse(MCPDraftRequest.objects.exists())

    def test_bearer_required_cookie_is_not_enough(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post('/mcp/', '{}', content_type='application/json').status_code, 401)
        self.assertEqual(self.rpc('ping', token='wrong').status_code, 401)
        self.assertEqual(self.rpc('ping', HTTP_ORIGIN='https://untrusted.example').status_code, 403)
        self.assertEqual(self.rpc('ping', HTTP_ORIGIN='http://localhost:8001').status_code, 200)
        self.assertEqual(self.connection.token_hash, hashlib.sha256(self.token.encode()).hexdigest())

    def test_revoked_expired_and_disabled_users_are_denied(self):
        for field, value in [('revoked_at', timezone.now()), ('expires_at', timezone.now() - timedelta(seconds=1))]:
            MCPConnection.objects.filter(pk=self.connection.pk).update(**{field: value})
            self.assertEqual(self.rpc('ping').status_code, 401)
            self.connection.save()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        self.assertEqual(self.rpc('ping').status_code, 401)

    def test_read_only_and_page_permissions(self):
        self.connection.can_write = False
        self.connection.save()
        names = [t['name'] for t in self.rpc('tools/list').json()['result']['tools']]
        self.assertNotIn('create_article_draft', names)
        self.assertTrue(self.draft()['isError'])
        self.connection.can_write = True
        self.connection.save()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_superuser=False)
        self.assertTrue(self.draft()['isError'])
        result = self.rpc('tools/call', {'name': 'list_articles', 'arguments': {}}).json()['result']
        self.assertEqual(result['structuredContent']['articles'], [])

    def test_malformed_requests_and_notifications(self):
        response = self.client.post('/mcp/', '{', content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/mcp/', json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(self.rpc('nonexistent').json()['error']['code'], -32601)
        response = self.client.post('/mcp/', 'x' * 3000001, content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 413)

    def test_upload_image_and_create_rich_draft(self):
        output = BytesIO()
        Image.new('RGB', (180, 120), '#355a36').save(output, format='PNG')
        arguments = {'title': 'Test editorial image', 'image_base64': base64.b64encode(output.getvalue()).decode()}
        upload = self.rpc('tools/call', {'name': 'upload_image', 'arguments': arguments}).json()['result']
        self.assertFalse(upload['isError'], upload)
        image_id = upload['structuredContent']['image_id']
        retry = self.rpc('tools/call', {'name': 'upload_image', 'arguments': arguments}).json()['result']
        self.assertEqual(retry['structuredContent']['image_id'], image_id)
        self.assertTrue(retry['structuredContent']['reused'])
        result = self.draft(cover_image_id=image_id, cover_alt='An editorial illustration',
            sections=[{'type': 'quote', 'text': 'An original thought.', 'attribution': 'From this article'},
                {'type': 'image', 'image_id': image_id, 'alt': 'An accessible description', 'caption': 'Illustration.'}])
        self.assertFalse(result['isError'], result)
        article = ArticlePage.objects.get(pk=result['structuredContent']['article']['id'])
        self.assertFalse(article.live)
        self.assertEqual(article.cover_id, image_id)
        self.assertTrue(article.cover.file.name.endswith('.webp'))
        draft = article.get_latest_revision_as_object()
        self.assertEqual(draft.body[0].value['attribution'], 'From this article')
        self.assertEqual(draft.body[1].value['image'].pk, image_id)
        self.assertTrue(self.draft(request_key='no-alt', cover_image_id=image_id)['isError'])

    def test_upload_validation_and_permissions(self):
        for data in ['not-base64', base64.b64encode(b'<svg>invalid</svg>').decode()]:
            result = self.rpc('tools/call', {'name': 'upload_image', 'arguments': {'title': 'Invalid', 'image_base64': data}}).json()['result']
            self.assertTrue(result['isError'])
        self.connection.can_write = False
        self.connection.save()
        result = self.rpc('tools/call', {'name': 'upload_image', 'arguments': {'title': 'Blocked', 'image_base64': 'AAAA'}}).json()['result']
        self.assertTrue(result['isError'])
