"""Publisher-controlled placements; no external requests on preview/dev pages."""
from django.conf import settings
from django.utils.html import strip_tags
from .models import PublicationSettings


def eligible(request):
    config = PublicationSettings.for_request(request)
    return bool(not settings.DEBUG and not getattr(request, 'is_preview', False)
        and not request.user.is_staff and config.adsense_enabled and config.adsense_cmp_ready
        and config.adsense_article_slot and config.adsense_vertical_slot and config.adsense_square_slot)


def article_blocks(body):
    result = [{'block': block, 'ad_after': False} for block in body]
    sizes = [len(strip_tags(str(block.value)).split()) if block.block_type in {'paragraph', 'heading'} else 0 for block in body]
    total = sum(sizes)
    # A short story stays uninterrupted; longer pieces get natural text breaks.
    targets = [total / 2] if total >= 450 else []
    if total >= 1600:
        targets = [total / 3, total * 2 / 3]
    cumulative, candidates = 0, []
    for index, (block, words) in enumerate(zip(body, sizes)):
        cumulative += words
        if block.block_type == 'paragraph' and cumulative >= 180 and total - cumulative >= 150:
            candidates.append((index, cumulative))
    for target in targets:
        available = [(i, n) for i, n in candidates if not result[i]['ad_after']]
        if available:
            index, _ = min(available, key=lambda candidate: abs(candidate[1] - target))
            result[index]['ad_after'] = True
    return result, any(item['ad_after'] for item in result)
