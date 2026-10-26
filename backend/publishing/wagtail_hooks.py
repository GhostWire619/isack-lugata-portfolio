from django.urls import reverse
from django.forms import Media
from wagtail import hooks
from publishing.models import ArticlePage, JournalIndexPage


@hooks.register('insert_global_admin_css')
def journal_admin_styles():
    from django.templatetags.static import static
    from django.utils.html import format_html
    return format_html('<link rel="stylesheet" href="{}">', static('sidenotes/studio.css'))


class JournalWelcomePanel:
    name = 'journal_welcome'
    order = 50
    media = Media()
    def __init__(self, request):
        self.request = request
    def render_html(self, parent_context):
        from django.template.loader import render_to_string
        journal = JournalIndexPage.objects.first()
        return render_to_string('publishing/studio_welcome.html', {
            'journal': journal,
            'published_count': ArticlePage.objects.live().count(),
            'draft_count': ArticlePage.objects.filter(live=False).count(),
            'new_article_url': reverse('wagtailadmin_pages:add', args=['publishing', 'articlepage', journal.pk]) if journal else None,
        }, request=self.request)


@hooks.register('construct_homepage_panels')
def journal_welcome(request, panels):
    panels.append(JournalWelcomePanel(request))
