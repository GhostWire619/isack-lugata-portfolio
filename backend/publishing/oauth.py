"""OAuth/PKCE and registration are handled by Django OAuth Toolkit."""
import hashlib
import json
import secrets
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.views import AuthorizationView
from oauth2_provider.models import get_access_token_model
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
from .models import MCPConnection


def resource_uri():
    return settings.PUBLIC_URL + '/mcp'


def connection_for(user, application, scopes, reconnect=False):
    connection, _ = MCPConnection.objects.get_or_create(user=user, oauth_application=application,
        defaults={'name': application.name[:100], 'token_hash': hashlib.sha256(secrets.token_bytes(40)).hexdigest(),
            'can_write': 'articles:write' in scopes, 'can_publish': 'articles:publish' in scopes,
            'can_analytics': 'analytics:read' in scopes,
            'expires_at': timezone.now() + timedelta(days=30)})
    if reconnect:
        connection.revoked_at = None
        connection.can_write = 'articles:write' in scopes
        connection.can_publish = 'articles:publish' in scopes
        connection.can_analytics = 'analytics:read' in scopes
        connection.expires_at = timezone.now() + timedelta(days=30)
        connection.save()
    return connection


class JournalOAuthValidator(OAuth2Validator):
    def _validate_resource_uris(self, request, resources):
        super()._validate_resource_uris(request, resources)
        if any(value.rstrip('/') != resource_uri() for value in resources):
            raise CustomOAuth2Error(error='invalid_target', description='This authorization server issues tokens only for the journal MCP endpoint.', request=request)

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        resources = getattr(request, 'resource', None) or [resource_uri()]
        if isinstance(resources, str):
            resources = [resources]
        self._validate_resource_uris(request, resources)
        request.resource = resources
        return super().save_authorization_code(client_id, code, request, *args, **kwargs)

    def _check_and_set_request_resource(self, request):
        super()._check_and_set_request_resource(request)
        if not request.resource:
            request.resource = [resource_uri()]


class JournalAuthorizationView(AuthorizationView):
    template_name = 'publishing/authorize.html'

    def form_valid(self, form):
        scopes = form.cleaned_data['scope'].split()
        if not self.request.POST.get('allow_publish'):
            scopes = [scope for scope in scopes if scope != 'articles:publish']
            form.cleaned_data['scope'] = ' '.join(scopes)
        response = super().form_valid(form)
        if form.cleaned_data.get('allow') and response.status_code == 302 and 'code=' in response.get('Location', ''):
            from oauth2_provider.models import get_application_model
            application = get_application_model().objects.get(client_id=form.cleaned_data['client_id'])
            connection_for(self.request.user, application, scopes, reconnect=True)
        return response


class RegistrationPermission:
    def has_permission(self, request):
        if int(request.META.get('CONTENT_LENGTH') or 0) > 16384:
            return False
        try:
            data = json.loads(request.body)
            if not isinstance(data, dict):
                return False
            redirects = data.get('redirect_uris', [])
            if not isinstance(redirects, list) or not 1 <= len(redirects) <= 5:
                return False
            for uri in redirects:
                parsed = urlsplit(uri)
                if len(uri) > 2048 or parsed.username or parsed.password or parsed.fragment or not parsed.hostname:
                    return False
                if parsed.scheme != 'https' and not (settings.DEBUG and parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1', '::1'}):
                    return False
            if set(data.get('grant_types', ['authorization_code'])) - {'authorization_code', 'refresh_token'}:
                return False
            if set(data.get('response_types', ['code'])) != {'code'}:
                return False
        except (ValueError, TypeError, AttributeError):
            return False
        key = 'oauth-register:' + hashlib.sha256(request.META.get('REMOTE_ADDR', '').encode()).hexdigest()
        cache.add(key, 0, 3600)
        try:
            return cache.incr(key) <= 30
        except ValueError:
            return False


def authenticate(token):
    access = get_access_token_model().objects.select_related('application', 'user').filter(
        token_checksum=hashlib.sha256(token.encode()).hexdigest()).first()
    if not access or not access.user or not access.user.is_active or not access.user.is_staff or not access.is_valid(['articles:read']):
        return None
    if not access.resource or any(value.rstrip('/') != resource_uri() for value in access.resource):
        return None
    connection = connection_for(access.user, access.application, access.scope.split())
    if connection.revoked_at or connection.expires_at <= timezone.now():
        return None
    # The current token's scope controls each request, even after a narrower grant.
    connection.can_write = 'articles:write' in access.scope.split()
    connection.can_publish = 'articles:publish' in access.scope.split()
    connection.can_analytics = 'analytics:read' in access.scope.split()
    return connection
