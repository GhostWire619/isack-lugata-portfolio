"""Correlated OAuth diagnostics without credentials, state, codes or raw URLs."""
from contextvars import ContextVar
import hashlib
import json
import logging
import re
from urllib.parse import urlsplit
from uuid import uuid4
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger('publishing.oauth_diagnostics')
current_request = ContextVar('journal_oauth_request', default=None)


def provider(client_id='', redirect_uri=''):
    for value in (client_id, redirect_uri):
        try:
            host = (urlsplit(value).hostname or '').lower()
        except ValueError:
            continue
        if host in {'claude.ai', 'claude.com'}:
            return 'Claude'
        if host in {'chatgpt.com', 'chat.openai.com'}:
            return 'ChatGPT'
    return 'Other'


def safe_description(description, request):
    text = str(description or '')[:1000]
    for values in (request.GET, request.POST):
        for name in ('state', 'code', 'code_challenge', 'client_secret', 'access_token', 'refresh_token', 'id_token', 'client_id', 'redirect_uri'):
            for value in values.getlist(name):
                if value:
                    text = text.replace(value, '[redacted]')
    return re.sub(r'https?://\S+', '[address redacted]', text)[:400]


def metadata_failed(client_id, error):
    request = current_request.get()
    # Derive a bounded category; never log exception text or the fetched URL.
    match = re.search(r'HTTP (\d{3})', str(error))
    details = {'metadata_error': type(error).__name__, 'metadata_http_status': int(match[1]) if match else None}
    if request is not None:
        request.oauth_metadata_failure = details
    logger.warning(json.dumps({'event': 'oauth.metadata_failed', 'at': timezone.now().isoformat(),
        'reference': getattr(request, 'oauth_reference', None), 'provider': provider(client_id), **details}, sort_keys=True))


class OAuthDiagnostics:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/admin/ai/authorize/' and not request.path.startswith('/oauth/'):
            return self.get_response(request)
        if request.method == 'OPTIONS':
            return self.get_response(request)
        request.oauth_reference = uuid4().hex[:16]
        token = current_request.set(request)
        response = None
        try:
            response = self.get_response(request)
            response['X-OAuth-Diagnostic-ID'] = request.oauth_reference
            error = getattr(request, 'oauth_failure', None)
            if not error and response.status_code >= 400:
                code = 'http_error'
                if not response.streaming and len(response.content) <= 4096:
                    try:
                        value = json.loads(response.content).get('error', '')
                        if isinstance(value, str) and re.fullmatch(r'[a-z_]{1,80}', value):
                            code = value
                    except (ValueError, AttributeError):
                        pass
                error = {'code': code}
            stage = 'authorize' if request.path == '/admin/ai/authorize/' else 'registration' if request.path.startswith('/oauth/register/') else 'token' if request.path == '/oauth/token/' else 'revoke'
            if error:
                client_id = request.GET.get('client_id', '') or request.POST.get('client_id', '')
                redirect_uri = request.GET.get('redirect_uri', '') or request.POST.get('redirect_uri', '')
                from oauth2_provider.models import get_application_model
                application = get_application_model().objects.filter(client_id=client_id).first() if client_id else None
                redirect_matches = None
                if application and redirect_uri:
                    from oauth2_provider.models import check_redirect_to_uri_allowed
                    try:
                        redirect_matches = check_redirect_to_uri_allowed(redirect_uri, application.redirect_uris.split())[0]
                    except ValueError:
                        redirect_matches = False
                method = request.GET.get('code_challenge_method') or request.POST.get('code_challenge_method') or 'missing'
                details = {'event': 'oauth.request_failed', 'at': timezone.now().isoformat(), 'reference': request.oauth_reference, 'stage': stage,
                    'http_status': response.status_code, 'provider': provider(client_id, redirect_uri),
                    'error_code': error['code'], 'description': error.get('description', ''),
                    'client_registered': bool(application),
                    'client_fingerprint': hashlib.sha256(client_id.encode()).hexdigest()[:12] if client_id else None,
                    'redirect_matches': redirect_matches,
                    'pkce_method': method if method in {'S256', 'plain', 'missing'} else 'unsupported',
                    **getattr(request, 'oauth_metadata_failure', {})}
                logger.warning(json.dumps(details, sort_keys=True))
                if request.user.is_authenticated and request.user.is_staff:
                    # Bound persistent diagnostics; anonymous token/registration failures stay in logs only.
                    key = f'oauth-diagnostic-count:{request.user.pk}'
                    cache.add(key, 0, 3600)
                    try:
                        if cache.incr(key) <= 50:
                            from .models import OAuthFailure
                            OAuthFailure.objects.create(reference=request.oauth_reference, user=request.user, details=details)
                    except Exception:
                        logger.exception('Could not persist OAuth diagnostic %s', request.oauth_reference)
            elif stage in {'registration', 'token'} and 200 <= response.status_code < 300:
                logger.info(json.dumps({'event': 'oauth.request_succeeded', 'at': timezone.now().isoformat(), 'reference': request.oauth_reference,
                    'stage': stage, 'http_status': response.status_code}, sort_keys=True))
            return response
        except Exception:
            # An observability failure must never replace an OAuth response.
            if response is None:
                raise
            logger.exception(json.dumps({'event': 'oauth.diagnostics_failed', 'reference': request.oauth_reference}))
            return response
        finally:
            current_request.reset(token)
