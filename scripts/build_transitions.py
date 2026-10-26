"""Set the real canvas colour before first paint and restore nav handoffs."""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
boot = (ROOT / 'scripts/navigation-boot.js').read_text(encoding='utf8')
for path in DIST.glob('*.html'):
    soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
    dark = path.stem == 'about'
    color = '#000000' if dark else '#ffffff'
    soup.html['data-portfolio-theme'] = 'dark' if dark else 'light'
    for tag in soup.select('#portfolio-canvas,#portfolio-navigation-boot,#portfolio-render-ready,meta[name="theme-color"]'):
        tag.decompose()
    style = soup.new_tag('style', id='portfolio-canvas')
    style.string = ':root{background:' + color + ';color-scheme:' + ('dark' if dark else 'light') + '}body{background:' + color + '!important}'
    script = soup.new_tag('script', id='portfolio-navigation-boot')
    script.string = boot
    charset = soup.head.find('meta', charset=True)
    position = list(soup.head.children).index(charset) + 1 if charset else 0
    soup.head.insert(position, style)
    soup.head.insert(position + 1, script)
    soup.head.insert(position + 2, soup.new_tag('meta', attrs={'name':'theme-color', 'content':color}))
    soup.body.append(soup.new_tag('span', id='portfolio-render-ready', hidden=''))
    path.write_text(str(soup), encoding='utf8')
print('Prepared light/dark canvas colours and pre-paint navigation handoffs.')
