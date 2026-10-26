from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from wagtail.models import Site
from .models import JournalIndexPage, PublicationSettings


class JournalFeed(Feed):
    def get_object(self, request):
        self.request = request
        site = Site.find_for_request(request)
        return get_object_or_404(JournalIndexPage.objects.live().public(), pk=site.root_page_id)
    def title(self, obj):
        return PublicationSettings.for_request(self.request).name
    def link(self, obj):
        return settings.PUBLIC_URL + obj.get_url(self.request)
    def description(self, obj):
        return obj.intro
    def items(self, obj):
        return obj.articles()[:30]
    def item_title(self, item):
        return item.title
    def item_description(self, item):
        return item.intro
    def item_link(self, item):
        return settings.PUBLIC_URL + item.get_url(self.request)
    def item_pubdate(self, item):
        return item.first_published_at
    def item_updateddate(self, item):
        return item.last_published_at
    def item_author_name(self, item):
        return item.author_name
