# Side notes: interactive blog design

This is a local design prototype, kept separate from the deployed portfolio. “Side notes” is a proposed working title. Sample articles and analytics are illustrative, not claims about Isack's writing or traffic.

Run `node design/blog/preview.mjs`, then open `http://localhost:5174`.

## Screens

- `index.html`: independent journal homepage, topic filters and search.
- `article.html`: reading layout, responsive photography, contents links and sharing.
- `admin.html`: overview, searchable story list, analytics, local image previews, AI connection permission preview and local settings.
- `editor.html`: editable story, formatting, local draft persistence, image previews, search snippet and local publishing plan.

No authentication, database, analytics collection, remote MCP, image uploads or actual publishing is implemented here. Draft text and settings are saved only to browser localStorage. Images selected from the computer remain temporary object URLs and are not durable uploads. The local server binds to loopback; all responses are marked noindex. This prototype is not part of the production Docker image.

## Design decisions

Editorial public pages use native HTML/CSS with the existing self-hosted LT Superior Serif and Inter Display assets. These are reused from the existing portfolio capture; validate their production license before expanding font use. The design-taste-frontend skill applies only to the public editorial screens, not the custom admin prototype. Dials: DESIGN_VARIANCE 6, MOTION_INTENSITY 4, VISUAL_DENSITY 3. One green accent; light theme; 6px control radius. Content remains readable without animation. Native form controls and dialogs support keyboard interaction. Dashboard figures are always labeled illustrative.

The proposed backend remains Django + Wagtail, PostgreSQL, optimized image renditions and persistent media storage. Owner authentication, scheduled publishing, consent choices and authenticated MCP are implementation work after design review. The dashboard can consume analytics through the backend without exposing analytics credentials to the browser.

## Media

- Landscape: https://images.unsplash.com/photo-1470770841072-f978cf4d019e
- Coast: https://images.unsplash.com/photo-1500375592092-40eb2168fd21
- Robotics illustration and author portrait: existing portfolio assets; illustration source recorded in `content/asset-sources.json`.
- Icons: Phosphor regular SVGs, https://github.com/phosphor-icons/core (MIT license), fetched from its official repository. The matching license is included in `assets/PHOSPHOR-LICENSE`.

Photographs from Unsplash illustrate the layout and do not represent Isack's travels or photography. Replace sample text and illustrative photographs with author-approved content before launch.

Editorial direction: an independent, topic-led journal, not a personal diary or portfolio extension. Author attribution remains; autobiographical promotional copy does not.
