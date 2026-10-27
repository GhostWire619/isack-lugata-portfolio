from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from publishing import security, studio, views, mcp, analytics, writing
from publishing.feeds import JournalFeed

urlpatterns = [
    path('', include('publishing.oauth_urls')),
    path('ads.txt', views.ads_txt, name='journal_ads_txt'),
    path('blog/privacy/', views.privacy, name='journal_privacy'),
    path('blog/terms/', views.terms, name='journal_terms'),
    path('blog/ai-writing-skill.md', writing.skill_document, name='journal_writing_skill'),
    path('mcp/', mcp.endpoint, name='journal_mcp'),
    path('mcp', mcp.endpoint),
    path('events/', analytics.collect, name='journal_metrics'),
    path('admin/ai/', studio.ai_connections, name='journal_ai'),
    path('admin/ai/writing-skill/', writing.skill_download, name='journal_skill_download'),
    path('admin/analytics/', studio.analytics, name='journal_analytics'),
    path('admin/', studio.articles, name='journal_studio'),
    path('admin/articles/', studio.articles, name='journal_articles'),
    path('admin/articles/new/', studio.write, name='journal_write'),
    path('admin/advertising/preview/', studio.advertising_preview, name='journal_ad_preview'),
    path('admin/', include(wagtailadmin_urls)),
    path('security/verify/', security.verify, name='journal_verify'),
    path('documents/', include(wagtaildocs_urls)),
    path('blog/feed/', JournalFeed(), name='journal_feed'),
    path('sitemap.xml', views.sitemap, name='journal_sitemap'),
    path('healthz', views.health),
    path('blog/', include(wagtail_urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('', views.portfolio_preview), path('<path:path>', views.portfolio_preview)]
