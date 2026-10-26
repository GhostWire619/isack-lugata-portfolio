"""Render focused editorial case studies instead of repeated captured galleries."""
from pathlib import Path
import html
import json
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
data = json.loads((ROOT / 'content/portfolio.json').read_text(encoding='utf8'))
esc = html.escape
fonts = '\n'.join(re.findall(r'@font-face\s*\{[^}]*\}', (DIST / 'index.html').read_text(encoding='utf8')))
(DIST / 'assets/personal/case-fonts.css').write_text(fonts, encoding='utf8')
(DIST / 'assets/personal/case-studies.css').write_text((ROOT / 'scripts/case-studies.css').read_text(encoding='utf8'), encoding='utf8')
(DIST / 'assets/personal/case-interactions.js').write_text((ROOT / 'scripts/case-interactions.js').read_text(encoding='utf8'), encoding='utf8')
introductions = {
    'ecofy': 'Farm planning and agricultural guidance, brought together for Tanzanian farmers.',
    'wakili-msomi': 'Connecting legal information, document workflows, and AI assistance for the Tanzanian context.',
    'globoexpats': 'A marketplace experience for people making a life in Tanzania.',
    'habitek': 'Connecting the search for a property with the work of managing it.',
    'osher-market': 'The application services behind a commerce experience.',
    'falco': 'Backend development for the everyday work inside a financial-services business.',
    'tanstack-tanzania': 'Connecting tech students with resources, opportunities, and their next step.',
}
chapters = {
    'ecofy': [('The challenge', [0]), ('My contribution', [1, 2]), ('Building as a founder', [3, 4])],
    'wakili-msomi': [('The context', [0]), ('Frontend & backend', [1]), ('Product & collaboration', [2, 3])],
    'globoexpats': [('A community marketplace', [0]), ('My contribution', [1]), ('Frontend decisions', [2, 3, 4])],
    'habitek': [('The product', [0]), ('My contribution', [1]), ('Connecting the experience', [2])],
    'osher-market': [('The commerce context', [0]), ('My contribution', [1]), ('The backend approach', [2, 3])],
    'falco': [('Behind the scenes', [0]), ('My contribution', [1]), ('Internal workflows', [2, 3])],
    'tanstack-tanzania': [('A student community', [0]), ('My contribution', [1]), ('Lab collaboration', [2, 3])],
}
whatsapp = 'https://wa.me/' + re.sub(r'\D', '', data['whatsapp']) + '?text=' + quote(data['inquiry'])
socials = [
    ('GitHub', 'https://github.com/GhostWire619', '/assets/identity/icon-github-dark.svg'),
    ('Email', 'mailto:' + data['email'], '/assets/identity/icon-envelope-dark.svg'),
    ('LinkedIn', 'https://www.linkedin.com/in/isack-lugata-a6356531a/', '/assets/framerusercontent.com/images/ZFKhUtXfXZja4pTGZNB2LLZqrQ-183dfb5b2277.svg'),
    ('Instagram — @zac_eye', data['instagram'], '/assets/identity/icon-instagram-dark.svg'),
    ('WhatsApp — ' + data['whatsapp'], whatsapp, '/assets/identity/icon-whatsapp-dark.svg'),
]
social_html = ''.join(f'<a class="social-button" href="{esc(url,quote=True)}" aria-label="{esc(label,quote=True)}" target="_blank" rel="noopener noreferrer"><img src="{icon}" alt="" width="48" height="48"></a>' for label, url, icon in socials)

for i, project in enumerate(data['projects']):
    slug = project['slug']
    image = project.get('cover') or project['artwork']
    caption = 'Public product preview. My contribution: ' + project['role'] + '.'
    if slug == 'falco':
        caption = 'Company branding for context. My work was on the internal management backend.'
    sections = ''.join('<section class="case-chapter" data-case-reveal><div class="chapter-label"><span>' + str(n + 1).zfill(2) + '</span><h2>' + esc(title) + '</h2></div><div class="chapter-copy">' + ''.join('<p>' + esc(project['story'][index]) + '</p>' for index in indices) + '</div></section>' for n, (title, indices) in enumerate(chapters[slug]))
    others = data['projects'][i+1:] + data['projects'][:i]
    related = ''.join(f'<a class="more-work-card" href="/{p["slug"]}"><div class="more-work-cover"><img src="{p["artwork"]}" alt="{esc(p["name"])} project artwork" loading="lazy" decoding="async"></div><div class="more-work-copy"><h3>{esc(p["name"])}</h3><span aria-hidden="true">↗</span><p>{esc(p["role"])}</p></div></a>' for p in others)
    focus = ''.join('<li>' + esc(item) + '</li>' for item in project['stack'])
    site_label = 'Company website' if slug == 'falco' else 'Visit the product'
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(project['name'])} — {esc(data['name'])}</title><link rel="icon" href="/assets/personal/mark-il.svg"><link rel="stylesheet" href="/assets/personal/case-fonts.css"><link rel="stylesheet" href="/assets/personal/case-studies.css"><link rel="stylesheet" href="/assets/personal/contact.css"><link rel="stylesheet" href="/assets/personal/navigation.css"><script defer src="/assets/personal/navigation.js"></script><script defer src="/assets/personal/contact.js"></script><script defer src="/assets/personal/case-interactions.js"></script></head><body>
<a class="skip-link" href="#case-study">Skip to project</a>
<header class="case-header"><a class="wordmark" href="/">{esc(data['name'])}</a><nav aria-label="Main navigation"><a href="/">Works</a><a href="/about">Story</a></nav><a class="chrome-button header-contact" href="mailto:{esc(data['email'])}">Let’s chat</a></header>
<main id="case-study" class="case-shell"><article>
<section class="case-intro"><a class="back-link" href="/">← All projects</a><div class="case-title"><img src="{esc(project['icon'])}" width="54" height="54" alt=""><span>Selected work / {esc(project['tags'][0])}</span></div><h1>{esc(project['name'])}</h1><p class="case-summary">{esc(introductions[slug])}</p><a class="chrome-button" href="{esc(project['url'],quote=True)}" target="_blank" rel="noopener noreferrer">{site_label} ↗</a></section>
<dl class="case-facts"><div><dt>My role</dt><dd>{esc(project['role'])}</dd></div><div><dt>Project</dt><dd>{esc(project['tags'][1])}</dd></div><div><dt>Website</dt><dd><a href="{esc(project['url'],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(urlsplit(project['url']).netloc)} ↗</a></dd></div></dl>
<figure class="case-media"><img src="{esc(image)}" alt="{esc(project['name'])} — {'company branding' if slug == 'falco' else 'public product interface'}" fetchpriority="high"><figcaption>{esc(caption)}</figcaption></figure>
<div class="case-narrative"><aside class="case-scope"><span class="eyebrow">Focus of my work</span><ul>{focus}</ul></aside><div class="case-chapters">{sections}</div></div>
<section class="case-next" data-case-reveal><div class="more-work-heading"><div><span class="eyebrow">Keep exploring</span><h2>Other projects</h2></div><div class="rail-controls"><button data-rail-previous aria-label="Previous projects">←</button><button data-rail-next aria-label="Next projects">→</button></div></div><div class="more-work-rail" aria-label="Other projects" tabindex="0">{related}</div></section>
</article></main>
<footer class="case-footer"><div><span class="eyebrow">Have a project in mind?</span><h2>Ready for the<br>next adventure.</h2><a class="chrome-button" href="mailto:{esc(data['email'])}">Let’s talk ↗</a></div><div class="footer-contact"><p>Frontend, mobile, backend & applied AI.</p><p>Dar es Salaam, Tanzania.</p><a href="mailto:{esc(data['email'])}">{esc(data['email'])}</a><div class="case-socials">{social_html}</div></div></footer>
</body></html>'''
    (DIST / (slug + '.html')).write_text(page, encoding='utf8')
print('Built', len(data['projects']), 'editorial case studies with one contextual image each and complete contribution narratives.')
