import json
from django.conf import settings
from .models import ArticlePage, PublicationSettings


def journal_context(request):
    publication = PublicationSettings.for_request(request)
    return {'publication': publication, 'public_origin': settings.PUBLIC_URL,
        'development': settings.DEBUG}


def article_schema(page, request):
    data = {'@context': 'https://schema.org', '@type': 'BlogPosting',
        'headline': page.seo_title or page.title, 'description': page.search_description or page.intro,
        'url': settings.PUBLIC_URL + page.get_url(request),
        'author': {'@type': 'Person', 'name': page.author_name},
        'publisher': {'@type': 'Organization', 'name': PublicationSettings.for_request(request).name}}
    if page.first_published_at:
        data['datePublished'] = page.first_published_at.isoformat()
    if page.last_published_at:
        data['dateModified'] = page.last_published_at.isoformat()
    if page.cover:
        data['image'] = settings.PUBLIC_URL + page.cover.get_rendition('width-1600|format-webp').url
    return json.dumps(data).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
