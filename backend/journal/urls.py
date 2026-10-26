from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from publishing import security, views
from publishing.feeds import JournalFeed

urlpatterns = [
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
