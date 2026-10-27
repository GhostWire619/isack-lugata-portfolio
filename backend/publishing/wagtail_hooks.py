from django.urls import reverse
from wagtail import hooks
from publishing.models import ArticlePage, JournalIndexPage
from wagtail.admin.menu import MenuItem


@hooks.register('insert_global_admin_css')
def journal_admin_styles():
    from django.templatetags.static import static
    from django.utils.html import format_html
    return format_html('<link rel="stylesheet" href="{}">', static('sidenotes/studio.css'))


class ArticlesMenuItem(MenuItem):
    def is_active(self, request):
        return request.path == '/admin/' or request.path.startswith('/admin/articles/')


@hooks.register('register_admin_menu_item')
def articles_menu():
    return ArticlesMenuItem('Articles', reverse('journal_articles'), icon_name='doc-full', order=50)


@hooks.register('register_admin_menu_item')
def ai_menu():
    return MenuItem('AI connections', reverse('journal_ai'), icon_name='link', order=60)


class AnalyticsMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm('publishing.view_pageview')


@hooks.register('register_admin_menu_item')
def analytics_menu():
    return AnalyticsMenuItem('Analytics', reverse('journal_analytics'), icon_name='chart-line', order=70)


@hooks.register('construct_page_action_menu')
def clear_article_actions(menu_items, request, context):
    if isinstance(context.get('page'), ArticlePage) or (context.get('view') == 'create' and isinstance(context.get('parent_page'), JournalIndexPage)):
        request.journal_article_editor = True
        request.journal_more_actions = any(item.name not in ['action-save-draft', 'action-publish'] for item in menu_items)
        request.journal_can_schedule = any(item.name == 'action-publish' for item in menu_items)
