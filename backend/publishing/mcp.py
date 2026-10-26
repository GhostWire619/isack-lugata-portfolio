"""Stateless MCP Streamable HTTP. Bearer credentials never inherit browser sessions.

Only read and draft creation are exposed: publishing remains an authenticated
Studio action. JSON responses are used; server-initiated streams are not needed.
"""
import hashlib
import json
import logging
from typing import Literal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel, ConfigDict, Field, ValidationError as InputError
from wagtail.permission_policies.pages import PagePermissionPolicy

from .models import ArticlePage, Category, JournalIndexPage, MCPConnection, MCPDraftRequest
from .studio import can_write

logger = logging.getLogger(__name__)
VERSIONS = {'2025-11-25', '2025-06-18', '2025-03-26'}


class Arguments(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ListArguments(Arguments):
    limit: int = Field(default=20, ge=1, le=50)
    after_id: int = Field(default=0, ge=0)


class GetArguments(Arguments):
    article_id: int = Field(gt=0)


class Section(Arguments):
    type: Literal['heading', 'paragraph', 'code']
    text: str = Field(min_length=1, max_length=10000)


class DraftArguments(Arguments):
    request_key: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    title: str = Field(min_length=1, max_length=200)
    intro: str = Field(min_length=1, max_length=350)
    category_slug: str | None = Field(default=None, max_length=100)
    sections: list[Section] = Field(min_length=1, max_length=80)


TOOLS = {
    'list_articles': (ListArguments, 'List articles accessible to this connection, including drafts. Use after_id for pagination.'),
    'get_article': (GetArguments, 'Read the latest saved draft of an accessible article.'),
    'create_article_draft': (DraftArguments, 'Create an unpublished article for review in Studio. Plain text sections only. Reuse request_key for safe retries; never publishes.'),
}


def accessible(user):
    return PagePermissionPolicy(ArticlePage).instances_user_has_any_permission_for(user, {'change'})


def serialize(article, include_body=False):
    draft = article.get_latest_revision_as_object()
    result = {'id': article.pk, 'title': draft.title, 'intro': draft.intro,
        'live': article.live, 'has_unpublished_changes': article.has_unpublished_changes,
        'editor_url': settings.PUBLIC_URL.rstrip('/') + reverse('wagtailadmin_pages:edit', args=[article.pk]),
        'category_slug': draft.category.slug if draft.category_id else None}
    if include_body:
        result['body'] = draft.body.get_prep_value()
    return result


def call_tool(connection, name, raw):
    if name not in TOOLS or (name == 'create_article_draft' and not connection.can_write):
        raise ValueError('Tool is unavailable for this connection.')
    args = TOOLS[name][0].model_validate(raw)
    user = connection.user
    if name == 'list_articles':
        articles = list(accessible(user).filter(pk__gt=args.after_id).order_by('pk')[:args.limit])
        return {'articles': [serialize(article) for article in articles],
            'next_after_id': articles[-1].pk if len(articles) == args.limit else None}
    if name == 'get_article':
        article = accessible(user).filter(pk=args.article_id).first()
        if not article:
            raise ValueError('Article was not found or access is denied.')
        return {'article': serialize(article, True)}
    payload_hash = hashlib.sha256(args.model_dump_json().encode()).hexdigest()
    with transaction.atomic():
        # Serialize tree insertion and retries for a connection on PostgreSQL.
        MCPConnection.objects.select_for_update().get(pk=connection.pk)
        journal = JournalIndexPage.objects.select_for_update().first()
        if not can_write(user, journal):
            raise ValueError('This account cannot create journal articles.')
        previous = MCPDraftRequest.objects.filter(connection=connection, request_key=args.request_key).first()
        if previous:
            if previous.payload_hash != payload_hash:
                raise ValueError('request_key was already used with different content.')
            if not accessible(user).filter(pk=previous.article_id).exists():
                raise ValueError('Article access is denied.')
            return {'article': serialize(previous.article, True), 'reused': True}
        category = None
        if args.category_slug:
            category = Category.objects.filter(slug=args.category_slug).first()
            if not category:
                raise ValueError('Unknown category. Use list_categories to choose an existing category.')
        if not args.title.strip() or not args.intro.strip() or any(not s.text.strip() for s in args.sections):
            raise ValueError('Title, introduction and sections must contain text.')
        slug_base = slugify(args.title)[:180] or 'article'
        slug, suffix = slug_base, 2
        while journal.get_children().filter(slug=slug).exists():
            slug = f'{slug_base}-{suffix}'
            suffix += 1
        body = [(s.type, '<p>' + str(escape(s.text)).replace('\n\n', '</p><p>').replace('\n', '<br/>') + '</p>'
            if s.type == 'paragraph' else s.text) for s in args.sections]
        article = ArticlePage(title=args.title.strip(), slug=slug, intro=args.intro.strip(),
            category=category, owner=user, live=False, body=body, search_description=args.intro.strip()[:255])
        article.full_clean(exclude=['path', 'depth'])
        journal.add_child(instance=article)
        article.save_revision(user=user, log_action=True)
        MCPDraftRequest.objects.create(connection=connection, request_key=args.request_key,
            payload_hash=payload_hash, article=article)
        return {'article': serialize(article, True), 'reused': False}


def rpc(request, connection):
    try:
        message = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Invalid JSON'}}, status=400)
    if not isinstance(message, dict) or message.get('jsonrpc') != '2.0' or not isinstance(message.get('method'), str):
        return JsonResponse({'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request'}}, status=400)
    request_id = message.get('id')
    method, params = message['method'], message.get('params', {})
    def result(value):
        return JsonResponse({'jsonrpc': '2.0', 'id': request_id, 'result': value})
    def error(code, text):
        return JsonResponse({'jsonrpc': '2.0', 'id': request_id, 'error': {'code': code, 'message': text}})
    if not isinstance(params, dict):
        return error(-32602, 'Parameters must be an object.')
    if 'id' not in message:
        return HttpResponse(status=202)
    if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
        return error(-32600, 'Invalid request ID.')
    if method == 'initialize':
        version = params.get('protocolVersion')
        return result({'protocolVersion': version if version in VERSIONS else '2025-11-25',
            'capabilities': {'tools': {'listChanged': False}},
            'serverInfo': {'name': 'isack-journal', 'version': '1.0.0'},
            'instructions': 'Articles created here remain drafts. Review and publish in Studio.'})
    if request.headers.get('MCP-Protocol-Version', '2025-03-26') not in VERSIONS:
        return error(-32600, 'Unsupported MCP protocol version.')
    if method == 'ping':
        return result({})
    if method == 'tools/list':
        definitions = [{'name': name, 'description': description, 'inputSchema': model.model_json_schema(),
            'annotations': {'readOnlyHint': name != 'create_article_draft', 'destructiveHint': False,
                'idempotentHint': True, 'openWorldHint': False}}
            for name, (model, description) in TOOLS.items()
            if name != 'create_article_draft' or connection.can_write]
        definitions.append({'name': 'list_categories', 'description': 'List available article categories.',
            'inputSchema': Arguments.model_json_schema(), 'annotations': {'readOnlyHint': True, 'openWorldHint': False}})
        return result({'tools': definitions})
    if method == 'tools/call':
        try:
            name = params.get('name')
            if not isinstance(name, str):
                raise ValueError('Tool name must be a string.')
            if name == 'list_categories':
                Arguments.model_validate(params.get('arguments', {}))
                value = {'categories': list(Category.objects.values('name', 'slug'))}
            else:
                value = call_tool(connection, name, params.get('arguments', {}))
            return result({'content': [{'type': 'text', 'text': json.dumps(value)}], 'structuredContent': value, 'isError': False})
        except (InputError, ValueError, ValidationError) as exc:
            return result({'content': [{'type': 'text', 'text': str(exc)}], 'isError': True})
        except Exception:
            logger.exception('MCP tool failed for connection %s', connection.pk)
            return result({'content': [{'type': 'text', 'text': 'The operation could not be completed. Retry with the same request_key.'}], 'isError': True})
    return error(-32601, 'Method not found.')


@csrf_exempt
def endpoint(request):
    if request.method != 'POST':
        response = HttpResponse(status=405)
        response['Allow'] = 'POST'
    elif request.headers.get('Origin') and request.headers['Origin'] != settings.PUBLIC_URL.rstrip('/'):
        response = HttpResponse('Origin is not allowed.', status=403)
    elif request.content_type != 'application/json':
        response = HttpResponse('Use application/json.', status=415)
    elif int(request.META.get('CONTENT_LENGTH') or 0) > 131072:
        response = HttpResponse('Request is too large.', status=413)
    else:
        auth = request.headers.get('Authorization', '')
        token = auth[7:] if auth.startswith('Bearer ') else ''
        connection = MCPConnection.objects.select_related('user').filter(
            token_hash=hashlib.sha256(token.encode()).hexdigest(), revoked_at__isnull=True,
            expires_at__gt=timezone.now(), user__is_active=True, user__is_staff=True).first() if token else None
        if not connection:
            response = HttpResponse('A valid journal access token is required.', status=401)
            response['WWW-Authenticate'] = 'Bearer realm="journal"'
        else:
            MCPConnection.objects.filter(pk=connection.pk).update(last_used_at=timezone.now())
            response = rpc(request, connection)
    response['Cache-Control'] = 'no-store'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response
