"""The project deck's markup. One source for the built page and for returning to Home by the router."""
from html import escape

ORDER = ('globoexpats', 'falco', 'wakili-msomi', 'tanstack-tanzania', 'ecofy', 'habitek', 'osher-market')
ARROW = '<svg viewBox="0 0 20 20" width="18" height="18"><path d="M6 14L14 6M7.5 6H14v6.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def card(project, index):
    slug, name, role = (escape(project[key], quote=True) for key in ('slug', 'name', 'role'))
    small, large = (f'/assets/personal/showcase/{slug}-{width}.webp' for width in (720, 1280))
    # Only the first card is in view at load; it must not wait behind the rest.
    loading = 'fetchpriority="high"' if index == 0 else 'loading="lazy" decoding="async"'
    tags = ''.join(f'<li>{escape(tag)}</li>' for tag in project.get('tags', [])[:3])
    return (
        f'<a class="showcase-card" href="/{slug}" aria-label="{name}: {role}" '
        f'style="--tint:{escape(project.get("color") or "#eee", quote=True)};--stick:{68 + index * 9}px;--stick-wide:{70 + index * 8}px">'
        f'<div class="showcase-media"><img src="{small}" srcset="{small} 720w, {large} 1280w" '
        f'sizes="(max-width:760px) calc(100vw - 38px), 92vw" alt="" {loading}></div>'
        f'<div class="showcase-caption"><div class="showcase-caption-top"><span class="showcase-index">{index + 1:02d}</span><h3>{name}</h3></div>'
        f'<p class="showcase-role">{role}</p><ul class="showcase-tags">{tags}</ul>'
        f'<span class="showcase-arrow" aria-hidden="true">{ARROW}</span></div></a>'
    )


def render_showcase(projects):
    by_slug = {project['slug']: project for project in projects}
    cards = ''.join(card(by_slug[slug], index) for index, slug in enumerate(slug for slug in ORDER if slug in by_slug))
    return f'<section class="showcase" aria-label="Selected projects">{cards}<p class="showcase-more">More projects coming soon</p></section>'
