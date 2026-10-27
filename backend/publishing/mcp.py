"""Stateless MCP Streamable HTTP. Bearer credentials never inherit browser sessions.

Drafts are the default; publishing needs an explicit connection scope and native
page permission. JSON responses are used; server-initiated streams are not needed.
"""
import hashlib
import base64
import binascii
from io import BytesIO
import json
import logging
import warnings
from typing import Annotated, Literal, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel, ConfigDict, Field, ValidationError as InputError
from wagtail.permission_policies.pages import PagePermissionPolicy
from wagtail.images import get_image_model, get_permission_policy
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import ArticlePage, Category, JournalIndexPage, MCPConnection, MCPDraftRequest, MCPImageUpload, MCPAction
from .studio import can_write
from .links import paragraph_html

logger = logging.getLogger(__name__)
VERSIONS = {'2025-11-25', '2025-06-18', '2025-03-26'}


class Arguments(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ListArguments(Arguments):
    limit: int = Field(default=20, ge=1, le=50)
    after_id: int = Field(default=0, ge=0)


class GetArguments(Arguments):
    article_id: int = Field(gt=0)


class TextSection(Arguments):
    type: Literal['heading', 'paragraph', 'code']
    text: str = Field(min_length=1, max_length=10000, description='Paragraphs support clickable URLs and [link labels](https://example.com). Raw HTML is escaped. Headings and code remain plain text.')


class QuoteSection(Arguments):
    type: Literal['quote']
    text: str = Field(min_length=1, max_length=2000)
    attribution: str = Field(default='', max_length=250)


class ImageSection(Arguments):
    type: Literal['image']
    image_id: int = Field(gt=0)
    alt: str = Field(min_length=1, max_length=250)
    caption: str = Field(default='', max_length=350)


class UploadArguments(Arguments):
    title: str = Field(min_length=1, max_length=250)
    image_base64: str = Field(min_length=4, max_length=2800000)


Section = Annotated[Union[TextSection, QuoteSection, ImageSection], Field(discriminator='type')]


class DraftArguments(Arguments):
    request_key: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    title: str = Field(min_length=1, max_length=200)
    intro: str = Field(min_length=1, max_length=350)
    category_slug: str | None = Field(default=None, max_length=100)
    cover_image_id: int | None = Field(default=None, gt=0)
    cover_alt: str = Field(default='', max_length=250)
    cover_caption: str = Field(default='', max_length=350)
    sections: list[Section] = Field(min_length=1, max_length=80)


class UpdateArguments(DraftArguments):
    article_id: int = Field(gt=0)
    expected_revision_id: int = Field(gt=0)


class PublishArguments(GetArguments):
    request_key: str = Field(min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    expected_revision_id: int = Field(gt=0)


class ScheduleArguments(PublishArguments):
    publish_at: str = Field(min_length=20, max_length=40, description='Future ISO 8601 timestamp with timezone, e.g. 2027-01-01T09:00:00+03:00.')


class AnalyticsArguments(Arguments):
    days: int = Field(default=30, ge=1, le=90)
    article_id: int | None = Field(default=None, gt=0)


TOOLS = {
    'update_article_draft': (UpdateArguments, 'Replace an article draft with complete content. Requires expected_revision_id from get_article to prevent overwriting newer changes. Never publishes.'),
    'publish_article': (PublishArguments, 'Publish the specified saved revision immediately. Requires explicit direct-publishing permission. This makes content public; use only when the owner requests publication.'),
    'schedule_article': (ScheduleArguments, 'Schedule a saved revision for a future timezone-aware timestamp. Requires explicit direct-publishing permission.'),
    'get_analytics': (AnalyticsArguments, 'Read actual aggregate page views, active reading time, popular pages and referrer domains over 1–90 days. No unique-person counts or identifying visitor data.'),
    'list_articles': (ListArguments, 'List articles accessible to this connection, including drafts. Use after_id for pagination.'),
    'get_article': (GetArguments, 'Read the latest saved draft of an accessible article.'),
    'create_article_draft': (DraftArguments, 'Create an unpublished article for review in Studio. Supports text, attributed quotations, images and a cover. Upload images first. Reuse request_key for safe retries; never publishes.'),
    'upload_image': (UploadArguments, 'Upload a base64 JPEG, PNG or WebP image (maximum 2 MB, 40 megapixels). Images are resized, stripped of metadata and compressed to WebP. Identical retries reuse the image. Returns image_id for covers and image sections.'),
}

WRITE_TOOLS = {'create_article_draft', 'upload_image', 'update_article_draft'}
PUBLISH_TOOLS = {'publish_article', 'schedule_article'}


def available(connection, name):
    return (name in TOOLS and (name not in WRITE_TOOLS or connection.can_write)
        and (name not in PUBLISH_TOOLS or connection.can_publish)
        and (name != 'get_analytics' or (connection.can_analytics and connection.user.has_perm('publishing.view_pageview'))))


def draft_content(user, args):
    category = Category.objects.filter(slug=args.category_slug).first() if args.category_slug else None
    if args.category_slug and not category:
        raise ValueError('Unknown category. Use list_categories to choose an existing category.')
    if not args.title.strip() or not args.intro.strip() or any(not s.text.strip() for s in args.sections if hasattr(s, 'text')):
        raise ValueError('Title, introduction and sections must contain text.')
    body = []
    for section in args.sections:
        if section.type == 'image':
            if not section.alt.strip():
                raise ValueError('Each image needs an accessible description.')
            body.append(('image', {'image': choose_image(user, section.image_id), 'alt': section.alt, 'caption': section.caption}))
        elif section.type == 'quote':
            body.append(('quote', {'quote': section.text, 'attribution': section.attribution}))
        elif section.type == 'paragraph':
            body.append(('paragraph', paragraph_html(section.text)))
        else:
            body.append((section.type, section.text))
    return dict(title=args.title.strip(), intro=args.intro.strip(), category=category, body=body,
        search_description=args.intro.strip()[:255], cover=choose_image(user, args.cover_image_id) if args.cover_image_id else None,
        cover_alt=args.cover_alt, cover_caption=args.cover_caption)


@transaction.atomic
def change_article(connection, name, args):
    from django.utils.dateparse import parse_datetime
    MCPConnection.objects.select_for_update().get(pk=connection.pk)
    article = accessible(connection.user).select_for_update().filter(pk=args.article_id).first()
    if not article:
        raise ValueError('Article was not found or access is denied.')
    digest = hashlib.sha256(args.model_dump_json().encode()).hexdigest()
    previous = MCPAction.objects.filter(connection=connection, request_key=args.request_key).first()
    if previous:
        if previous.payload_hash != digest or previous.tool != name:
            raise ValueError('request_key was already used with different content.')
        return {'article': serialize(article, True), 'reused': True}
    if article.latest_revision_id != args.expected_revision_id:
        raise ValueError('The article has changed. Read it again before editing or publishing.')
    draft = article.get_latest_revision_as_object()
    if name == 'update_article_draft':
        for field, value in draft_content(connection.user, args).items():
            setattr(draft, field, value)
        draft.full_clean()
        draft.save_revision(user=connection.user, log_action=True)
    else:
        if not article.permissions_for_user(connection.user).can_publish():
            raise ValueError('This account cannot publish this article.')
        draft.full_clean()
        if name == 'schedule_article':
            when = parse_datetime(args.publish_at)
            if not when or timezone.is_naive(when) or when <= timezone.now():
                raise ValueError('Choose a future date and include a timezone offset.')
            draft.go_live_at = when
            revision = draft.save_revision(user=connection.user, log_action=True)
        else:
            # An existing schedule must not silently defer an explicit publish-now request.
            draft.go_live_at = None
            revision = draft.save_revision(user=connection.user, log_action=True)
        revision.publish(user=connection.user)
    MCPAction.objects.create(connection=connection, request_key=args.request_key, payload_hash=digest, tool=name, article=article)
    article.refresh_from_db()
    return {'article': serialize(article, True), 'reused': False}


def choose_image(user, image_id):
    image = get_permission_policy().instances_user_has_any_permission_for(user, {'choose', 'change'}).filter(pk=image_id).first()
    if not image:
        raise ValueError('Image was not found or access is denied.')
    return image


def upload_image(connection, args):
    if not args.title.strip():
        raise ValueError('The image title must contain text.')
    policy = get_permission_policy()
    collection = policy.collections_user_has_permission_for(connection.user, 'add').order_by('depth', 'pk').first()
    if not collection or not can_write(connection.user, JournalIndexPage.objects.first()):
        raise ValueError('This account cannot upload journal images.')
    try:
        source = base64.b64decode(args.image_base64, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError('Invalid base64 image.')
    if len(source) > 2 * 1024 * 1024:
        raise ValueError('Image exceeds 2 MB. Compress it before uploading.')
    digest = hashlib.sha256(source).hexdigest()
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        try:
            picture = Image.open(BytesIO(source))
            if picture.format not in {'JPEG', 'PNG', 'WEBP'} or picture.width * picture.height > 40000000:
                raise ValueError('Use JPEG, PNG or WebP images up to 40 megapixels.')
            picture.load()
            picture = ImageOps.exif_transpose(picture).convert('RGB')
            picture.thumbnail((2560, 2560))
            output = BytesIO()
            picture.save(output, format='WEBP', quality=85, method=6)
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise ValueError('The image could not be decoded safely.')
    with transaction.atomic():
        MCPConnection.objects.select_for_update().get(pk=connection.pk)
        previous = MCPImageUpload.objects.filter(connection=connection, content_hash=digest).first()
        if previous:
            image = choose_image(connection.user, previous.image_id)
        else:
            image = get_image_model()(title=args.title.strip(), collection=collection, uploaded_by_user=connection.user,
                width=picture.width, height=picture.height)
            filename = f'journal-{digest[:20]}.webp'
            image.file.save(filename, ContentFile(output.getvalue(), name=filename), save=False)
            try:
                image.save()
                MCPImageUpload.objects.create(connection=connection, content_hash=digest, image=image)
            except Exception:
                image.file.delete(save=False)
                raise
    return {'image_id': image.pk, 'title': image.title, 'width': image.width, 'height': image.height, 'reused': bool(previous)}


def accessible(user):
    return PagePermissionPolicy(ArticlePage).instances_user_has_any_permission_for(user, {'change'})


def serialize(article, include_body=False):
    draft = article.get_latest_revision_as_object()
    result = {'id': article.pk, 'title': draft.title, 'intro': draft.intro,
        'revision_id': article.latest_revision_id,
        'scheduled_at': article.latest_revision.approved_go_live_at.isoformat() if article.latest_revision and article.latest_revision.approved_go_live_at else None,
        'live': article.live, 'has_unpublished_changes': article.has_unpublished_changes,
        'editor_url': settings.PUBLIC_URL.rstrip('/') + reverse('wagtailadmin_pages:edit', args=[article.pk]),
        'category_slug': draft.category.slug if draft.category_id else None}
    result.update({'cover_image_id': draft.cover_id, 'cover_alt': draft.cover_alt, 'cover_caption': draft.cover_caption})
    if include_body:
        result['body'] = draft.body.get_prep_value()
    return result


def call_tool(connection, name, raw):
    if not available(connection, name):
        raise ValueError('Tool is unavailable for this connection.')
    args = TOOLS[name][0].model_validate(raw)
    user = connection.user
    if name in PUBLISH_TOOLS or name == 'update_article_draft':
        return change_article(connection, name, args)
    if name == 'get_analytics':
        from .analytics import report
        path = None
        if args.article_id:
            article = accessible(user).filter(pk=args.article_id).first()
            if not article:
                raise ValueError('Article was not found or access is denied.')
            path = '/blog/' + article.slug + '/'
        return report(args.days, path)
    if name == 'upload_image':
        return upload_image(connection, args)
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
        if not args.title.strip() or not args.intro.strip() or any(not s.text.strip() for s in args.sections if hasattr(s, 'text')):
            raise ValueError('Title, introduction and sections must contain text.')
        slug_base = slugify(args.title)[:180] or 'article'
        slug, suffix = slug_base, 2
        while journal.get_children().filter(slug=slug).exists():
            slug = f'{slug_base}-{suffix}'
            suffix += 1
        body = []
        for section in args.sections:
            if section.type == 'image':
                if not section.alt.strip():
                    raise ValueError('Each image needs an accessible description.')
                body.append(('image', {'image': choose_image(user, section.image_id), 'alt': section.alt, 'caption': section.caption}))
            elif section.type == 'quote':
                body.append(('quote', {'quote': section.text, 'attribution': section.attribution}))
            elif section.type == 'paragraph':
                body.append(('paragraph', paragraph_html(section.text)))
            else:
                body.append((section.type, section.text))
        cover = choose_image(user, args.cover_image_id) if args.cover_image_id else None
        article = ArticlePage(title=args.title.strip(), slug=slug, intro=args.intro.strip(),
            category=category, owner=user, live=False, body=body, search_description=args.intro.strip()[:255],
            cover=cover, cover_alt=args.cover_alt, cover_caption=args.cover_caption)
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
            'serverInfo': {'name': 'isack-journal', 'version': '1.1.0'},
            'instructions': 'Create and update tools save private drafts. Review in Studio. Publish/schedule tools are available only with separately granted direct-publishing permission; use them only when the owner explicitly requests publication.'})
    if request.headers.get('MCP-Protocol-Version', '2025-03-26') not in VERSIONS:
        return error(-32600, 'Unsupported MCP protocol version.')
    if method == 'ping':
        return result({})
    if method == 'tools/list':
        definitions = [{'name': name, 'description': description, 'inputSchema': model.model_json_schema(),
            'annotations': {'readOnlyHint': name not in WRITE_TOOLS | PUBLISH_TOOLS, 'destructiveHint': name in PUBLISH_TOOLS,
                'idempotentHint': True, 'openWorldHint': name in PUBLISH_TOOLS}}
            for name, (model, description) in TOOLS.items()
            if available(connection, name)]
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
    elif request.headers.get('Origin') and request.headers['Origin'] not in settings.MCP_ALLOWED_ORIGINS:
        response = HttpResponse('Origin is not allowed.', status=403)
    elif request.content_type != 'application/json':
        response = HttpResponse('Use application/json.', status=415)
    elif int(request.META.get('CONTENT_LENGTH') or 0) > 3000000:
        response = HttpResponse('Request is too large.', status=413)
    else:
        auth = request.headers.get('Authorization', '')
        token = auth[7:] if auth.startswith('Bearer ') else ''
        connection = MCPConnection.objects.select_related('user').filter(
            token_hash=hashlib.sha256(token.encode()).hexdigest(), revoked_at__isnull=True,
            expires_at__gt=timezone.now(), user__is_active=True, user__is_staff=True, oauth_application__isnull=True).first() if token else None
        if not connection and token:
            from .oauth import authenticate
            connection = authenticate(token)
        if not connection:
            response = HttpResponse('A valid journal access token is required.', status=401)
            response['WWW-Authenticate'] = f'Bearer realm="journal", resource_metadata="{settings.PUBLIC_URL}/.well-known/oauth-protected-resource/mcp"'
        else:
            MCPConnection.objects.filter(pk=connection.pk).update(last_used_at=timezone.now())
            response = rpc(request, connection)
    response['Cache-Control'] = 'no-store'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response
