from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from wagtail.admin.auth import require_admin_access
from wagtail.permission_policies.pages import PagePermissionPolicy
from .models import ArticlePage, JournalIndexPage, MCPConnection


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
    from wagtail.models import Site
    site = Site.find_for_request(request)
    settings_url = reverse('wagtailsettings:edit', args=['publishing', 'publicationsettings', site.pk]) if site and request.user.has_perm('publishing.change_publicationsettings') else None
    return render(request, 'publishing/studio_articles.html', {'articles': pages, 'counts': counts,
        'status': status, 'query': query, 'can_write': can_write(request.user, journal), 'advertising_settings_url': settings_url})


@require_admin_access
def write(request):
    journal = JournalIndexPage.objects.first()
    if not can_write(request.user, journal):
        raise PermissionDenied('You do not have permission to create an article.')
    return redirect(reverse('wagtailadmin_pages:add', args=['publishing', 'articlepage', journal.pk]) + '?' + urlencode({'next': reverse('journal_articles')}))


@require_admin_access
def advertising_preview(request):
    from django.http import Http404
    request.advertising_preview = True
    request.is_preview = True
    if request.GET.get('layout') == 'journal':
        page = JournalIndexPage.objects.first()
    else:
        page = PagePermissionPolicy(ArticlePage).instances_user_has_any_permission_for(request.user, {'change'}).order_by('-latest_revision_created_at').first()
        if page:
            page = page.get_latest_revision_as_object()
    if not page:
        raise Http404('Create an article before previewing ad placements.')
    return page.serve_preview(request, page.default_preview_mode)


@require_admin_access
def ai_connections(request):
    from django import forms
    from django.conf import settings
    from django.http import HttpResponseBadRequest
    from django.utils import timezone
    from datetime import timedelta
    class TokenForm(forms.Form):
        name = forms.CharField(max_length=100, label='Connection name', initial='My AI assistant')
        days = forms.IntegerField(min_value=1, max_value=30, initial=7, label='Expires after (days)')
        can_write = forms.BooleanField(required=False, initial=True, label='Create and edit drafts, upload images')
        can_analytics = forms.BooleanField(required=False, initial=True, label='Read aggregate analytics')
        can_publish = forms.BooleanField(required=False, label='Allow direct publishing and scheduling')
    token = None
    form = TokenForm(request.POST if request.method == 'POST' and request.POST.get('action') == 'create' else None)
    if request.method == 'POST':
        if request.POST.get('action') == 'setup_claude':
            from .oauth import claude_application
            claude_application(request.user, create=True)
            return redirect('journal_ai')
        if request.POST.get('action') == 'revoke':
            connection = MCPConnection.objects.filter(pk=request.POST.get('connection'), user=request.user).first()
            if not connection:
                return HttpResponseBadRequest('Connection not found.')
            connection.revoked_at = timezone.now()
            connection.save(update_fields=['revoked_at'])
            if connection.oauth_application_id:
                from oauth2_provider.models import AccessToken, RefreshToken, Grant
                RefreshToken.objects.filter(user=request.user, application=connection.oauth_application).delete()
                AccessToken.objects.filter(user=request.user, application=connection.oauth_application).delete()
                Grant.objects.filter(user=request.user, application=connection.oauth_application).delete()
            return redirect('journal_ai')
        if request.POST.get('action') == 'create' and form.is_valid():
            values = form.cleaned_data
            _, token = MCPConnection.issue(user=request.user, name=values['name'],
                expires_at=timezone.now() + timedelta(days=values['days']), can_write=values['can_write'],
                can_analytics=values['can_analytics'], can_publish=values['can_publish'])
    connections = MCPConnection.objects.filter(user=request.user, revoked_at__isnull=True,
        expires_at__gt=timezone.now()).select_related('oauth_application').order_by('-created_at')
    from .models import OAuthFailure
    from .oauth import claude_application
    failures = OAuthFailure.objects.filter(user=request.user).order_by('-created_at')[:10]
    response = render(request, 'publishing/studio_ai.html', {'connections': connections, 'oauth_failures': failures, 'form': form,
        'token': token, 'mcp_url': settings.PUBLIC_URL + '/mcp', 'claude_client': claude_application(request.user)})
    response['Cache-Control'] = 'no-store'
    # Native form POSTs need their same-origin provenance for Django CSRF.
    # no-referrer can produce Origin: null even with a valid form token.
    response['Referrer-Policy'] = 'same-origin'
    return response


@require_admin_access
def analytics(request):
    from .analytics import report
    if not request.user.has_perm('publishing.view_pageview'):
        raise PermissionDenied()
    days = int(request.GET.get('days', '30')) if request.GET.get('days', '30') in {'7', '30', '90'} else 30
    return render(request, 'publishing/studio_analytics.html', {'metrics': report(days), 'days': days})
