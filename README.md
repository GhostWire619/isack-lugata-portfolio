# Daniel Sun portfolio replica

A faithful capture of https://danielsun.space/, retrieved on October 26, 2026. The original published HTML, styling, fonts, images, video, Lottie files, and Framer animation runtime are retained. Assets and runtime modules are served locally. The original analytics script and editor preload are removed.

## Run

Requires Node.js. No package installation is needed.

```sh
npm run dev
```

Open http://localhost:5173. Set `PORT` to use a different port.

## Contents

- `dist/index.html`: home page.
- `dist/about.html`: Story page.
- `dist/{clerk,dibsy,stimulate,caldera,reward-point,ruby,artem-astakhov}.html`: seven project pages.
- `dist/404.html` and `dist/test-1.html`: additional published pages.
- `dist/assets/`: original published assets and modules.
- `asset-manifest.json`: source URLs, local file names, and download sizes.
- `server.mjs`: static server with extensionless routes and video range requests.
- `scripts/mirror.py`: repeatable capture and URL rewriting workflow. Requires Python 3.

## Refresh

```sh
npm run refresh
```

This replaces the captured pages with the current public versions. The ignored `.mirror-cache/` stores downloaded originals; remove that folder before refreshing if you need to re-fetch all remote assets.

## Editing and scope

This is the deployed site's captured output, including its compiled Framer modules. It is not the original editable Framer canvas or an uncompiled component project. HTML and CSS can be edited directly; changes to hydrated components may also require changing their compiled modules.

The original names, contact addresses, project descriptions, social links, and external CV link are intentionally preserved to match the reference. External destination links continue to point to the original destinations.

## Verification

The home page, Story navigation, and Clerk project navigation were checked in the browser. Fonts, project imagery, motion runtime, and page transitions rendered without browser warnings or errors in those checks. All captured page routes and downloaded asset routes were checked over local HTTP. This does not assert an automated pixel comparison at every screen size.
