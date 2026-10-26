"""Publish metadata for the real domain in HTML and hydrated Framer metadata."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
data = json.loads((ROOT / 'content/portfolio.json').read_text(encoding='utf8'))
origin = data['siteUrl'].rstrip('/')
assert origin.startswith('https://') and origin.count('/') == 2
name = data['name']
person_id = origin + '/#person'
website_id = origin + '/#website'
portrait = origin + '/assets/personal/portrait.png'
same_as = ['https://github.com/GhostWire619', 'https://www.linkedin.com/in/isack-lugata-a6356531a/', data['instagram']]
person = {
    '@type': 'Person', '@id': person_id, 'name': name,
    'alternateName': data['fullName'], 'url': origin + '/',
    'image': portrait, 'jobTitle': 'Software Developer',
    'description': 'Freelance software developer in Dar es Salaam, Tanzania, working across frontend, mobile apps, backend systems, and applied AI. Co-founder of Ecofy Africa.',
    'email': data['email'], 'telephone': data['whatsapp'],
    'homeLocation': {'@type': 'Place', 'name': data['location'], 'address': {'@type': 'PostalAddress', 'addressLocality': 'Dar es Salaam', 'addressCountry': 'TZ'}},
    'sameAs': same_as,
    'knowsAbout': ['Frontend development', 'Web application development', 'Mobile application development', 'Backend development', 'API integration', 'Applied artificial intelligence', 'Swahili language technology'],
    'worksFor': {'@type': 'Organization', 'name': 'Ecofy Africa', 'url': 'https://ecofy.co.tz/'},
}
website = {'@type': 'WebSite', '@id': website_id, 'name': name, 'url': origin + '/', 'inLanguage': 'en', 'publisher': {'@id': person_id}}
pages = {
    'index': {'path': '/', 'title': 'Isack Lugata | Software & AI Developer in Tanzania', 'description': 'Isack Lugata is a freelance software developer in Dar es Salaam, Tanzania, building websites, mobile apps, backend systems and applied AI solutions.'},
    'about': {'path': '/about', 'title': 'About Isack Lugata | Developer in Dar es Salaam, Tanzania', 'description': 'Meet Isack Madaha Lugata: software developer in Tanzania, Ecofy Africa co-founder and former UDSM robotics lab chairperson. Explore his background and work.'},
    'robotics': {'path': '/robotics', 'title': 'UDSM Robotics & Nena AI | Isack Lugata', 'description': 'Isack Lugata’s backend contributions and former leadership at the UDSM 3D Solutions & Robotics Lab, including the Nena AI Swahili speech team project.'},
}
descriptions = {
    'ecofy': 'Explore Isack Lugata’s frontend, backend and applied AI work at Ecofy Africa, an agricultural platform for Tanzanian farmers. Co-founder, CEO and AI Lead.',
    'wakili-msomi': 'Explore Isack Lugata’s frontend and backend development for Wakili Msomi, an AI-powered legal-information application for Tanzania.',
    'globoexpats': 'Explore Isack Lugata’s mainly frontend development work for GloboExpats, a marketplace serving the expat community in Tanzania.',
    'habitek': 'Explore Isack Lugata’s frontend and backend work on Habitek, a property discovery and hospitality management platform in Tanzania.',
    'osher-market': 'Explore Isack Lugata’s backend development for Osher Market, including the application services behind its commerce platform.',
    'falco': 'Explore Isack Lugata’s internal management backend work for Falco Finance, focused on application services and everyday business operations.',
    'tanstack-tanzania': 'Explore Isack Lugata’s backend contributions to TanStack Tanzania, a lab team project connecting tech students with resources and opportunities.',
}
for project in data['projects']:
    slug = project['slug']
    pages[slug] = {'path': '/' + slug, 'title': project['name'] + ' | ' + name + ' — Development Case Study', 'description': descriptions[slug], 'project': project}


def set_meta(soup, key, value, property=False):
    attr = 'property' if property else 'name'
    matches = soup.find_all('meta', attrs={attr: key})
    tag = matches[0] if matches else soup.new_tag('meta', attrs={attr: key})
    for duplicate in matches[1:]:
        duplicate.decompose()
    tag['content'] = value
    if not matches:
        soup.head.append(tag)


old_titles = {}
for file, page in pages.items():
    path = DIST / (file + '.html')
    soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
    old_titles[soup.title.get_text()] = page
    soup.html['lang'] = 'en'
    soup.title.string = page['title']
    url = origin + page['path']
    image_path = page.get('project', {}).get('cover') or '/assets/personal/portrait.png'
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        image_path = '/assets/personal/portrait.png'
    page['image'] = origin + image_path
    set_meta(soup, 'description', page['description'])
    set_meta(soup, 'robots', 'index, follow, max-image-preview:large')
    for key, value in {'og:type': 'website', 'og:locale': 'en_TZ', 'og:site_name': name, 'og:title': page['title'], 'og:description': page['description'], 'og:url': url, 'og:image': page['image'], 'og:image:alt': page.get('project', {}).get('name', name + ' — software developer in Tanzania')}.items():
        set_meta(soup, key, value, property=True)
    for key, value in {'twitter:card': 'summary_large_image' if page.get('project') and image_path != '/assets/personal/portrait.png' else 'summary', 'twitter:title': page['title'], 'twitter:description': page['description'], 'twitter:image': page['image']}.items():
        set_meta(soup, key, value)
    for link in soup.select('link[rel="canonical"]'):
        link.decompose()
    soup.head.append(soup.new_tag('link', rel='canonical', href=url))
    for script in soup.select('script[type="application/ld+json"]'):
        script.decompose()
    web_page = {'@type': 'ProfilePage' if file in ['index', 'about'] else 'WebPage', '@id': url + '#webpage', 'url': url, 'name': page['title'], 'description': page['description'], 'inLanguage': 'en', 'isPartOf': {'@id': website_id}, 'about': {'@id': person_id}}
    graph = [person, website, web_page]
    if file in ['index', 'about']:
        web_page['mainEntity'] = {'@id': person_id}
    if file != 'index':
        breadcrumb_id = url + '#breadcrumbs'
        web_page['breadcrumb'] = {'@id': breadcrumb_id}
        graph.append({'@type': 'BreadcrumbList', '@id': breadcrumb_id, 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': origin + '/'}, {'@type': 'ListItem', 'position': 2, 'name': page.get('project', {}).get('name', 'About' if file == 'about' else 'Robotics & Nena AI'), 'item': url}]})
    if page.get('project'):
        project = page['project']
        web_page['mainEntity'] = {'@id': url + '#case-study'}
        graph.append({'@type': 'CreativeWork', '@id': url + '#case-study', 'name': project['name'] + ' — development case study', 'description': page['description'], 'url': url, 'author': {'@id': person_id}, 'about': {'@type': 'Thing', 'name': project['name'], 'url': project['url']}})
    if file == 'index':
        for i, service in enumerate(data['services']):
            graph.append({'@type': 'Service', '@id': origin + '/#service-' + str(i + 1), 'name': service['title'], 'description': service['description'], 'provider': {'@id': person_id}, 'areaServed': {'@type': 'Country', 'name': 'Tanzania'}, 'url': origin + '/'})
    page['schema'] = {'@context': 'https://schema.org', '@graph': graph}
    tag = soup.new_tag('script', type='application/ld+json', id='portfolio-structured-data')
    tag.string = json.dumps(page['schema'], ensure_ascii=False).replace('</', '<\\/')
    soup.head.append(tag)
    for script in soup.select('script[src="/assets/personal/seo.js"]'):
        script.decompose()
    soup.head.append(soup.new_tag('script', src='/assets/personal/seo.js', defer=''))
    path.write_text(str(soup), encoding='utf8')

# Keep Framer's client navigation from restoring pre-SEO titles and descriptions.
patched = 0
for path in (DIST / 'assets/framerusercontent.com/sites').rglob('*.mjs'):
    text = path.read_text(encoding='utf8')
    if 'serializationId:' not in text and not path.name.startswith('siteMetadata.'):
        continue
    for old_title, page in old_titles.items():
        if 'title:`' + old_title + '`' not in text:
            continue
        for field, value in [('title', page['title']), ('description', page['description']), ('socialImage', page['image'])]:
            literal = value.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
            text = re.sub(r'\b' + field + r':`[^`]*`', lambda _: field + ':`' + literal + '`', text)
        text = text.replace('robots:`max-image-preview:large`', 'robots:`index, follow, max-image-preview:large`')
        path.write_text(text, encoding='utf8')
        patched += 1
        break

# Captured auxiliary page should never compete with the homepage.
auxiliary = BeautifulSoup((DIST / 'index.html').read_text(encoding='utf8'), 'html.parser')
set_meta(auxiliary, 'robots', 'noindex, follow')
(DIST / 'test-1.html').write_text(str(auxiliary), encoding='utf8')
not_found = BeautifulSoup((DIST / '404.html').read_text(encoding='utf8'), 'html.parser')
set_meta(not_found, 'robots', 'noindex, follow')
for link in not_found.select('link[rel="canonical"]'):
    link.decompose()
(DIST / '404.html').write_text('\n'.join(line.rstrip() for line in str(not_found).splitlines()) + '\n', encoding='utf8')

namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', namespace)
sitemap = ET.Element('{' + namespace + '}urlset')
for page in pages.values():
    item = ET.SubElement(sitemap, '{' + namespace + '}url')
    ET.SubElement(item, '{' + namespace + '}loc').text = origin + page['path']
(DIST / 'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8', xml_declaration=True))
(DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /healthz\n\nSitemap: ' + origin + '/sitemap.xml\n', encoding='utf8')
print('SEO generated:', len(pages), 'pages,', patched, 'client metadata modules, sitemap and robots.txt for', origin)
client_pages = {p['path']: {key:p[key] for key in ['title','description','image','schema']} for p in pages.values()}
client_script = (ROOT / 'scripts/seo.js').read_text(encoding='utf8').replace('__PORTFOLIO_SEO__', json.dumps(client_pages, ensure_ascii=False)).replace('__PORTFOLIO_ORIGIN__', json.dumps(origin))
(DIST / 'assets/personal/seo.js').write_text(client_script, encoding='utf8')
