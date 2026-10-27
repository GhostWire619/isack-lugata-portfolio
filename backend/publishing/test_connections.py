import base64
import hashlib
import json
import secrets
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit, urlencode
from uuid import uuid4
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, Client, override_settings
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from oauth2_provider.models import AccessToken, Grant
from .models import MCPConnection, PageView, ArticlePage, JournalIndexPage
from .mcp import call_tool
from .tests import TEST_STORAGE


@override_settings(STORAGES=TEST_STORAGE, PUBLIC_URL='http://localhost:8001', MCP_ALLOWED_ORIGINS=['http://localhost:8001'])
class ConnectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('bootstrap_journal', verbosity=0)
        cls.owner = get_user_model().objects.create_superuser('oauth-owner', 'oauth@example.test', 'test-only-password')
        cls.device = TOTPDevice.objects.create(user=cls.owner, name='Test', confirmed=True)

    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        session = self.client.session
        session['otp_device_id'] = self.device.persistent_id
        session.save()

    def register(self):
        response = self.client.post('/oauth/register/', json.dumps({'client_name': 'Test AI',
            'redirect_uris': ['https://assistant.example/callback'], 'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['code'], 'token_endpoint_auth_method': 'none'}), content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()['client_id']

    def authorize(self, client_id, *, publish=False, resource='http://localhost:8001/mcp'):
        verifier = secrets.token_urlsafe(48)
        query = {'client_id': client_id, 'response_type': 'code', 'redirect_uri': 'https://assistant.example/callback',
            'scope': 'articles:read articles:write analytics:read articles:publish', 'state': 'checked-state',
            'code_challenge': base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode(),
            'code_challenge_method': 'S256', 'resource': resource}
        response = self.client.get('/admin/ai/authorize/?' + urlencode(query))
        self.assertEqual(response.status_code, 200, response.content)
        soup = BeautifulSoup(response.content, 'html.parser')
        form = {item['name']: item.get('value', '') for item in soup.select('form input[type=hidden]')}
        form['allow'] = 'true'
        if publish:
            form['allow_publish'] = 'on'
        response = self.client.post('/admin/ai/authorize/', form)
        self.assertEqual(response.status_code, 302, response.content)
        values = parse_qs(urlsplit(response['Location']).query)
        self.assertEqual(values.get('state'), ['checked-state'])
        self.assertIn('code', values, values)
        return values['code'][0], verifier

    def exchange(self, client_id, code, verifier, resource='http://localhost:8001/mcp'):
        return self.client.post('/oauth/token/', {'client_id': client_id, 'grant_type': 'authorization_code',
            'code': code, 'code_verifier': verifier, 'redirect_uri': 'https://assistant.example/callback', 'resource': resource})

    def test_oauth_pkce_scope_consent_refresh_and_revoke(self):
        client_id = self.register()
        code, verifier = self.authorize(client_id)
        response = self.exchange(client_id, code, verifier)
        self.assertEqual(response.status_code, 200, response.content)
        tokens = response.json()
        self.assertNotIn('articles:publish', tokens['scope'])
        rpc = self.client.post('/mcp', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])
        self.assertEqual(rpc.status_code, 200, rpc.content)
        names = [tool['name'] for tool in rpc.json()['result']['tools']]
        self.assertIn('get_analytics', names)
        self.assertIn('update_article_draft', names)
        self.assertNotIn('publish_article', names)
        self.assertEqual(self.exchange(client_id, code, verifier).status_code, 400)
        refreshed = self.client.post('/oauth/token/', {'client_id': client_id, 'grant_type': 'refresh_token', 'refresh_token': tokens['refresh_token']})
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotEqual(tokens['refresh_token'], refreshed.json()['refresh_token'])
        page = self.client.get('/admin/ai/')
        csrf = BeautifulSoup(page.content, 'html.parser').select_one('input[name=csrfmiddlewaretoken]')['value']
        connection = MCPConnection.objects.get(oauth_application__client_id=client_id)
        self.assertEqual(self.client.post('/admin/ai/', {'action': 'revoke', 'connection': connection.pk, 'csrfmiddlewaretoken': csrf}).status_code, 302)
        self.assertFalse(AccessToken.objects.filter(application__client_id=client_id).exists())
        denied = self.client.post('/oauth/token/', {'client_id': client_id, 'grant_type': 'refresh_token', 'refresh_token': refreshed.json()['refresh_token']})
        self.assertEqual(denied.status_code, 400)

    def test_pkce_and_resource_cannot_be_bypassed(self):
        client_id = self.register()
        code, verifier = self.authorize(client_id, publish=True)
        self.assertEqual(self.exchange(client_id, code, 'incorrect-verifier').status_code, 400)
        self.assertEqual(self.exchange(client_id, code, verifier, 'https://different.example/mcp').status_code, 400)
        response = self.exchange(client_id, code, verifier)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('articles:publish', response.json()['scope'])

    def test_metadata_and_registration_safety(self):
        metadata = self.client.get('/.well-known/oauth-authorization-server').json()
        self.assertEqual(metadata['code_challenge_methods_supported'], ['S256'])
        self.assertEqual(metadata['authorization_endpoint'], 'http://localhost:8001/admin/ai/authorize/')
        self.assertEqual(self.client.get('/.well-known/oauth-protected-resource/mcp').json()['resource'], 'http://localhost:8001/mcp')
        bad = self.client.post('/oauth/register/', json.dumps({'redirect_uris': ['javascript:alert(1)']}), content_type='application/json')
        self.assertIn(bad.status_code, [400, 401, 403])
        self.assertEqual(Client().get('/admin/ai/').status_code, 302)
        session = self.client.session
        session.pop('otp_device_id')
        session.save()
        self.assertRedirects(self.client.get('/admin/ai/'), '/security/verify/', fetch_redirect_response=False)

    def test_manual_token_is_shown_once_and_analytics_enforces_user_permission(self):
        page = self.client.get('/admin/ai/')
        csrf = BeautifulSoup(page.content, 'html.parser').select_one('input[name=csrfmiddlewaretoken]')['value']
        response = self.client.post('/admin/ai/', {'action': 'create', 'name': 'Draft helper', 'days': '7',
            'can_write': 'on', 'can_analytics': 'on', 'csrfmiddlewaretoken': csrf})
        self.assertEqual(response.status_code, 200)
        token = response.context['token']
        self.assertTrue(token.startswith('journal_'))
        self.assertContains(response, token)
        self.assertNotContains(self.client.get('/admin/ai/'), token)
        self.assertFalse(MCPConnection.objects.get(name='Draft helper').can_publish)
        self.assertEqual(self.client.post('/admin/ai/', {'action': 'create'}).status_code, 403)
        PageView.objects.create(id=uuid4(), path='/', seconds=20)
        connection = MCPConnection.objects.get(name='Draft helper')
        self.assertEqual(call_tool(connection, 'get_analytics', {})['views'], 1)
        json.dumps(call_tool(connection, 'get_analytics', {}))
        connection.can_analytics = False
        with self.assertRaises(ValueError):
            call_tool(connection, 'get_analytics', {})

    def test_draft_edit_publish_and_schedule_permissions(self):
        connection, _ = MCPConnection.issue(user=self.owner, name='Test', can_write=True,
            expires_at=timezone.now() + timedelta(hours=1))
        payload = {'request_key': 'create', 'title': 'A useful article', 'intro': 'Introduction.',
            'sections': [{'type': 'paragraph', 'text': 'Original text.'}]}
        article = call_tool(connection, 'create_article_draft', payload)['article']
        publish = {'article_id': article['id'], 'request_key': 'publish', 'expected_revision_id': article['revision_id']}
        with self.assertRaises(ValueError):
            call_tool(connection, 'publish_article', publish)
        connection.can_publish = True
        result = call_tool(connection, 'publish_article', publish)
        self.assertTrue(result['article']['live'])
        self.assertTrue(call_tool(connection, 'publish_article', publish)['reused'])
        update = dict(payload, request_key='edit', article_id=article['id'], expected_revision_id=result['article']['revision_id'],
            intro='Private new introduction.')
        edited = call_tool(connection, 'update_article_draft', update)['article']
        self.assertNotContains(Client().get('/blog/a-useful-article/'), 'Private new introduction.')
        self.assertTrue(call_tool(connection, 'update_article_draft', update)['reused'])
        with self.assertRaises(ValueError):
            call_tool(connection, 'update_article_draft', dict(update, request_key='stale'))
        when = timezone.now() + timedelta(days=2)
        scheduled = call_tool(connection, 'schedule_article', dict(publish, request_key='schedule',
            expected_revision_id=edited['revision_id'], publish_at=when.isoformat()))
        self.assertIsNotNone(scheduled['article']['scheduled_at'])


@override_settings(STORAGES=TEST_STORAGE, PUBLIC_URL='http://localhost:8001')
class AnalyticsTests(TestCase):
    def setUp(self):
        cache.clear()

    def event(self, data, **headers):
        return self.client.post('/events/', json.dumps(data), content_type='application/json', HTTP_ORIGIN='http://localhost:8001', **headers)

    def test_deduplicates_monotonic_metrics_without_visitor_identity(self):
        event = {'id': str(uuid4()), 'path': '/', 'referrer': 'https://search.example/?private=query'}
        self.assertEqual(self.event(event).status_code, 204)
        self.assertEqual(self.event(dict(event, seconds=45, progress=80)).status_code, 204)
        self.event(dict(event, seconds=10, progress=20))
        view = PageView.objects.get()
        self.assertEqual((view.seconds, view.progress, view.referrer), (45, 80, 'search.example'))
        from .analytics import report
        self.assertEqual(report()['views'], 1)
        self.assertEqual(report()['average_seconds'], 45)
        self.assertEqual(self.event(dict(event, path='/blog/')).status_code, 400)

    def test_rejects_private_paths_wrong_origins_and_invalid_data(self):
        for path in ['/admin/', '/security/verify/', '/blog/not-published/', '/?secret=1']:
            self.assertEqual(self.event({'id': str(uuid4()), 'path': path}).status_code, 400)
        self.assertEqual(self.client.post('/events/', '{}', content_type='application/json', HTTP_ORIGIN='https://other.example').status_code, 403)
        self.assertFalse(PageView.objects.exists())
