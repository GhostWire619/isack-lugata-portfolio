from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from wagtail.admin.auth import require_admin_access
from wagtail.permission_policies.pages import PagePermissionPolicy
from .models import ArticlePage, JournalIndexPage


def can_write(user, journal):
    return bool(journal and journal.permissions_for_user(user).can_add_subpage() and ArticlePage.can_create_at(journal))


@require_admin_access
def articles(request):
    journal = JournalIndexPage.objects.first()
    allowed = PagePermissionPolicy(ArticlePage).instances_user_has_any_permission_for(request.user, {'change'})
    scheduled = Q(latest_revision__approved_go_live_at__isnull=False)
    counts = {'all': allowed.count(), 'published': allowed.filter(live=True).count(),
        'draft': allowed.filter(live=False).exclude(scheduled).count(), 'scheduled': allowed.filter(scheduled).count()}
    status = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()[:200]
    filtered = allowed
    if status == 'draft':
        filtered = filtered.filter(live=False).exclude(scheduled)
    elif status == 'published':
        filtered = filtered.filter(live=True)
    elif status == 'scheduled':
        filtered = filtered.filter(scheduled)
    else:
        status = ''
    if query:
        filtered = filtered.filter(Q(title__icontains=query) | Q(draft_title__icontains=query) | Q(intro__icontains=query))
    pages = Paginator(filtered.select_related('category', 'latest_revision', 'cover').order_by('-latest_revision_created_at', '-pk'), 20).get_page(request.GET.get('page'))
    return render(request, 'publishing/studio_articles.html', {'articles': pages, 'counts': counts,
        'status': status, 'query': query, 'can_write': can_write(request.user, journal)})


@require_admin_access
def write(request):
    journal = JournalIndexPage.objects.first()
    if not can_write(request.user, journal):
        raise PermissionDenied('You do not have permission to create an article.')
    return redirect(reverse('wagtailadmin_pages:add', args=['publishing', 'articlepage', journal.pk]) + '?' + urlencode({'next': reverse('journal_articles')}))
