import math

from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.html import strip_tags
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    panels = [FieldPanel('name'), FieldPanel('slug')]
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name


class PictureBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt = blocks.CharBlock(help_text='Describe the image for readers who cannot see it.')
    caption = blocks.CharBlock(required=False)
    class Meta:
        template = 'publishing/blocks/picture.html'
        icon = 'image'


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)
    class Meta:
        template = 'publishing/blocks/quote.html'
        icon = 'openquote'


class JournalIndexPage(Page):
    intro = models.CharField(max_length=250, default='Articles and perspectives on technology, science, culture, and ideas.')
    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['publishing.ArticlePage']
    max_count = 1
    content_panels = Page.content_panels + [FieldPanel('intro')]
    def articles(self):
        return ArticlePage.objects.child_of(self).live().public().select_related('category', 'cover').order_by('-first_published_at', '-id')
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        query = request.GET.get('q', '').strip()[:200]
        category = request.GET.get('category', '')[:100]
        articles = self.articles()
        if category:
            articles = articles.filter(category__slug=category)
        if query:
            articles = articles.filter(Q(title__icontains=query) | Q(intro__icontains=query) | Q(search_description__icontains=query))
        featured = articles.first() if not query and not category else None
        if featured:
            articles = articles.exclude(pk=featured.pk)
        paginator = Paginator(articles, 9)
        page = paginator.get_page(request.GET.get('page'))
        context.update({'featured': featured if page.number == 1 else None,
            'articles': page, 'categories': Category.objects.all(), 'query': query,
            'active_category': category, 'filtered': bool(query or category),
            'description': self.search_description or self.intro})
        return context


class ArticlePage(Page):
    intro = models.TextField(max_length=350)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=100, default='Isack Lugata')
    cover = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover_alt = models.CharField(max_length=250, blank=True)
    cover_caption = models.CharField(max_length=350, blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname='title')),
        ('paragraph', blocks.RichTextBlock(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ('image', PictureBlock()),
        ('gallery', blocks.ListBlock(PictureBlock(), min_num=2, max_num=12)),
        ('quote', QuoteBlock()),
        ('code', blocks.TextBlock()),
    ], use_json_field=True)
    parent_page_types = ['publishing.JournalIndexPage']
    subpage_types = []
    content_panels = Page.content_panels + [FieldPanel('intro'), FieldPanel('category'), FieldPanel('author_name'),
        FieldPanel('cover'), FieldPanel('cover_alt'), FieldPanel('cover_caption'), FieldPanel('body')]
    search_fields = Page.search_fields + [index.SearchField('intro'), index.SearchField('body')]
    def clean(self):
        super().clean()
        if self.cover_id and not self.cover_alt.strip():
            from django.core.exceptions import ValidationError
            raise ValidationError({'cover_alt': 'Add an accessible description for the cover image before publishing.'})
    @property
    def reading_minutes(self):
        text = self.intro + ' ' + ' '.join(str(block.value) for block in self.body if block.block_type in ['heading', 'paragraph', 'quote'])
        return max(1, math.ceil(len(strip_tags(text).split()) / 220))
    @property
    def headings(self):
        return [{'id': f'section-{i}', 'title': str(block.value)} for i, block in enumerate(self.body) if block.block_type == 'heading']
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['description'] = self.search_description or self.intro
        from .context import article_schema
        context['article_schema'] = article_schema(self, request)
        context['related'] = ArticlePage.objects.sibling_of(self).live().public().exclude(pk=self.pk).select_related('cover', 'category').order_by('-first_published_at')[:3]
        return context


@register_setting
class PublicationSettings(BaseSiteSetting):
    name = models.CharField(max_length=80, default='Side notes')
    tagline = models.CharField(max_length=200, default='An independent journal of ideas and perspectives.')
    about = models.TextField(default='Articles and perspectives on technology, science, culture, and the ideas shaping our world. A space to look closer, ask better questions, and explore beyond the familiar.')
    contact_email = models.EmailField(default='lugata619@gmail.com')
    panels = [FieldPanel('name'), FieldPanel('tagline'), FieldPanel('about'), FieldPanel('contact_email')]
