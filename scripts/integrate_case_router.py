"""Render editorial cases through the captured site's existing React router."""
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
MODULES = DIST / 'assets/framerusercontent.com/sites/2Wv4lVIfy23BjKEhMEIflQ'
ROUTES = {
 'ecofy': ('OJvd1BNaN', 'tWQA6IJBe3Wdm-1eSOzWrKC1JTe2omds3DjR2G8y2Kk.OMX9iHe2.mjs'),
 'osher-market': ('IhYkVKpYR', 'DOurT0eDuGjc6Nyg5Srhyw4nDbl1qNmybk-8tLBkboM.CilSFsOk.mjs'),
 'wakili-msomi': ('boFkVS3RZ', '1kQr3Z6k0QXna3mbebFk-z1w0OqfQjvwaFux-7IHbyA.Bf8-sypP.mjs'),
 'falco': ('Zmwx4Ibvc', 'uoXJpS21HxLbQ2wfzCzL2eT58OyD83Fi3jRP1SWbkgE.CtQIKUoU.mjs'),
 'habitek': ('mld1MIphZ', '9Cf809bSUX8DRk-bIDmjGbe0Z12NsuBgEfHnX_l5LLo.Dw0hhBHJ.mjs'),
 'tanstack-tanzania': ('wi2Xaghpb', 'U0naiUYiF_AWE5tsteYWQYYkjYNpA6GBb8ZAOEp3hCQ.Cdw_3_DS.mjs'),
 'globoexpats': ('kuKUydbQG', 'xzmC7tbR0Z7ka88fnCsKLHr7ed179DTgWpC463xhh8o.a2lLmhtJ.mjs'),
}

def integrate(captured_pages):
    for i, (slug, (_, filename)) in enumerate(ROUTES.items()):
        path = DIST / (slug + '.html')
        editorial = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
        captured = BeautifulSoup(captured_pages[slug], 'html.parser')
        content = ''.join(str(editorial.select_one(selector)) for selector in ['.skip-link', '.case-shell', '.case-footer'])
        root = captured.select_one('[data-framer-root]')
        root.clear()
        root['class'] = 'portfolio-case-root'
        root.append(BeautifulSoup(content, 'html.parser'))
        path.write_text(str(captured), encoding='utf8')
        module = MODULES / filename
        source = module.read_text(encoding='utf8')
        match = re.search(r'export\{([^}]+)\}', source)
        original = re.search(r'([^,]+) as default', match.group(1)).group(1)
        adapter = 'PortfolioCase' + str(i)
        addition = '\nimport{makeCasePage}from"./portfolio-cases.mjs";\nconst ' + adapter + '=makeCasePage(' + json.dumps(content, ensure_ascii=False) + ',' + original + ');\n'
        source = source[:match.start()] + addition + source[match.start():].replace(original + ' as default', adapter + ' as default', 1)
        module.write_text(source, encoding='utf8')
    css = (ROOT / 'scripts/case-studies.css').read_text(encoding='utf8')
    # Prefix selectors, including inside media rules, without touching keyframes.
    css = re.sub(r'(^|[{}])([^{}@]+)\{', lambda m: m.group(1) + ','.join('.portfolio-case-root' if v.strip() in [':root','body','html'] else '.portfolio-case-root ' + v.strip() for v in m.group(2).split(',')) + '{', css)
    css = css.replace('.portfolio-case-root from', 'from').replace('.portfolio-case-root to', 'to')
    css += '\n.portfolio-case-root {color:#111; font:18px/1.6 "Inter Display",Inter,Arial,sans-serif; --line:#d4d4d4; --muted:#737373;}\n'
    (DIST / 'assets/personal/case-studies.css').write_text(css, encoding='utf8')
    routes = {'/':'UTNT6GAXH', '/about':'XdYBo4_p8', **{'/' + slug: entry[0] for slug, entry in ROUTES.items()}}
    adapter = (ROOT / 'scripts/case-router.mjs').read_text(encoding='utf8').replace('__ROUTES__', json.dumps(routes))
    (MODULES / 'portfolio-cases.mjs').write_text(adapter, encoding='utf8')
    for path in DIST.glob('*.html'):
        soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
        soup.head.append(soup.new_tag('link', rel='stylesheet', href='/assets/personal/case-studies.css'))
        soup.head.append(soup.new_tag('script', src='/assets/personal/case-interactions.js', defer=''))
        path.write_text(str(soup), encoding='utf8')
