"""One portable writing skill, delivered through MCP and Studio."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from wagtail.admin.auth import require_admin_access

SKILL_FILE = Path(__file__).parent / 'skills' / 'write-journal-articles' / 'SKILL.md'
SKILL_URI = 'journal://skills/write-journal-articles'
SKILL_VERSION = '2026-10-27.1'


def writing_guide():
    return SKILL_FILE.read_text(encoding='utf-8')


@require_GET
def skill_document(request):
    response = HttpResponse(writing_guide(), content_type='text/markdown; charset=utf-8')
    response['X-Robots-Tag'] = 'noindex, follow'
    response['Content-Disposition'] = 'attachment; filename="SKILL.md"'
    return response


@require_admin_access
@require_GET
def skill_download(request):
    buffer = BytesIO()
    with ZipFile(buffer, 'w', ZIP_DEFLATED) as package:
        package.writestr('write-journal-articles/SKILL.md', writing_guide())
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="write-journal-articles.zip"'
    response['Cache-Control'] = 'no-store'
    return response
