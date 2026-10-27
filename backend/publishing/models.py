import math
import hashlib
import secrets

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils.html import strip_tags
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
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
        from .advertising import eligible
        context['ad_preview'] = bool(getattr(request, 'advertising_preview', False))
        context['show_journal_ads'] = (eligible(request) or context['ad_preview']) and len(page.object_list) >= 3
        return context


def new_article_body():
    return [('paragraph', '')]


class ArticlePage(Page):
    class Meta:
        verbose_name = 'article'
        verbose_name_plural = 'articles'
    intro = models.TextField(max_length=350)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=100, default='Isack Lugata')
    cover = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cover_alt = models.CharField(max_length=250, blank=True)
    cover_caption = models.CharField(max_length=350, blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname='title')),
        ('paragraph', blocks.RichTextBlock(features=['h3', 'bold', 'italic', 'underline', 'link', 'ol', 'ul'])),
        ('image', PictureBlock()),
        ('gallery', blocks.ListBlock(PictureBlock(), min_num=2, max_num=12)),
        ('quote', QuoteBlock()),
        ('code', blocks.TextBlock()),
    ], use_json_field=True, default=new_article_body)
    parent_page_types = ['publishing.JournalIndexPage']
    subpage_types = []
    content_panels = [
        MultiFieldPanel([FieldPanel('title', help_text='The headline readers will see.'), FieldPanel('intro', heading='Short introduction', help_text='One or two sentences that introduce the article.'), FieldPanel('category')], heading='Article details'),
        FieldPanel('body', heading='Write your article', help_text='Start typing in the text block below. Use + to add a heading, image, gallery, quote, or code block.'),
        MultiFieldPanel([FieldPanel('cover'), FieldPanel('cover_alt', heading='Image description', help_text='Describe the cover for readers who cannot see it.'), FieldPanel('cover_caption')], heading='Cover image (optional)', help_text='Choose or upload an image to appear with your article. Add an image description for accessibility.'),
        FieldPanel('author_name'),
    ]
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Article'),
        ObjectList(Page.promote_panels, heading='Search & sharing'),
        ObjectList(Page.settings_panels, heading='Publishing settings'),
    ])
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
        from .advertising import eligible, article_blocks
        context['show_article_ad'] = self.live and eligible(request)
        context['ad_preview'] = bool(getattr(request, 'advertising_preview', False))
        if context['ad_preview']:
            context['show_article_ad'] = True
        context['article_blocks'], context['has_inline_ad'] = article_blocks(self.body)
        return context


@register_setting
class PublicationSettings(BaseSiteSetting):
    name = models.CharField(max_length=80, default='Side notes')
    tagline = models.CharField(max_length=200, default='An independent journal of ideas and perspectives.')
    about = models.TextField(default='Articles and perspectives on technology, science, culture, and the ideas shaping our world. A space to look closer, ask better questions, and explore beyond the familiar.')
    contact_email = models.EmailField(default='lugata619@gmail.com')
    adsense_article_slot = models.CharField(max_length=20, blank=True, default='8873194178', verbose_name='Horizontal ad-unit slot',
        validators=[RegexValidator(r'^[0-9]{1,20}$', 'Enter only the numeric data-ad-slot value from Google.')],
        help_text='Create a responsive Display ad unit in AdSense, then copy its data-ad-slot number. Publisher: pub-4911606730643023.')
    adsense_vertical_slot = models.CharField(max_length=20, blank=True, default='1485658746', verbose_name='Vertical ad-unit slot',
        validators=[RegexValidator(r'^[0-9]{1,20}$', 'Enter only the numeric data-ad-slot value from Google.')])
    adsense_square_slot = models.CharField(max_length=20, blank=True, default='6247030833', verbose_name='Square ad-unit slot',
        validators=[RegexValidator(r'^[0-9]{1,20}$', 'Enter only the numeric data-ad-slot value from Google.')])
    adsense_cmp_ready = models.BooleanField(default=False,
        verbose_name='Google consent message is published',
        help_text='Confirm that the Google-certified consent message is published for isack.space in AdSense → Privacy & messaging. A homemade cookie banner does not replace it.')
    adsense_enabled = models.BooleanField(default=False,
        verbose_name='Enable journal advertisements',
        help_text='Enable after Google approves the site and the consent message is published. Keep Auto ads OFF in AdSense to preserve these placements. No ads run in local development, Studio, staff sessions or draft previews.')
    panels = [FieldPanel('name'), FieldPanel('tagline'), FieldPanel('about'), FieldPanel('contact_email'),
        MultiFieldPanel([FieldPanel('adsense_article_slot'), FieldPanel('adsense_vertical_slot'), FieldPanel('adsense_square_slot'), FieldPanel('adsense_cmp_ready'), FieldPanel('adsense_enabled')], heading='Google AdSense')]

    def clean(self):
        super().clean()
        if self.adsense_enabled and (not all([self.adsense_article_slot, self.adsense_vertical_slot, self.adsense_square_slot]) or not self.adsense_cmp_ready):
            from django.core.exceptions import ValidationError
            raise ValidationError({'adsense_enabled': 'Add the ad-unit slot and confirm the published Google consent message before enabling ads.'})


class MCPConnection(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True, editable=False)
    can_write = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)
    can_analytics = models.BooleanField(default=False)
    oauth_application = models.ForeignKey('oauth2_provider.Application', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'oauth_application'], condition=Q(oauth_application__isnull=False), name='unique_user_oauth_connection')]

    @classmethod
    def issue(cls, *, user, name, expires_at, can_write=False, can_publish=False, can_analytics=False):
        token = 'journal_' + secrets.token_urlsafe(40)
        connection = cls.objects.create(user=user, name=name, expires_at=expires_at,
            can_write=can_write, can_publish=can_publish, can_analytics=can_analytics,
            token_hash=hashlib.sha256(token.encode()).hexdigest())
        return connection, token


class MCPDraftRequest(models.Model):
    connection = models.ForeignKey(MCPConnection, on_delete=models.CASCADE)
    request_key = models.CharField(max_length=100)
    payload_hash = models.CharField(max_length=64)
    article = models.ForeignKey(ArticlePage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['connection', 'request_key'], name='unique_mcp_draft_request')]


class MCPImageUpload(models.Model):
    connection = models.ForeignKey(MCPConnection, on_delete=models.CASCADE)
    content_hash = models.CharField(max_length=64)
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['connection', 'content_hash'], name='unique_mcp_image_upload')]


class MCPAction(models.Model):
    connection = models.ForeignKey(MCPConnection, on_delete=models.CASCADE)
    request_key = models.CharField(max_length=100)
    payload_hash = models.CharField(max_length=64)
    tool = models.CharField(max_length=60)
    article = models.ForeignKey(ArticlePage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['connection', 'request_key'], name='unique_mcp_action_request')]


class PageView(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    path = models.CharField(max_length=250, db_index=True)
    referrer = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    seconds = models.PositiveIntegerField(default=0)
    progress = models.PositiveSmallIntegerField(default=0)
