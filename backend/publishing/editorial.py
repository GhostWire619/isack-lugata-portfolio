"""Structural editorial checks. No remote requests or invented SEO score."""
from bs4 import BeautifulSoup
from .links import link_article_html


def review(article):
    draft = article.get_latest_revision_as_object()
    headings, paragraphs, links, images = [], [], [], []
    if draft.cover_id:
        images.append({'id': draft.cover_id, 'alt': draft.cover_alt, 'placement': 'cover'})
    for block in draft.body:
        if block.block_type == 'heading':
            headings.append(str(block.value))
        elif block.block_type == 'paragraph':
            soup = BeautifulSoup(link_article_html(str(block.value)), 'html.parser')
            paragraphs.extend(len(p.get_text(' ', strip=True).split()) for p in soup.select('p,li'))
            links.extend({'label': link.get_text(' ', strip=True), 'url': link.get('href', '')} for link in soup.select('a'))
        elif block.block_type == 'image':
            images.append({'id': block.value['image'].pk, 'alt': block.value['alt'], 'placement': 'body'})
        elif block.block_type == 'gallery':
            images.extend({'id': item['image'].pk, 'alt': item['alt'], 'placement': 'gallery'} for item in block.value)
    warnings = []
    if not images:
        warnings.append('Add at least one relevant image before presenting this as a finished illustrated article.')
    if any(not image['alt'].strip() for image in images):
        warnings.append('Add accurate alt text to every image.')
    if any(count > 100 for count in paragraphs):
        warnings.append('Some paragraphs exceed 100 words; consider splitting them for mobile reading.')
    if not links:
        warnings.append('No clickable references found. Add verified sources where factual claims require them.')
    if not draft.seo_title:
        warnings.append('The SEO title uses the article headline; set seo_title only if a distinct search title improves clarity.')
    return {'article_id': article.pk, 'revision_id': article.latest_revision_id,
        'seo_title': draft.seo_title or draft.title, 'meta_description': draft.search_description or draft.intro,
        'headings': headings, 'word_count': sum(paragraphs) + len(draft.intro.split()),
        'long_paragraphs': sum(count > 100 for count in paragraphs), 'links': links, 'images': images,
        'warnings': warnings, 'limits': 'Structural checks only. Source accuracy, image relevance, URL availability, search ranking and AI citations are not verified.'}
