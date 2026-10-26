"""Apply editable portfolio content to the captured Framer presentation.

The immutable capture commit is the input, so this is safe to run repeatedly.
Motion components, font files, layout rules and responsive variants are retained.
"""
from pathlib import Path
from collections import OrderedDict
import copy
import html
import json
import re
import subprocess
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd644207659b68a8a866714bf4216042a9229802a'
DIST = ROOT / 'dist'
DATA = json.loads((ROOT / 'content/portfolio.json').read_text(encoding='utf8'))
ORIGIN = 'https://daniel-sun-portfolio-replica.darkseed8192.chatgpt.site'
PERSONAL = DIST / 'assets/personal'
PERSONAL.mkdir(parents=True, exist_ok=True)
MAPPINGS = {}
ASSETS = {}
CASE_HEADINGS = {}
TOOL_LABELS = {'figma':'Python','webflow':'FastAPI','framer':'Docker','illustrator':'PostgreSQL','photoshop':'Linux','after effects':'nginx','my brain':'Engineering judgment','chat gpt':'LLM APIs','branding':'backend engineering','logotype':'API design','brand research':'data modeling','ui/ux research':'requirements','illustrations':'AI integration','website design':'backend APIs','visual direction':'architecture','design system':'service design','framer development':'deployment','portfolio research':'document ingestion','icons & illustrations':'data processing','web platform design':'platform APIs','illustrations creation':'service configuration','marketing design':'product planning','illustrations & icons design':'data processing','agent development':'AI services'}

def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT).decode('utf8')

def out(name, text):
    (PERSONAL / name).write_text(text, encoding='utf8')
    return '/assets/personal/' + name

def esc(value):
    return html.escape(str(value), quote=True)

def text(x,y,size,value,fill='#151515',**kwargs):
    attrs=' '.join(f'{k.replace("_", "-")}="{esc(v)}"' for k,v in kwargs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {attrs}>{esc(value)}</text>'

def svg(body, width=1600, height=1000):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Arial, Helvetica, sans-serif">{body}</svg>'

def wordmark(label, dark=False):
    return out('word-' + re.sub(r'[^a-z0-9]','',label.lower()) + ('-dark' if dark else '') + '.svg', svg(text(160,68,44,label,'#fff' if dark else '#111',text_anchor='middle',font_weight='600'),320,100))

def monogram(label, color='#e8e8e8', ink='#111'):
    key=re.sub(r'[^a-z0-9]','',label.lower())
    return out('mark-'+key+'.svg',svg(f'<rect width="200" height="200" rx="38" fill="{color}"/>'+text(100,125,60,label,ink,text_anchor='middle',font_weight='600'),200,200))

def panel(project, variant=0):
    """Editorial technical diagrams, explicitly presented as illustrative sketches."""
    if project.get('detailAssets'):
        return project['detailAssets'][variant%len(project['detailAssets'])]
    p=project
    mode=variant%5
    bg=p['color']; ink=p['ink']
    b=f'<rect width="1600" height="1000" fill="{bg}"/>'
    b+='<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#000" opacity=".05"/></pattern></defs><rect width="1600" height="1000" fill="url(#grid)"/>'
    b+=text(75,82,22,'ISACK LUGATA / ENGINEERING NOTES',ink,letter_spacing='3')
    b+=text(75,195,72,p['name'],ink,letter_spacing='-3')
    b+=text(75,246,25,['A system, from input to outcome.','How the pieces fit together.','The tools behind the work.','The engineering focus.','Where the work stands.'][mode],ink)
    b+='<rect x="65" y="310" width="1470" height="535" rx="22" fill="#fff" fill-opacity=".78" stroke="#000" stroke-opacity=".10"/>'
    if mode in (0,1):
        for i,label in enumerate(p['flow']):
            x=110+i*355
            if mode==0:
                b+=f'<rect x="{x}" y="430" width="310" height="250" rx="16" fill="{bg}" stroke="{ink}" stroke-opacity=".15"/>'
                b+=text(x+25,480,22,f'0{i+1}',ink)
                words=label.split();line='';lines=[]
                for word in words:
                    if len(line+' '+word)>17:lines.append(line);line=word
                    else:line=(line+' '+word).strip()
                lines.append(line)
                for j,line in enumerate(lines):b+=text(x+25,557+j*42,30,line,ink,font_weight='500')
                if i<3:b+=f'<path d="M{x+317} 553 h28 m-9 -8 9 8 -9 8" fill="none" stroke="{ink}" stroke-width="2"/>'
            else:
                y=355+i*110
                b+=text(110,y+35,22,f'0{i+1}',ink)
                b+=text(190,y+35,37,label,ink)
                b+=f'<path d="M110 {y+70} H1490" stroke="{ink}" stroke-opacity=".12"/>'
        b+=text(110,795,21,'Conceptual flow. Actual implementation details vary by project.',ink)
    elif mode==2:
        b+=text(115,375,22,'TECHNICAL TOOLKIT',ink,letter_spacing='2')
        for i,tool in enumerate(p['stack']):
            x=115+(i%2)*700;y=425+(i//2)*115
            b+=f'<rect x="{x}" y="{y}" width="640" height="88" rx="12" fill="{bg}"/>'
            b+=text(x+28,y+57,32,tool,ink)
    elif mode==3:
        b+=text(115,390,23,'MY CONTRIBUTION',ink,letter_spacing='2')
        words=p['role'].split(); lines=[];line=''
        for word in words:
            if len(line+' '+word)>43:lines.append(line);line=word
            else:line=(line+' '+word).strip()
        lines.append(line)
        for j,line in enumerate(lines):b+=text(115,465+j*58,43,line,ink)
        b+=text(115,720,24,'Thoughtful interfaces between data, logic, and people.',ink)
        b+=text(115,770,23,'Team contributions are described separately in the case study.',ink)
    else:
        b+=text(115,390,23,'PROJECT STATUS',ink,letter_spacing='2')
        words=p['status'].split();lines=[];line=''
        for word in words:
            if len(line+' '+word)>50:lines.append(line);line=word
            else:line=(line+' '+word).strip()
        lines.append(line)
        for j,line in enumerate(lines):b+=text(115,475+j*52,36,line,ink)
        b+=text(115,680,24,'Next: review shareable screenshots, scope, and outcomes.',ink)
        b+=text(115,735,23,'No unverified adoption, revenue, or performance claims.',ink)
    b+=text(75,928,21,'ILLUSTRATIVE TECHNICAL SKETCH / NOT A PRODUCT SCREENSHOT',ink,letter_spacing='2')
    b+=text(1525,928,21,f'{variant+1:02}',ink,text_anchor='end')
    return out(f'{p["slug"]}-{variant}.svg',svg(b))

manifest=json.loads((ROOT/'asset-manifest.json').read_text(encoding='utf8'))
reverse={v['path']:urllib.parse.urlsplit(k).path for k,v in manifest['assets'].items()}
groups={}
for url,asset in manifest['assets'].items():
    groups.setdefault(urllib.parse.urlsplit(url).path,[]).append(asset['path'])

def asset(source,target):
    if not source:return
    key=reverse.get(source)
    for variant in groups.get(key,[source]):ASSETS[variant]=target

def add(old,new):
    if old and old!=new:MAPPINGS[old]=new

def cover(project):
    image=project.get('artwork') or project.get('cover')
    return image if image and (DIST/image.lstrip('/')).is_file() else panel(project,0)

def long_paragraphs(soup):
    return list(OrderedDict((p.get_text(),p) for p in soup.select('#main p') if len(p.get_text())>90).values())

pages={n:BeautifulSoup(original('dist/'+n+'.html'),'html.parser') for n in ['index','about','404','test-1']+[p['legacy'] for p in DATA['projects']]}
home=pages['index'];about=pages['about']

for name,soup in pages.items():
    for label in soup.select('#main p'):
        if label.get_text() in TOOL_LABELS:label.string=TOOL_LABELS[label.get_text()]
    project=next((p for p in DATA['projects'] if p['legacy']==name),None)
    if project:
        headings=[h for h in soup.select('#main h2,#main h3') if h.get_text()!='Other projects']
        CASE_HEADINGS[project['slug']]=[]
        for i,heading in enumerate(headings):
            replacement=project['sections'][i%len(project['sections'])]
            CASE_HEADINGS[project['slug']].append((heading.get_text(),replacement));heading.string=replacement
        for i,label in enumerate(soup.select('[data-framer-name="tags"] p')):label.string=project['stack'][i%len(project['stack'])]
        for label in soup.select('#main p'):
            if label.get_text() in ['Tools','Services']:label.string={'Tools':'Focus','Services':'Contribution'}[label.get_text()]
    newtitle=(project['name']+' — ' if project else ('About ' if name=='about' else ''))+DATA['name']+(' | '+DATA['title'] if not project else '')
    if soup.title:add(soup.title.get_text(),newtitle)
    for meta in soup.select('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]'):
        add(meta.get('content',''),project['summary'] if project else DATA['intro'])
    for meta in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
        if meta.get('content'):asset(meta['content'],panel(DATA['projects'][0],0))

add(home.h1.get_text(),DATA['hero'])
add(about.h1.get_text(),DATA['aboutHero'])
# Keep the reference's adventure heading and paper-collage composition.

for old,new in zip(long_paragraphs(about),DATA['about']):add(old.get_text(),new)

for p in DATA['projects']:
    soup=pages[p['legacy']]
    paras=long_paragraphs(soup)
    for old,new in zip(paras,[p['summary']]+p['story']):
        # The original introduction sometimes has a separate linked project name.
        leaves=list(old.strings)
        if len(leaves)>1 and str(leaves[0]).strip()==p['oldName']:
            add(str(leaves[1]),' '+new[len(p['name']):].lstrip() if new.startswith(p['name']) else ' — '+new)
        else:add(old.get_text(),new)
    add(p['oldName'],p['name'])
    add('./'+p['legacy'],'./'+p['slug'])
    add('path:`/'+p['legacy']+'`','path:`/'+p['slug']+'`')
    add('https://danielsun.space/'+p['legacy'],ORIGIN+'/'+p['slug'])
    # Project assets are replaced by genuine engineering diagrams, not borrowed work.
    for i,img in enumerate(soup.select('#main img')):
        if not img.find_parent(attrs={'data-framer-name':'project stack'}):continue
        src=img.get('src')
        parents=[a.get('data-framer-name','') for a in list(img.parents)[:9]]
        if any(a in ['X','sun white-pic','moon black-pic'] for a in parents):continue
        if 'logo' in ' '.join(parents).lower() or i==0:
            asset(src,monogram(p['shortName'][:2].upper(),p['color'],p['ink']))
        elif src not in ASSETS:
            asset(src,cover(p) if i==1 else panel(p,i%5))

# Project covers (including all responsive variants) use the relevant project sketch.
for p in DATA['projects']:
    for a in home.select(f'a[href="./{p["legacy"]}"]'):
        labels=a.select('p')
        if not labels or labels[0].get_text()!=p['oldName']:continue
        for img in a.select('img'):asset(img.get('src'),cover(p))
        for i,label in enumerate(a.select('p')[1:]):label.string=p['tags'][i%len(p['tags'])]

# The source's client marquee becomes a technology marquee: no borrowed affiliations.
tools=['React','Python','FastAPI','Docker']
for i,img in enumerate([x for x in home.select('img') if ' logo' in x.get('alt','')]):
    label=tools[i%4];asset(img.get('src'),wordmark(label));add(img.get('alt'),label)

# Replace personal photographs and former employers' marks on the Story page.
try:
    if not (PERSONAL/'portrait.png').exists():
        urllib.request.urlretrieve('https://avatars.githubusercontent.com/u/176749061?v=4',PERSONAL/'portrait.png')
except Exception:
    pass
aboutimgs=about.select('#main img')
for i,img in enumerate(aboutimgs[2:7]):
    target='/assets/personal/portrait.png' if i==0 and (PERSONAL/'portrait.png').exists() else panel(DATA['projects'][[0,0,5,6,2][i]],i)
    asset(img.get('src'),target)
for i,img in enumerate(aboutimgs[7:13]):
    asset(img.get('src'),monogram(['EA','TT','BF','3D','CS','IL'][i]))
for i,img in enumerate(aboutimgs[14:23]):asset(img.get('src'),panel(DATA['projects'][[6,0,5][i%3]],i%3))

# The existing exploration carousel and service imagery keep their motion containers.
for i,img in enumerate(home.select('#main img')[35:58]):
    asset(img.get('src'),monogram(['WEB','APP','API','AI'][min(i//4,3)]) if i<15 else cover(DATA['projects'][[6,2,5,0][(i-15)%4]]))

service_old=[
 'I start from scratch, define goals the site actually has to achieve, then comes shape structure, navigation, and every UI element around them.',
 'I build what I design in Framer or Webflow, down to the smallest interactions that make a site feel alive without ever pulling focus.',
 'From logo and type to colors, patterns, and graphics, delivered as one handoff your team can actually follow, so what you ship later still flows.',
 'Custom icons, product visuals, isometric scenes made for you only is the fastest way to explain the product and make people feel something.'
]
for old,new in zip(service_old,DATA['services']):add(old,new['description'])

shared={
 '6+ years designing for tech founders. Seed to Series C, across fintech, dev tools, and Web3.':DATA['intro'],
 '6+ years designing for tech founders. ':'Full-stack & mobile developer. ',
 'Seed to Series C, across fintech, dev tools, and Web3.':'Dar es Salaam. Co-founder of Ecofy Africa.',
 'Companies I helped:':'Companies I helped:',
 'Brand identity':DATA['services'][2]['title'],
 'Illustration':DATA['services'][3]['title'],
 'Web design':DATA['services'][0]['title'],
 'Development':DATA['services'][1]['title'],
 'Branding':'Systems',
 'Marketing':'Product',
 'Platform design':'Engineering',
 'Web platform':'Backend architecture',
 'Visual direction & Web design':'Implementation & architecture',
 'Events and swag':'Engineering decisions',
 'Currently open to collaborations':'Open to freelance projects & collaborations',
 'Download my CV':'Request my CV',
 'Senior Web & Brand designer':'Co-founder, CEO & AI Lead',
 'Senior Brand & Web designer':'Backend Developer',
 'Senior Web Designer':'Practical Training',
 'Middle Web Designer':'Former chairperson, Robotics Lab',
 'Junior Web Designer':'Computer Science studies',
 'at O0 Design':'at TanStack Tanzania',
 'at Ooze':'at Bluefin Solutions',
 'at Heartbeat':'at UDSM CoICT',
 'at HaloLab':'at University of Dar es Salaam',
 'Freelance work':'Web, mobile & backend projects',
 'for different companies':'for founders & teams',
 'Dec 2024 - Jul 2026':'2025 - present',
 'Mar 2024 - Dec 2024':'2026 - present',
 'Mar 2023 - Feb 2024':'Practical training',
 'Dec 2020 - Feb 2023':'Previous leadership role',
 'May 2020 - Dec 2020':'2023 - 2026',
 'Jan 2021 - Now':'Project-based',
 'hello@danielsun.space':DATA['email'],
 'Daniel Sun':DATA['name'],
 'https://www.linkedin.com/in/daniel-sun-design/':'https://www.linkedin.com/in/isack-lugata-a6356531a/',
 'https://x.com/danielsun_ui':'https://github.com/GhostWire619',
 'https://www.instagram.com/daniel.sun_design/':'mailto:'+DATA['email'],
 'https://www.threads.com/@daniel.sun_design':DATA['lab']['url'],
 'https://pinterest.com/daniel_sun_design/':'#unused-social',
 'https://dribbble.com/daniel_sun':'#unused-social',
 'https://drive.google.com/file/d/1GoylHM-evy5PBWtHRkDwa8ltOfER8Njk/view?usp=share_link':'mailto:'+DATA['email']+'?subject=Current%20engineering%20CV',
 'https://danielsun.space/':ORIGIN+'/',
 'Web & brand designer for SaaS and Web3 founders':DATA['title'],
 'designer making founders more competitive':'Full-stack developer, mobile builder & founder',
 'Card image':'Isack Lugata: engineering and exploration',
 'Daniel Sun on X':'Isack Lugata on GitHub',
 'Daniel Sun on Instagram':'Email Isack Lugata',
 'Daniel Sun on LinkedIn':'Isack Lugata on LinkedIn',
 'Daniel Sun on Threads':'UDSM 3D Solutions & Robotics Lab',
 'Daniel Sun on Pinterest':'',
 'Daniel Sun on Dribbble':''
}
for a,b in shared.items():add(a,b)

# Social artwork: four genuine destinations and no guessed personal accounts.
for soup in pages.values():
    for a in soup.select('a[href]'):
        url=a['href']
        label=None
        if 'x.com/danielsun_ui' in url:label='GH'
        elif 'instagram.com/daniel.sun_design' in url:label='@'
        elif 'threads.com/@daniel.sun_design' in url:label='3D'
        if label:
            for img in a.select('img'):
                dark=img.get('src') in {x.get('src') for x in about.select('a[href="'+url+'"] img')}
                asset(img.get('src'),wordmark(label,dark))

for soup in pages.values():
    for a in soup.select('a[href*="drive.google.com"]'):add(a['href'],'mailto:'+DATA['email']+'?subject=Current%20engineering%20CV')

# Faithful visual pass: genuine identities and the reference's dimensional artwork.
def restore_asset(src):
    for path in groups.get(reverse.get(src),[src]):ASSETS.pop(path,None)

visuals=DATA.get('visuals',{})
if visuals:
    for i,img in enumerate(aboutimgs[2:7]):asset(img.get('src'),visuals['photos'][i])
    for i,img in enumerate(aboutimgs[7:12]):asset(img.get('src'),f'/assets/identity/career-{i}.svg')
    restore_asset(aboutimgs[12].get('src'))
    for img in aboutimgs[14:23]:
        name=img.get('src','')
        if 'SVpEFYyf' in name:asset(name,visuals['readyNote'])
        elif 'ksM1tOjo' in name:asset(name,visuals['readyPhoto'])
        else:restore_asset(name)
    service_images=home.select('#main img')[35:50]
    for img in service_images:
        src=img.get('src','')
        if 'fuMe9' in src:restore_asset(src)
        elif '94BIn' in src:asset(src,visuals['services'][1])
        elif 'lPKpA' in src:asset(src,'/assets/identity/blank.svg')
        elif 'ii9hv' in src:asset(src,visuals['services'][2])
        elif 'YcxPf' in src:asset(src,visuals['services'][3])
    for soup in pages.values():
        for a in soup.select('a[href]'):
            url=a['href'];icon=None
            if 'x.com/danielsun_ui' in url:icon='github'
            elif 'instagram.com/daniel.sun_design' in url:icon='envelope'
            elif 'threads.com/@daniel.sun_design' in url:icon='globe'
            if icon:
                for img in a.select('img'):
                    dark=img.get('src') in {x.get('src') for x in about.select('a[href="'+url+'"] img')}
                    asset(img.get('src'),f'/assets/identity/icon-{icon}-'+('dark' if dark else 'light')+'.svg')
    for project in DATA['projects']:
        if project.get('icon'):
            first=pages[project['legacy']].select_one('#main img')
            if first:asset(first.get('src'),project['icon'])
    for i,img in enumerate([x for x in home.select('img') if ' logo' in x.get('alt','')]):
        company=DATA['companies'][i%len(DATA['companies'])]
        asset(img.get('src'),company['logo'])
        MAPPINGS[img.get('alt')]=company['name']

# Replace project-image descriptions rather than leaving another person's work in alt text.
for soup in pages.values():
    for img in soup.select('img[alt]'):
        old=img['alt']
        if len(old)>45 and img.get('src') in ASSETS:
            target=ASSETS[img.get('src')]
            project=next((p for p in DATA['projects'] if p.get('cover')==target),None)
            add(old,(project['name']+' public website preview; my contribution: '+project['role']) if project else 'Illustrative technical sketch from Isack Lugata’s project notes')

def replace_all(value):
    # One pass prevents short names from rewriting newly inserted content.
    mapping={}
    for old,new in {**MAPPINGS,**ASSETS}.items():
        mapping[old]=new
        mapping[html.escape(old,quote=False)]=html.escape(new,quote=False)
        mapping[html.escape(old,quote=True)]=html.escape(new,quote=True)
        mapping[json.dumps(old,ensure_ascii=False)[1:-1]]=json.dumps(new,ensure_ascii=False)[1:-1]
    pattern=re.compile('|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True)))
    return pattern.sub(lambda m:mapping[m.group()],value)

schema=json.dumps({'@context':'https://schema.org','@type':'Person','name':DATA['name'],'url':ORIGIN,'jobTitle':DATA['title'],'email':DATA['email'],'homeLocation':{'@type':'Place','name':DATA['location']},'sameAs':['https://github.com/GhostWire619','https://www.linkedin.com/in/isack-lugata-a6356531a/']},ensure_ascii=False)
schema_tag='<script type="application/ld+json">'+schema+'</script>'

def clean_snippets(raw):
    raw=re.sub(r'<script type="application/ld\+json">.*?</script>',schema_tag,raw,flags=re.S)
    raw=re.sub(r'<meta name="p:domain_verify"[^>]*>','',raw)
    return raw

def animated_heading(tag,new):
    char=tag.select_one('span span')
    if not char:
        tag.string=new;return
    style=char.get('style','')
    tag.clear()
    for i,word in enumerate(new.split(' ')):
        if i:tag.append(' ')
        wrap=home.new_tag('span',style='white-space:nowrap')
        for ch in word:
            letter=home.new_tag('span',style=style);letter.string=ch;wrap.append(letter)
        tag.append(wrap)

for name,soup in pages.items():
    for h in soup.select('h1,h2,h3'):
        old=h.get_text()
        if old in MAPPINGS and h.select_one('span span'):animated_heading(h,MAPPINGS[old])
    # Canonical metadata and personal sharing image.
    for meta in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):meta['content']=ORIGIN+panel(DATA['projects'][0],0)
    for tag in soup.select('link[rel="icon"],link[rel="apple-touch-icon"]'):tag['href']=monogram('IL','#fff16a')
    for tag in soup.select('meta[name="p:domain_verify"]'):tag.decompose()
    for tag in soup.select('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]'):tag['content']=DATA['intro']
    for tag in soup.select('script[type="application/ld+json"]'):tag.string=schema
    link=soup.new_tag('link',rel='stylesheet',href='/assets/personal/personal.css');soup.head.append(link)
    script=soup.new_tag('script',src='/assets/personal/personal.js');script['defer']='';soup.head.append(script)
    output=replace_all(clean_snippets(str(soup)))
    (DIST/(name+'.html')).write_text(output,encoding='utf8')
    project=next((p for p in DATA['projects'] if p['legacy']==name),None)
    if project:
        # Each case study receives a clean canonical route while old bookmarks stay usable.
        newsoup=BeautifulSoup(output,'html.parser')
        title=project['name']+' — '+DATA['name']
        newsoup.title.string=title
        for meta in newsoup.select('meta[property="og:title"],meta[name="twitter:title"]'):meta['content']=title
        for link in newsoup.select('link[rel="canonical"]'):link['href']=ORIGIN+'/'+project['slug']
        output=str(newsoup)
        (DIST/(project['slug']+'.html')).write_text(output,encoding='utf8')
        (DIST/(name+'.html')).write_text(output,encoding='utf8')

paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'dist'],cwd=ROOT,text=True).splitlines()
for filename in paths:
    if filename.endswith('.mjs'):
        raw=original(filename)
        raw=clean_snippets(raw)
        raw=replace_all(raw)
        # Tool names are literal text children, never framework identifiers.
        for old,new in TOOL_LABELS.items():
            raw=raw.replace('children:`'+old+'`','children:`'+new+'`')
        case=next((p for p in DATA['projects'] if p['story'][0] in raw),None)
        if case:
            for old,new in CASE_HEADINGS.get(case['slug'],[]):
                raw=raw.replace('children:`'+MAPPINGS.get(old,old)+'`','children:`'+new+'`')
            tag_index=[0]
            def case_tag(match):
                label=case['stack'][tag_index[0]%len(case['stack'])];tag_index[0]+=1
                return 'gGxJjYTTd:`'+label+'`'
            raw=re.sub(r'gGxJjYTTd:`[^`]*`',case_tag,raw)
            raw=raw.replace('children:`Tools`','children:`Focus`').replace('children:`Services`','children:`Contribution`')
        for project in DATA['projects']:
            pattern=r'(\w+\(\w+,\{Ciu1NbIJT:(?:(?!RehjAvB2r).){0,2400}?RehjAvB2r:`'+re.escape(project['name'])+r'`.{0,450}?YjyOs65XK:`[^`]*`)'
            def tags(match):
                block=match.group(0)
                for key,value in zip(['YjyOs65XK','f_gW6t3il','kQkO0Igq2'],project['tags']):block=re.sub(key+r':`[^`]*`',key+':`'+value+'`',block)
                return block
            raw=re.sub(pattern,tags,raw)
        (ROOT/filename).write_text(raw,encoding='utf8')

# Explicit personal metadata for the old auxiliary capture page.
(DIST/'test-1.html').write_text((DIST/'index.html').read_text(encoding='utf8'),encoding='utf8')
out('personal.css','''
/* Small content-specific corrections; the original Framer layout and motion remain. */
a[href*="unused-social"],a[href*="pinterest.com"],a[href*="dribbble.com"],div[class*="-container"]:has(>a[href*="unused-social"]),div[class*="-container"]:has(>a[href*="pinterest.com"]),div[class*="-container"]:has(>a[href*="dribbble.com"]) { display:none !important; }
video { object-fit:cover !important; visibility:hidden !important; }
img[src^="/assets/personal/"][src$=".svg"] { object-fit:contain !important; object-position:center !important; }
img[src^="/assets/identity/cover-"] { object-fit:cover !important; object-position:center !important; }
img[src^="/assets/identity/story-"],img[src^="/assets/identity/ready-"],img[src^="/assets/identity/icon-"],img[src^="/assets/identity/career-"] { object-fit:contain !important; object-position:center !important; }
.personal-companies-grid { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; grid-template-rows:none !important; grid-auto-rows:132px !important; height:auto !important; }
.personal-company-cell { height:132px !important; min-width:0 !important; display:flex !important; justify-content:center !important; align-items:center !important; }
.personal-company-hidden { display:none !important; }
.personal-companies-grid [data-framer-name="image 3"] { width:72% !important; max-width:180px !important; height:48px !important; }
.personal-companies-grid img { object-fit:contain !important; object-position:center !important; filter:grayscale(1); }
@media(max-width:640px) { .personal-companies-grid { grid-template-columns:repeat(2,minmax(0,1fr)) !important; grid-auto-rows:108px !important; } .personal-company-cell { height:108px !important; } }
[data-framer-name="cards"] > [data-framer-name="block"] > :nth-child(n+3) { display:none !important; }
.personal-confirmation { border-left:2px solid currentColor; padding-left:16px; opacity:.7; }
.personal-live-link { display:inline-flex; width:fit-content; align-self:flex-start; padding:10px 15px; margin-top:16px; border-radius:8px; background:linear-gradient(#555,#111); box-shadow:inset 0 0 0 1px #000,0 3px 6px #0003; color:white !important; font:14px Inter,sans-serif !important; text-decoration:none !important; }
[data-framer-name="tags"] > :nth-child(n+5) { display:none !important; }
.personal-project-role { display:block; margin-top:10px; font:12px/1.5 Inter,sans-serif; opacity:.65; }
[data-personal-gallery] { cursor:pointer; }
[data-personal-gallery]::after { content:attr(data-personal-gallery-label); white-space:pre-line; position:absolute; inset:0; z-index:5; display:flex; align-items:flex-end; padding:22px; background:linear-gradient(transparent 45%,#000b); color:white; font:16px/1.6 Inter,sans-serif; pointer-events:none; }
@media (prefers-reduced-motion:reduce) {
  html { scroll-behavior:auto !important; }
  *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
}
'''+ '\n'.join('a[href="./'+p['slug']+'"] [data-framer-name="cover"] { background:'+p['color']+'; }' for p in DATA['projects']))
nena={'slug':'nena-ai','name':'Nena AI','color':'#e1cec0','ink':'#594237','flow':['Swahili text','Speech model','Generated speech','Audio experience'],'stack':['Swahili','Speech synthesis','Lab collaboration'],'role':'Team lab project','status':'Lab text-to-speech project','detailAssets':['/assets/identity/cover-nena.svg']}
gallery=[
 {'title':'Nena AI','subtitle':'Swahili speech · Lab team project','href':'/robotics#nena-ai','image':panel(nena,0)},
 {'title':'3D Solutions & Robotics','subtitle':'Backend · Former chairperson','href':'/robotics','image':DATA['lab']['cover']},
 {'title':'TanStack Tanzania','subtitle':'Backend development','href':'/tanstack-tanzania','image':'/assets/personal/tanstack-live.png'},
 {'title':'GloboExpats','subtitle':'Mainly frontend development','href':'/globoexpats','image':'/assets/personal/globoexpats-live.png'}
]
out('personal.js','''
(() => {
  const gallery = '''+json.dumps(gallery)+''';
  const projects = '''+json.dumps([{**{k:p.get(k) for k in ['slug','name','role','url']},'cover':cover(p)} for p in DATA['projects']])+''';
  const companies = '''+json.dumps(DATA.get('companies',[]))+''';
  let pending = false;
  function update() {
    pending = false;
    function setCover(img, project) {
      if (img.getAttribute('src') !== project.cover) img.setAttribute('src', project.cover);
      if (img.hasAttribute('srcset')) img.removeAttribute('srcset');
      img.alt = project.name + ' — ' + project.role;
    }
    projects.forEach(project => {
      document.querySelectorAll(`a[href="./${project.slug}"],a[href="/${project.slug}"]`).forEach(a => {
        a.querySelectorAll('img').forEach(img => setCover(img, project));
      });
    });
    const companyGrid = document.querySelector('.framer-1yix6hu');
    if (companyGrid && companies.length) {
      companyGrid.classList.add('personal-companies-grid');
      [...companyGrid.children].forEach((cell,index) => {
        if (index >= companies.length) { cell.classList.add('personal-company-hidden'); return; }
        cell.classList.add('personal-company-cell');
        const img = cell.querySelector('img');
        if (img) {
          const company=companies[index];
          if (img.getAttribute('src') !== company.logo) img.src=company.logo;
          img.removeAttribute('srcset'); img.alt=company.name;
        }
      });
    }
    // Original showreels are replaced with labeled engineering sketches.
    document.querySelectorAll('video[src]').forEach((video, i) => {
      video.pause();
      video.removeAttribute('autoplay');
      const holder = video.parentElement;
      const item = gallery[i % gallery.length];
      holder.style.backgroundImage = `url("${item.image}")`;
      holder.style.backgroundSize = 'cover';
      holder.style.backgroundPosition = 'center';
      video.setAttribute('aria-hidden', 'true');
      video.style.visibility = 'hidden';
      video.removeAttribute('src');
      video.load();
      holder.dataset.personalGallery = item.href;
      holder.dataset.personalGalleryLabel = item.title + '\\n' + item.subtitle;
      holder.setAttribute('role', 'link'); holder.tabIndex = 0;
      holder.setAttribute('aria-label', item.title + ' — ' + item.subtitle);
      holder.addEventListener('click', event => { event.stopPropagation(); location.assign(item.href); }, true);
      holder.addEventListener('keydown', event => { if (event.key === 'Enter') location.assign(item.href); });
    });
    const project = projects.find(p => location.pathname === '/' + p.slug);
    if (project) {
      const heroImage = [...document.querySelectorAll('#main [data-framer-name="project stack"] img')].find(img => !img.closest('a') && img.getBoundingClientRect().width > 250);
      if (heroImage) setCover(heroImage, project);
    }
    if (project && !document.querySelector('.personal-live-link')) {
      const heading = document.querySelector('h1');
      const paragraphs = [...document.querySelectorAll('#main p')];
      const intro = paragraphs.find(p => p.textContent.length > 90);
      if (heading && intro) {
        const link = document.createElement('a');
        link.className = 'personal-live-link'; link.href = project.url;
        link.target = '_blank'; link.rel = 'noopener noreferrer';
        link.textContent = project.slug === 'falco' ? 'Company website ↗' : 'View live website ↗';
        const role = document.createElement('span');
        role.className = 'personal-project-role';
        role.textContent = 'My contribution: ' + project.role;
        intro.insertAdjacentElement('afterend', link);
        link.insertAdjacentElement('afterend', role);
      }
    }
    document.querySelectorAll('a[href*="pinterest.com"],a[href*="dribbble.com"],a[href*="unused-social"]').forEach(a => {
      a.style.display='none';
      if (a.parentElement.className.includes('-container')) a.parentElement.style.display='none';
    });
    document.querySelectorAll('#main a').forEach(a => {
      if (a.textContent.includes('More projects') && !a.dataset.personalPlaceholder) {
        a.dataset.personalPlaceholder='true'; a.setAttribute('aria-disabled','true');
        a.style.cursor='default'; a.tabIndex=-1;
        a.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();},true);
      }
    });
    document.querySelectorAll('p').forEach(p => { if (p.textContent.startsWith('[CONFIRM]')) p.classList.add('personal-confirmation'); });
    document.querySelectorAll('a[href="#unused-social"]').forEach(a => a.setAttribute('aria-hidden', 'true'));
    // Framer's original head snippets must not identify the previous portfolio owner.
    document.querySelectorAll('meta[name="p:domain_verify"]').forEach(m => m.remove());
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }
  function start() {
    // Wait for the captured motion tree to mount before enhancing its DOM.
    if (!window.MotionIsMounted) { requestAnimationFrame(start); return; }
    requestAnimationFrame(() => {
      update();
      new MutationObserver(schedule).observe(document.body, { childList:true, subtree:true, attributes:true, attributeFilter:['src'] });
    });
  }
  window.addEventListener('load', start, {once:true});
})();
''')
(ROOT/'content/REVIEW.md').write_text('# Content review\n\n'+ '\n'.join('- '+x for x in DATA['reviewNotes'])+'\n',encoding='utf8')

# The lab has its own editorial page, beyond the seven featured product slots.
fonts='\n'.join(re.findall(r'@font-face\s*\{[^}]*\}',original('dist/index.html')))
lab=DATA['lab']
lab_style='''
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:#111;background:#fff;font:16px/1.65 Inter,Arial,sans-serif}
header{height:52px;display:flex;align-items:center;justify-content:space-between;padding:0 25px;border-bottom:1px solid #ddd;background:#fff;position:sticky;top:0;z-index:10}a{color:inherit}header a{text-decoration:none}header nav{display:flex;gap:20px}
main{max-width:1200px;margin:auto;border-left:1px solid #ddd;border-right:1px solid #ddd}.lab-hero{padding:120px 48px 52px;background:radial-gradient(ellipse at 50% 0,#fff36b55,transparent 70%)}
h1,h2{font-family:'LT Superior Serif Regular',Georgia,serif;font-weight:400;letter-spacing:-.04em;line-height:1.08}h1{font-size:clamp(42px,5.3vw,68px);max-width:1000px;margin:18px 0 26px}h2{font-size:42px;margin:10px 0 22px}p{max-width:760px}.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.6}.lab-image{width:100%;display:block;border:1px solid #ddd;border-radius:12px}.lab-section{padding:48px;border-top:1px solid #ddd}.lab-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}.lab-grid img{width:100%;border-radius:12px}.lab-button{display:inline-flex;border-radius:8px;background:linear-gradient(#555,#111);color:#fff;text-decoration:none;padding:10px 16px;box-shadow:0 3px 8px #0003;font-size:14px}footer{max-width:1200px;margin:auto;padding:60px 30px;border-top:1px solid #ddd}footer a{font-size:clamp(24px,5vw,60px);font-family:'LT Superior Serif Regular',Georgia,serif;text-decoration:none}
@media(max-width:640px){.lab-hero{padding:85px 20px 32px}.lab-section{padding:32px 20px}.lab-grid{grid-template-columns:1fr}header{padding:0 20px;font-size:14px}h2{font-size:34px}}
@media(prefers-reduced-motion:no-preference){h1{animation:arrive .8s both}@keyframes arrive{from{opacity:0;filter:blur(8px);transform:translateY(8px)}to{opacity:1;filter:none;transform:none}}}
'''
lab_html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Robotics, Nena AI & lab projects — {esc(DATA['name'])}</title><meta name="description" content="Former lab chairperson and backend contributor. Nena AI, TanStack Tanzania, and shared lab work."><link rel="icon" href="/assets/personal/mark-il.svg"><style>{fonts}\n{lab_style}</style></head><body>
<header><a href="/">{esc(DATA['name'])}</a><nav><a href="/">Works</a><a href="/about">Story</a><a href="mailto:{esc(DATA['email'])}">Let's chat</a></nav></header>
<main><section class="lab-hero"><span class="eyebrow">{esc(lab['role'])}</span><h1>Software, speech, and shared curiosity.</h1><p>{esc(lab['description'])}</p><a class="lab-button" href="{esc(lab['url'])}" target="_blank" rel="noopener noreferrer">Visit the lab website ↗</a></section>
<section class="lab-section"><img class="lab-image" src="{esc(lab['cover'])}" alt="Public UDSM robotics lab website preview"><p class="eyebrow">Public lab website · My role: former chairperson and backend contributor</p></section>
<section class="lab-section lab-grid" id="nena-ai"><div><span class="eyebrow">AI · Lab team project</span><h2>Nena AI</h2><p>{esc(lab['nena']['description'])}</p><p>The project grew out of our lab's work on language technology and practical AI.</p></div><img src="{panel(nena,0)}" alt="Nena AI lab project artwork"></section>
<section class="lab-section lab-grid"><img src="/assets/personal/tanstack-live.png" alt="Public TanStack Tanzania website"><div><span class="eyebrow">Backend development</span><h2>TanStack Tanzania</h2><p>A platform connecting Tanzanian tech students with opportunities, resources, and career support. I contributed backend development as part of our lab project work.</p><a class="lab-button" href="/tanstack-tanzania">Explore the project ↗</a></div></section></main>
<footer><p>Open to freelance projects & collaborations</p><a href="mailto:{esc(DATA['email'])}">{esc(DATA['email'])}</a></footer></body></html>'''
(DIST/'robotics.html').write_text(lab_html,encoding='utf8')

# Redirect superseded project labels to the now-confirmed real project names.
aliases={p['legacy']:p['slug'] for p in DATA['projects']}
aliases.update({'rag-platform':'globoexpats','energyopt':'habitek','marketplace':'osher-market','infrastructure':'falco'})
for old,new in aliases.items():
    if old==new:continue
    (DIST/(old+'.html')).write_text(f'<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/{new}"><link rel="canonical" href="{ORIGIN}/{new}"><title>Project moved — {esc(DATA["name"])}</title></head><body><a href="/{new}">Open {esc(new.replace("-"," "))}</a></body></html>',encoding='utf8')

captures=[{'project':p['name'],'url':p.get('url'),'image':p.get('cover'),'contribution':p['role']} for p in DATA['projects']]
captures.append({'project':lab['name'],'url':lab['url'],'image':lab['cover'],'contribution':lab['role']})
(ROOT/'content/public-previews.json').write_text(json.dumps(captures,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('Personalized',len(pages),'captured pages and',len(DATA['projects']),'canonical case studies.')
print('Replaced',len(ASSETS),'asset references and',len(MAPPINGS),'content strings.')
