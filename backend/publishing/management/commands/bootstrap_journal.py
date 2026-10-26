from urllib.parse import urlsplit
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Page, Site
from wagtail.images import get_image_model
from publishing.models import JournalIndexPage, ArticlePage, Category, PublicationSettings


class Command(BaseCommand):
    help = 'Initialize the journal and topic categories. Does not create accounts or publish sample content by default.'
    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true', help='Local development only: create clearly marked example articles.')
    @transaction.atomic
    def handle(self, *args, **options):
        if options['demo'] and not settings.DEBUG:
            raise CommandError('Sample content can only be created with JOURNAL_ENV=development.')
        root = Page.get_first_root_node()
        journal = JournalIndexPage.objects.first()
        if journal is None:
            journal = root.add_child(instance=JournalIndexPage(title='Side notes', slug='journal', live=True))
            journal.save_revision().publish()
        public = urlsplit(settings.PUBLIC_URL)
        site = Site.objects.filter(is_default_site=True).first() or Site()
        site.hostname = public.hostname
        site.port = public.port or (443 if public.scheme == 'https' else 80)
        site.site_name = 'Side notes'
        site.root_page = journal
        site.is_default_site = True
        site.save()
        PublicationSettings.for_site(site)
        categories = {}
        for name, slug in [('Technology', 'technology'), ('Science', 'science'), ('Culture', 'culture'), ('Ideas', 'ideas')]:
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
        if options['demo']:
            samples = [
                ('When AI becomes part of everyday life.', 'when-ai-becomes-part-of-everyday-life', 'technology', 'lab.webp', 'A human hand shaking a robotic hand'),
                ('The tools we build change how we think.', 'the-tools-we-build', 'technology', 'lab.webp', 'A human hand shaking a robotic hand'),
                ('What the ocean can teach us about change.', 'the-ocean-and-change', 'science', 'coast.webp', 'Ocean waves rolling into the shore'),
                ('Why every good question deserves more time.', 'a-good-question', 'ideas', 'landscape.webp', 'A lake reflecting the mountains'),
            ]
            for title, slug, category, filename, alt in samples:
                if ArticlePage.objects.child_of(journal).filter(slug=slug).exists():
                    continue
                path = settings.BASE_DIR / 'static/sidenotes/assets' / filename
                image = get_image_model().objects.filter(title='Demo: ' + filename).first()
                if not image:
                    with path.open('rb') as source:
                        image = get_image_model().objects.create(title='Demo: ' + filename, file=File(source, name=filename))
                page = journal.add_child(instance=ArticlePage(title=title, slug=slug, category=categories[category],
                    intro='A demonstration article for exploring the journal’s publishing system. Replace this with your own writing.',
                    cover=image, cover_alt=alt, cover_caption='Illustrative image from the design prototype.', live=False,
                    body=[('paragraph', '<p>This is demonstration content, published only in the local development journal. It shows how articles, images, and topic categories work together.</p>'),
                        ('heading', 'A closer look'), ('paragraph', '<p>The real editor supports longer articles, source links, quotes, image galleries, and code. Drafts stay private until an authorized editor publishes them.</p>'),
                        ('quote', {'quote': 'A space to look closer and ask better questions.', 'attribution': ''})]))
                page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS('Journal initialized. Create your owner account with: python manage.py createsuperuser'))
