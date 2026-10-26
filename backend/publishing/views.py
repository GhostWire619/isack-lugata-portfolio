from xml.etree import ElementTree as ET
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from wagtail.models import Site
from .models import ArticlePage, JournalIndexPage


def portfolio_preview(request, path=''):
    """Local-only integration: serve the existing portfolio beside the journal."""
    from django.http import FileResponse, Http404
    import mimetypes
    if not settings.DEBUG:
        raise Http404
    root = (settings.BASE_DIR.parent / 'dist').resolve()
    file = (root / (path or 'index.html')).resolve()
    if not file.is_relative_to(root):
        raise Http404
    if not file.suffix:
        file = file.with_suffix('.html')
    if not file.is_file():
        raise Http404
    content_type = 'text/javascript' if file.suffix == '.mjs' else mimetypes.guess_type(file.name)[0]
    return FileResponse(file.open('rb'), content_type=content_type or 'application/octet-stream')


@require_GET
def health(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return HttpResponse('ok', content_type='text/plain')


@require_GET
def sitemap(request):
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    root = ET.Element(f'{{{namespace}}}urlset')
    seen = set()
    def add(location, modified=None):
        if location in seen:
            return
        seen.add(location)
        node = ET.SubElement(root, f'{{{namespace}}}url')
        ET.SubElement(node, f'{{{namespace}}}loc').text = location
        if modified:
            ET.SubElement(node, f'{{{namespace}}}lastmod').text = modified.isoformat()
    if settings.PORTFOLIO_SITEMAP.exists():
        source = ET.parse(settings.PORTFOLIO_SITEMAP)
        for loc in source.findall(f'.//{{{namespace}}}loc'):
            # Site-controlled static sitemap, preserving paths when testing another hostname.
            from urllib.parse import urlsplit
            add(settings.PUBLIC_URL + urlsplit(loc.text).path)
    site = Site.find_for_request(request)
    if site:
        for page in JournalIndexPage.objects.live().public().descendant_of(site.root_page, inclusive=True):
            add(settings.PUBLIC_URL + page.get_url(request), page.last_published_at)
        for page in ArticlePage.objects.live().public().descendant_of(site.root_page):
            add(settings.PUBLIC_URL + page.get_url(request), page.last_published_at)
    return HttpResponse(ET.tostring(root, encoding='utf-8', xml_declaration=True), content_type='application/xml')
