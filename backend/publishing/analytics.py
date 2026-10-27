"""First-party, per-page aggregate metrics. No visitor identifiers or IP storage."""
import hashlib
import json
from datetime import timedelta
from urllib.parse import urlsplit
from uuid import UUID
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, F
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import ArticlePage, PageView


def report(days=30, path=None):
    views = PageView.objects.filter(created_at__gte=timezone.now() - timedelta(days=days))
    if path:
        views = views.filter(path=path)
    summary = views.aggregate(views=Count('pk'), average_seconds=Avg('seconds'))
    summary['average_seconds'] = round(summary['average_seconds'] or 0)
    summary['read_to_end'] = views.filter(path__startswith='/blog/', progress__gte=75).count()
    daily = list(views.extra(select={'day': 'date(created_at)'}).values('day').annotate(views=Count('pk')).order_by('day'))
    for row in daily:
        row['day'] = str(row['day'])
    return dict(summary, days=days, pages=list(views.values('path').annotate(views=Count('pk'),
        average_seconds=Avg('seconds')).order_by('-views')[:30]),
        sources=list(views.exclude(referrer='').values('referrer').annotate(views=Count('pk')).order_by('-views')[:10]),
        daily=daily)


def public_path(path):
    if not isinstance(path, str) or len(path) > 250 or '?' in path or '#' in path:
        return False
    if path in {'/', '/index.html', '/about', '/about/', '/blog/', '/blog/privacy/', '/blog/terms/'}:
        return True
    if path.startswith('/blog/'):
        slug = path.removeprefix('/blog/').strip('/')
        return '/' not in slug and ArticlePage.objects.live().public().filter(slug=slug).exists()
    portfolio_pages = {'ecofy', 'falco', 'globoexpats', 'habitek', 'osher-market', 'robotics',
        'tanstack-tanzania', 'wakili-msomi', 'about', 'infrastructure', 'rag-platform', 'marketplace'}
    if path.strip('/').removesuffix('.html') in portfolio_pages:
        return True
    # Portfolio project paths are generated locally, never arbitrary URLs.
    from pathlib import Path
    root = settings.BASE_DIR.parent / 'dist'
    relative = path.lstrip('/').rstrip('/')
    if not relative or '/' in relative or relative.startswith('.'):
        return False
    candidate = (root / (relative if relative.endswith('.html') else relative + '.html')).resolve()
    return candidate.is_relative_to(root.resolve()) and candidate.is_file()


@csrf_exempt
def collect(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    if request.headers.get('Origin') != settings.PUBLIC_URL or request.user.is_authenticated:
        return HttpResponse(status=403)
    if int(request.META.get('CONTENT_LENGTH') or 0) > 2048:
        return HttpResponse(status=413)
    if request.content_type != 'application/json':
        return HttpResponse(status=415)
    try:
        data = json.loads(request.body)
        event_id = UUID(data['id'])
        path = data['path']
        seconds, progress = data.get('seconds', 0), data.get('progress', 0)
        if type(seconds) is not int or type(progress) is not int or not 0 <= seconds <= 3600 or not 0 <= progress <= 100 or not public_path(path):
            raise ValueError()
        referrer = urlsplit(data.get('referrer', '')).hostname or ''
        if len(referrer) > 200:
            raise ValueError()
    except (ValueError, KeyError, TypeError, AttributeError):
        return HttpResponse(status=400)
    key = 'metrics:' + hashlib.sha256(request.META.get('REMOTE_ADDR', '').encode()).hexdigest()
    cache.add(key, 0, 60)
    try:
        if cache.incr(key) > 120:
            return HttpResponse(status=429)
    except ValueError:
        return HttpResponse(status=429)
    event, created = PageView.objects.get_or_create(pk=event_id, defaults={'path': path, 'referrer': referrer,
        'seconds': seconds, 'progress': progress})
    if not created:
        if event.path != path:
            return HttpResponse(status=400)
        PageView.objects.filter(pk=event.pk, seconds__lt=seconds).update(seconds=seconds)
        PageView.objects.filter(pk=event.pk, progress__lt=progress).update(progress=progress)
    response = HttpResponse(status=204)
    response['Cache-Control'] = 'no-store'
    return response
