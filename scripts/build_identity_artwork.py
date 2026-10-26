"""Code-native covers and paper compositions using genuine images and licensed frames."""
from pathlib import Path
import base64
import html
import json
import re
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=DIST/'assets/identity'
DATA=json.loads((ROOT/'content/portfolio.json').read_text(encoding='utf8'))
URL='/assets/identity/'

def data_uri(file):
    p=Path(file)
    if not p.is_absolute():p=DIST/str(file).lstrip('/')
    mime={'.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'}.get(p.suffix,'application/octet-stream')
    return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()

def image(file,x,y,w,h,fit='xMidYMid meet',extra=''):
    return f'<image href="{data_uri(file)}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" {extra}/>'

def svg(body,w=1600,h=2000):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'

def write(name,body,w=1600,h=2000):
    (OUT/name).write_text(svg(body,w,h),encoding='utf8');return URL+name

def label(x,y,size,value,color='#111',family='Arial,Helvetica,sans-serif',anchor='start',weight='400'):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(value)}</text>'

def bounds(file):
    im=Image.open(OUT/file).convert('RGBA')
    alpha=im.getchannel('A')
    bbox=alpha.getbbox()
    if alpha.getextrema()==(255,255):
        rgb=im.convert('RGB');diff=ImageChops.difference(rgb,Image.new('RGB',im.size,'white'))
        bbox=diff.point(lambda v:255 if v>28 else 0).getbbox()
    return im.size,bbox or (0,0,*im.size)

def trim_logo(file,name):
    # The raster remains unchanged; the SVG viewport trims its empty canvas.
    (w,h),(l,t,r,b)=bounds(file)
    body=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{l} {t} {r-l} {b-t}" width="{r-l}" height="{b-t}">{image(URL+file,0,0,w,h)}</svg>'
    (OUT/name).write_text(body,encoding='utf8');return URL+name

LOGOS={
 'ecofy':trim_logo('ecofy-logo.png','brand-ecofy.svg'),
 'osher-market':trim_logo('osher-logo.png','brand-osher.svg'),
 'habitek':trim_logo('habitek-logo.png','brand-habitek.svg'),
 'falco':trim_logo('falco-logo.png','brand-falco.svg'),
 'wakili-msomi':trim_logo('wakili-mark.webp','brand-wakili.svg'),
 'tanstack-tanzania':URL+'tanstack-light.png',
}
globo=image(URL+'globo-icon.svg',0,0,90,90)+label(110,66,57,'Globo', '#151515',weight='700')+label(278,66,57,'expats','#d99500',weight='700')
LOGOS['globoexpats']=write('brand-globo.svg',globo,480,90)
wakili_mark=LOGOS['wakili-msomi']
LOGOS['wakili-msomi']=write('wordmark-wakili.svg',image(wakili_mark,0,0,95,95)+label(115,42,38,'Wakili',weight='600')+label(115,84,38,'Msomi',weight='600'),310,100)
habitek_mark=LOGOS['habitek']
LOGOS['habitek']=write('wordmark-habitek.svg',image(habitek_mark,0,0,100,100)+label(120,70,58,'Habitek','#263c3d',weight='600'),380,110)
ICONS={'ecofy':'ecofy-icon.png','globoexpats':'globo-icon.svg','osher-market':'osher-icon.png','habitek':'habitek-logo.png','falco':'falco-icon.png','wakili-msomi':'wakili-mark.webp','tanstack-tanzania':'tanstack-icon.svg'}
for slug,file in list(ICONS.items()):
    if file.endswith(('.png','.webp')):ICONS[slug]=trim_logo(file,'mark-'+slug+'.svg').rsplit('/',1)[-1]

DEFS='''<defs>
<filter id="shadow" x="-70%" y="-70%" width="240%" height="260%"><feDropShadow dx="12" dy="45" stdDeviation="35" flood-opacity=".38"/></filter>
<filter id="fine" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".065"/></feComponentTransfer><feBlend in="SourceGraphic" mode="multiply"/></filter>
<linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e5e7e5"/><stop offset=".48" stop-color="#b8bbb9"/><stop offset="1" stop-color="#f2f2ee"/></linearGradient>
<linearGradient id="blackcard" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#3b4243"/><stop offset=".48" stop-color="#151a1c"/><stop offset="1" stop-color="#05090b"/></linearGradient>
</defs>'''

def device(screen,x,y,w,rotate=0,kind='macbook',fit='xMidYMin slice'):
    if kind=='macbook':
        h=w*700/1208;sx=x+w*.118377483444;sy=y+h*.067142857143;sw=w*.764072847682;sh=h*.824285714286
        frame=URL+'macbook.png'
    else:
        h=w*2497/1766;sx=x+w*.064552661382;sy=y+h*.090909090909;sw=w*.869762174405;sh=h*.820184221065
        frame=URL+'ipad.png'
    return f'<g transform="rotate({rotate} {x+w/2} {y+h/2})" filter="url(#shadow)">'+image(frame,x,y,w,h)+image(screen,sx,sy,sw,sh,fit)+'</g>'

def cover(p,variant=0):
    slug=p['slug'];logo=LOGOS[slug];screen=p.get('cover')
    b=DEFS
    height=2000
    if slug=='ecofy':
        height=1400
        b+='<rect width="1600" height="2000" fill="url(#silver)"/><path d="M0 1560 1600 1250V2000H0Z" fill="#a7aaa6" opacity=".45"/>'
        b+=image(logo,570,65,460,180)
        b+=device(screen,-70,335,1740,-4 if variant==0 else 5)
        b+='<rect width="1600" height="2000" fill="transparent" filter="url(#fine)"/>'
    elif slug=='globoexpats':
        height=1400
        b+='<rect width="1600" height="2000" fill="#141a25"/><ellipse cx="1100" cy="400" rx="1000" ry="800" fill="#294574" opacity=".42"/>'
        b+=f'<g>{image(URL+"globo-icon.svg",690,60,220,220)}</g>'
        b+=device(screen,-90,340,1780,5 if variant==0 else -5)
        b+='<rect width="1600" height="2000" fill="transparent" filter="url(#fine)"/>'
    elif slug=='wakili-msomi':
        b+='<rect width="1600" height="2000" fill="#efe6cb"/><path d="M0 0h1600v140L0 1980Z" fill="#e1d1a9" opacity=".5"/>'
        b+=image(logo,135,180,380,380)
        b+=device(screen,450,420,1100,-11 if variant==0 else 9,'ipad','xMinYMid slice')
    elif slug=='habitek':
        b+='<rect width="1600" height="2000" fill="#b9c7bd"/><path d="M0 0 1600 0 1600 900 0 1550Z" fill="#e1e6db"/>'
        b+=image(logo,570,120,460,430)
        b+=device(screen,-210,730,2100,8 if variant==0 else -6)
        b+='<rect width="1600" height="2000" fill="transparent" filter="url(#fine)"/>'
    elif slug=='osher-market':
        b+='<rect width="1600" height="2000" fill="#08121e"/>'
        # A brand field with the same rich, full-bleed character as the reference.
        dots=[]
        import math
        for x in range(0,1600,22):
            for y in range(0,2000,22):
                wave=math.sin(x/330+y/350)*math.cos(y/420)
                radius=max(.6,3.2+2.5*wave)
                dots.append(f'<circle cx="{x}" cy="{y}" r="{radius:.2f}" fill="#3984ae" opacity="{.15+.25*(wave+1)/2:.2f}"/>')
        b+=''.join(dots)
        b+='<ellipse cx="850" cy="1000" rx="700" ry="370" fill="#07101b" opacity=".9"/>'
        b+=image(logo,260,780,1080,380)
    elif slug=='falco':
        height=1200
        b+='<rect width="1600" height="2000" fill="url(#silver)"/>'
        b+='<g transform="rotate(-8 800 500)" filter="url(#shadow)"><rect x="100" y="120" width="1370" height="680" rx="50" fill="#f5f3e9" stroke="#fff" stroke-width="5"/>'+image(logo,300,300,980,300)+'</g>'
        b+='<g transform="rotate(7 850 900)" filter="url(#shadow)"><rect x="350" y="710" width="1200" height="350" rx="30" fill="url(#blackcard)" stroke="#61686a" stroke-width="2"/>'+label(435,805,28,'FALCO FINANCIAL SERVICES','#ddd',weight='500')+label(435,910,61,'Management systems','#fff')+label(435,985,29,'Backend development','#c2c8c9')+'</g>'
    else:
        b+='<rect width="1600" height="2000" fill="#0d2927"/><ellipse cx="550" cy="400" rx="1000" ry="700" fill="#207967" opacity=".36"/>'
        b+=image(URL+'tanstack-logo.png',410,200,780,190)
        b+=device(screen,-90,650,1780,-8 if variant==0 else 5)
        b+='<rect width="1600" height="2000" fill="transparent" filter="url(#fine)"/>'
    return write(f'cover-{slug}'+('-detail' if variant else '')+'.svg',b,1600,height)

for p in DATA['projects']:
    p['logo']=LOGOS[p['slug']];p['icon']=URL+ICONS[p['slug']]
    p['artwork']=cover(p,0)
    p['detailAssets']=[cover(p,1),p.get('cover') or p['artwork'],p['artwork']]

nena=DEFS+'<rect width="1600" height="2000" fill="#e4eaf4"/><circle cx="750" cy="1000" r="670" fill="#f7f8fb"/>'+image(URL+'robot-3d.png',300,480,1000,1000)+label(800,330,150,'Nena AI','#1f355c',anchor='middle',weight='700')+label(800,1660,38,'Swahili, spoken naturally.','#354d74',anchor='middle')
write('cover-nena.svg',nena)

# Public icon paths come from maintained icon libraries, never text abbreviations.
for name in ['github','envelope','globe','briefcase']:
    source=(OUT/(name+'.svg')).read_text()
    for color,tag in [('#111111','light'),('#ffffff','dark')]:
        icon=re.sub(r'fill="(?:currentColor|black|#000000|#000)"',f'fill="{color}"',source)
        if 'fill=' not in icon.split('>')[0]:icon=icon.replace('<svg ',f'<svg fill="{color}" ')
        icon=icon.replace('currentColor',color)
        def pad(match):
            attrs=re.sub(r'\s(?:width|height)="[^"]*"','',match.group(1))
            return '<svg x="16" y="16" width="40" height="40"'+attrs+'>'
        icon=re.sub(r'<svg\b([^>]*)>',pad,icon,count=1)
        icon='<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72">'+icon+'</svg>'
        (OUT/f'icon-{name}-{tag}.svg').write_text(icon,encoding='utf8')

# Reuse the original hand-lettering font in the paper assets.
raw=(DIST/'index.html').read_text(encoding='utf8')
font_faces=[face for face in re.findall(r'@font-face\s*\{[^}]*\}',raw) if 'Caveat' in face]
latin_face=next((face for face in reversed(font_faces) if 'U+0000-00FF' in face),font_faces[-1] if font_faces else '')
font_match=re.search(r'url\([\x27\"]?([^\x27\")]+)',latin_face)
font_css=''
if font_match:
    path=font_match[1]
    if path.startswith('/assets/') and (DIST/path.lstrip('/')).exists():font_css='@font-face{font-family:Hand;font-weight:100 900;src:url('+data_uri(path)+')} '
FONT='<style>'+font_css+'text.hand{font-family:Hand,Caveat,cursive;font-weight:600}</style>'

def polaroid(name,photo,caption,angle=0):
    b=DEFS+FONT+f'<g transform="rotate({angle} 390 440)" filter="url(#shadow)"><rect x="55" y="45" width="670" height="760" rx="5" fill="#fbfbf9" stroke="#ddd" stroke-width="2"/>'
    b+=image(photo,90,80,600,560,'xMidYMid slice')
    lines=caption.split('|')
    for i,line in enumerate(lines):b+=f'<text class="hand" x="390" y="{705+i*46}" text-anchor="middle" font-size="39" fill="#151515">{html.escape(line)}</text>'
    return write(name,b+'</g>',780,860)

portrait='/assets/personal/portrait.png';lab=URL+'lab-photo.jpg'
photos=[
 polaroid('story-portrait.svg',portrait,'Curiosity got me here.',-3),
 polaroid('story-team.svg',lab,'A good team changes everything.',3),
 polaroid('story-ecofy.svg',URL+'lab-exhibition.jpg','Ideas deserve a real-world test.',-2),
 polaroid('story-lab.svg',URL+'lab-work.jpg','Life around the lab.',1),
 polaroid('story-products.svg','/assets/personal/tanstack-live.png','Built with people, for people.',-3),
]
ready_photo=polaroid('ready-portrait.svg',portrait,'Always up for|the next adventure.',-6)
note=DEFS+FONT+'<g transform="rotate(8 352 388)" filter="url(#shadow)"><path d="M90 75H630V650Q625 720 540 720H90Z" fill="#fff19a"/>'
for y in [215,315,415,515,615]:note+=f'<path d="M90 {y}H630" stroke="#8bcbb5" stroke-width="3" opacity=".75"/>'
note+='<path d="M560 75V705" stroke="#ee8c66" stroke-width="3"/>'
for y in [130,230,330,430,530,630]:note+=f'<circle cx="104" cy="{y}" r="14" fill="#171717"/>'
for i,line in enumerate(['✓ Web apps','✓ Mobile apps','✓ Backend','✓ Applied AI','✓ Real products']):note+=f'<text class="hand" x="148" y="{200+i*100}" font-size="52" fill="#191a14">{html.escape(line)}</text>'
note+='<path d="M90 650Q340 760 540 655L580 700Q400 790 90 720Z" fill="#f2d764"/>'
ready_note=write('ready-note.svg',note+'</g>',704,776)

# Company-grid art combines the genuine mark with a restrained wordmark when needed.
DATA['companies']=[
 {'name':'Ecofy Africa','logo':LOGOS['ecofy'],'url':'https://ecofy.co.tz/'},
 {'name':'GloboExpats','logo':LOGOS['globoexpats'],'url':'https://globoexpats.com/'},
 {'name':'Osher Market','logo':LOGOS['osher-market'],'url':'https://oshermarket.com/'},
 {'name':'Habitek','logo':LOGOS['habitek'],'url':'https://habitek.co.tz/'},
 {'name':'Falco Finance','logo':LOGOS['falco'],'url':'https://falco.co.tz/'},
 {'name':'Wakili Msomi','logo':LOGOS['wakili-msomi'],'url':'https://wakilimsomi.sheriakiganjani.co.tz/'},
 {'name':'TanStack Tanzania','logo':LOGOS['tanstack-tanzania'],'url':'https://tanstack.co.tz/'},
 {'name':'UDSM Robotics Lab','logo':write('brand-lab.svg',image(URL+'lab-icon.png',0,0,100,100)+label(120,40,31,'UDSM',weight='600')+label(120,78,28,'Robotics Lab'),390,105),'url':DATA['lab']['url']},
]
DATA['visuals']={'photos':photos,'readyPhoto':ready_photo,'readyNote':ready_note,'services':['original',URL+'phone-3d.png',URL+'gear-3d.png',URL+'robot-3d.png']}

# Glossy career badges retain the original scale while using real identities.
for i,icon in enumerate([URL+'mark-ecofy.svg',URL+'tanstack-icon.svg',URL+'briefcase.svg',URL+'lab-icon.png',URL+'udsm-logo.png']):
    b=DEFS+'<circle cx="100" cy="95" r="76" fill="url(#silver)" stroke="#fff" stroke-width="3"/><circle cx="100" cy="95" r="66" fill="#fafafa"/>'+image(icon,49,44,102,102)
    write(f'career-{i}.svg',b,200,190)

(ROOT/'content/portfolio.json').write_text(json.dumps(DATA,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('Built seven full-bleed covers, genuine company assets, five photo cards, and the adventure collage.')
