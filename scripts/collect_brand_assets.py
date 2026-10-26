"""Download genuine public brand assets and licensed device/icon artwork."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/assets/identity'
OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
 'ecofy-logo.png':'https://ecofy.co.tz/ecoo%20full%20with%20text%20no%20boundaries%20logo.png',
 'ecofy-icon.png':'https://ecofy.co.tz/ecofy%20icon.png',
 'globo-icon.svg':'https://globoexpats.com/icon.svg',
 'osher-logo.png':'https://oshermarket.com/assets/Osher%20logo%20blue-D9zsdejb.png',
 'osher-icon.png':'https://oshermarket.com/assets/circle%20no%20bgg-C35oROpd.png',
 'habitek-logo.png':'https://habitek.co.tz/brand/habitek-logo-cropped.png',
 'falco-logo.png':'https://falco.co.tz/wp-content/uploads/2025/08/FALCO-MASTER-LOGO-TRANSPARENT.png',
 'falco-icon.png':'https://falco.co.tz/wp-content/uploads/2025/08/cropped-FALCO-MASTER-LOGO-1o-192x192.png',
 'wakili-logo.png':'https://wakilimsomi.sheriakiganjani.co.tz/wakili%20msomi%201.png',
 'wakili-mark.webp':'https://wakilimsomi.sheriakiganjani.co.tz/_next/image?url=%2Fwakili%20msomi%201.png&w=384&q=75',
 'tanstack-logo.png':'https://tanstack.co.tz/assets/TanStackDarkLogo-CC_HCX6O.png',
 'tanstack-light.png':'https://tanstack.co.tz/assets/TanstackLightLogo-I2zKZR5T.png',
 'tanstack-icon.svg':'https://tanstack.co.tz/tanstackfavicon.svg',
 'lab-photo.jpg':'https://robotics-preview.netlify.app/assets/hero%20image-DJ4B8XXn.jpg',
 'lab-icon.png':'https://robotics-preview.netlify.app/assets/yellow%20logo%20with%20no%20bg-CQg3VZhJ.png',
 'udsm-logo.png':'https://robotics-preview.netlify.app/assets/udsm%20logo-BwWYBQxf.png',
 'lab-exhibition.jpg':'https://robotics-preview.netlify.app/assets/exhibition-CJtfWhst.jpg',
 'lab-work.jpg':'https://robotics-preview.netlify.app/assets/who%20are%20we-D61Z_eDF.jpg',
 'phone-3d.png':'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Mobile%20phone/3D/mobile_phone_3d.png',
 'gear-3d.png':'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Gear/3D/gear_3d.png',
 'robot-3d.png':'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Robot/3D/robot_3d.png',
 'github.svg':'https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/github.svg',
 'envelope.svg':'https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/envelope.svg',
 'globe.svg':'https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/globe.svg',
 'briefcase.svg':'https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/briefcase.svg',
 'macbook.png':'https://raw.githubusercontent.com/pixelsign/html5-device-mockups/master/device-mockups/MacbookPro/portrait_black.png',
 'ipad.png':'https://raw.githubusercontent.com/pixelsign/html5-device-mockups/master/device-mockups/iPadAir2/portrait_black.png',
 'devices-license.txt':'https://raw.githubusercontent.com/pixelsign/html5-device-mockups/master/LICENSE.txt',
 'emoji-license.txt':'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE',
 'phosphor-license.txt':'https://raw.githubusercontent.com/phosphor-icons/core/main/LICENSE',
}
def download(item):
    name,url=item;file=OUT/name
    if file.exists():return {'name':name,'url':url,'bytes':file.stat().st_size}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=24) as r:data=r.read()
        file.write_bytes(data)
        return {'name':name,'url':url,'bytes':len(data)}
    except Exception as e:return {'name':name,'url':url,'error':str(e)}
if __name__=='__main__':
    results=list(ThreadPoolExecutor(10).map(download,SOURCES.items()))
    (ROOT/'content/asset-sources.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
    for result in results:print(json.dumps(result))
