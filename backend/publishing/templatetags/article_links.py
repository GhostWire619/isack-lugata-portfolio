from django import template
from django.utils.safestring import mark_safe
from publishing.links import link_article_html

register = template.Library()


@register.filter
def article_links(rendered_richtext):
    # This filter must follow |richtext; ordinary text is escaped by the parser.
    return mark_safe(link_article_html(str(rendered_richtext)))
