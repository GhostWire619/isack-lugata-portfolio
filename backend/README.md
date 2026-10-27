# Database-backed journal

Django 5.2 + Wagtail 8.0 serve the journal at `/blog/` and the publishing studio at `/admin/`. This is separate from the captured portfolio runtime. The public templates implement the independent journal design; Wagtail supplies the actual authenticated editorial interface, replacing the nonfunctional design editor.

## Implemented

- Database-backed articles, categories, configurable publication identity and real publication dates.
- Rich text, headings, quotes, code blocks, inline images and image galleries with descriptions and captions.
- Private drafts, native Wagtail revisions/previews, publishing/unpublishing and scheduled publishing.
- Responsive AVIF/WebP renditions generated from uploaded images. Original uploads are retained.
- Public search, topic filters, pagination, related articles, RSS and a combined portfolio/journal sitemap.
- Initial HTML includes article content, canonical/OG metadata and BlogPosting structured data.
- Password login, password strength checks, login throttling, authenticator-based two-factor setup and single-use recovery codes. All `/admin/` routes require a verified second factor after password login.
- Production PostgreSQL and persistent media volumes, separate scheduler and database health checks.
- Authenticated MCP tools to read articles and create private, editable drafts, with expiring/revocable connections and safe retries.

Studio includes real aggregate analytics, OAuth sign-in for compatible MCP clients, AI connection management, and permission-gated AI publishing/scheduling. The old `design/blog/admin.html` is an illustrative prototype, not the real admin. Production never seeds sample posts or creates a shared default administrator.

## Writing and publishing

Open `/admin/` and sign in. Studio opens directly to **Your articles**. Use **Write an article** to open an article editor with a text block already ready for typing. Add a title, short introduction and article content; images and a topic are optional.

The editor exposes **Preview**, **Save draft**, **Publish**, and **Schedule** as visible controls. Saving a draft keeps you in the editor. Publishing returns you to the article list with its live status. To publish later, choose Schedule, save the date/time, then choose Schedule to publish. Drafts and existing articles can be resumed from the list. The public journal links to Studio in its header and footer.

The old design preview on port 5174 links to the real Studio; its illustrative editor is not used to publish database content.

## Local development (Windows)

From the repository root, using Python 3.13:

```powershell
py -3.13 -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.lock
$env:JOURNAL_ENV='development'
$env:PUBLIC_URL='http://localhost:8001'
backend/.venv/Scripts/python.exe backend/manage.py migrate
backend/.venv/Scripts/python.exe backend/manage.py bootstrap_journal --demo
backend/.venv/Scripts/python.exe backend/manage.py createsuperuser
backend/.venv/Scripts/python.exe backend/manage.py runserver 127.0.0.1:8001
```

The local database is SQLite in `backend/data/`, for a quick isolated preview. Production requires PostgreSQL; CI runs the publishing/authentication tests against PostgreSQL. Local sample articles are explicitly marked development content and cannot be seeded in production. SQLite, the development signing key and uploaded files are ignored by Git. For a separate development publishing scheduler, run `python manage.py run_scheduler` in another process with the same environment.

Log in at `/admin/`, scan the QR code with an authenticator, verify the code and save the recovery codes. The account's first password session cannot access the CMS until two-factor setup is complete. There is no public account registration. Only an administrator can add users.

## Deploy on the existing server

One `compose.yaml` starts the entire site: portfolio gateway, journal, PostgreSQL and scheduler. No extra Compose files or flags are needed:

Both journal services declare the same local Docker build. Compose gives them local project image tags, so a fresh server never tries to fetch a private `isack-journal` repository. Container names, the published gateway port and persistent volumes keep their existing identities.

```bash
git pull
python3 scripts/setup_blog_env.py
docker compose up -d --build --wait
docker compose exec journal python manage.py createsuperuser
```

The setup script creates the ignored `.env` with a unique database password and Django signing key. When upgrading from `.env.blog`, it copies the existing settings byte-for-byte and keeps the legacy file. Existing `.env` files are validated and preserved; no secrets are printed or rotated. Set `PUBLIC_URL` if using another domain. Future updates use `docker compose up -d --build`, and logs/status use `docker compose logs` / `docker compose ps`. Keep the same checkout directory/project name to reuse the existing named volumes.

Nginx Proxy Manager remains `http://isack-portfolio:3100` on `ecofy-network`, with HTTPS configured for `isack.space` and forwarded protocol headers preserved. Restrict direct external access to port 3100 to your reverse proxy as appropriate for your host. The journal and its PostgreSQL database use a separate Docker network; neither exposes a host port. No Ecofy application or database configuration is modified.

The database migration/bootstrap runs before the application becomes healthy. The scheduler checks due revisions once per minute. Wagtail's scheduling UI uses `Africa/Nairobi`. HTML always reflects the live published revision; changing a draft does not replace its currently published revision.

The production image runs as a non-root user. The Nginx container reads the shared image volume; uploads are limited to image formats with a 15 MB application limit and a 16 MB gateway limit. Admin/security responses are not cached or indexed. Production uses secure session cookies and HTTPS redirects, so use the HTTPS domain for real logins.

## Password recovery and recovery codes

Configure `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS` and `DEFAULT_FROM_EMAIL` in `.env`, then recreate the journal container to enable actual email delivery. Development uses console email. Without SMTP, a server owner can reset a password with `python manage.py changepassword USERNAME` inside the journal container. Password recovery does not bypass two-factor authentication.

Recovery codes are shown once, are consumed on use and should be stored in a password manager. Keep the production signing key stable so existing sessions and signed links remain valid across deployments.

## AI connections and MCP

`/mcp/` is an authenticated, stateless Streamable HTTP MCP endpoint. It supports `initialize`, `ping`, `tools/list`, `tools/call` and initialization notifications, with JSON responses and protocol versions 2025-03-26, 2025-06-18 and 2025-11-25. There are no server-initiated streams. The read tools are `list_categories`, `list_articles`, and `get_article`. Write permission adds `create_article_draft`, `update_article_draft`, and `upload_image`. Explicit publishing permission adds `publish_article` and `schedule_article`; analytics permission adds `get_analytics` when the user also has `publishing.view_pageview`. Draft tools never publish. Publishing tools also check native Wagtail publishing permission. Updates, publishing and scheduling require the current `revision_id` as `expected_revision_id` to prevent overwriting newer work, plus a retry-safe `request_key`.

Connections use individual expiring bearer tokens, stored only as hashes in the database, tied to an active staff account and its current article permissions. Browser login cookies cannot authenticate MCP requests. MCP browser origins are restricted to the site, ChatGPT and Claude; protocol discovery/token endpoints permit credential-free CORS. Keep the endpoint behind HTTPS in production. Tokens must be treated as passwords; do not commit them or paste them into public configuration.

Create a connection from the server, choosing an existing Studio username and a private, persistent output location (the container's `/app/data/` is ephemeral unless you mount it):

```sh
python manage.py journal_mcp_token --username isack --name "My AI client" --write --hours 24 --output /tmp/journal-mcp-token.json
```

Omit `--write` for a read-only connection. The command prints the connection ID, never the token. Transfer the private output file securely if running a client elsewhere. Revoke access with `python manage.py journal_mcp_token --revoke CONNECTION_ID`; deleting a local credential file does not revoke the connection. A token lasts at most 30 days.

To verify with the official Python MCP SDK, install `scripts/requirements-mcp.txt` in a separate client environment and run from the repository root:

```sh
python scripts/journal_mcp_client.py --url https://isack.space/mcp/ --token-file /private/journal-mcp-token.json
```

Add `--article-file /private/article.json` to create and read back a draft. The client verifies an identical retry returns the same article. The file format is:

```json
{
  "request_key": "my-unique-article-request",
  "title": "An article headline",
  "intro": "A short introduction, up to 350 characters.",
  "category_slug": "technology",
  "sections": [
    {"type": "heading", "text": "A section heading"},
    {"type": "paragraph", "text": "Plain text is safely escaped."}
  ]
}
```

Sections support `heading`, `paragraph`, `code`, `quote` and `image`. A quotation uses `{"type":"quote","text":"Original or verified quotation","attribution":"Source or attribution"}`. An image uses `{"type":"image","image_id":123,"alt":"Accessible description","caption":"Optional caption"}`. Covers use the top-level fields `cover_image_id`, `cover_alt` and `cover_caption`.

Paragraph text supports clickable URLs and labelled references such as `[Read the source](https://example.com/report)`. MCP saves these as native editable rich-text links while escaping raw HTML. Existing published paragraphs with plain URLs or labelled references also gain clickable links when rendered, without changing their revisions. Existing anchors and code blocks are preserved. In the Studio editor, select text and use the link control to add or edit a link.

`upload_image` accepts `title` and `image_base64`: JPEG, PNG or WebP up to 2 MiB and 40 megapixels. It checks image collection permissions, strips metadata, scales to at most 2560 pixels and stores compressed WebP. No server-side fetching of arbitrary URLs or local files is exposed. Repeated identical uploads on the same connection reuse the image. Article references also check image permissions. The gateway and Django permit the bounded 3 MB JSON request.

The client can upload local images through MCP with `--image-file cover=/private/cover.webp --image-file inline=/private/inline.webp`. Use `"cover_image_id":"@cover"` or `"image_id":"@inline"` in the article JSON; the client replaces these references with the returned image IDs before calling the draft tool.

Use `list_categories` for category slugs, or omit the category. Keep the same `request_key` and content when retrying; changing content with an existing key is rejected. Responses include a Studio editor link. Drafts remain excluded from public pages, feeds and sitemaps. The draft-request record links creation to its connection for traceability.

### Bundled article-writing skill

The MCP advertises a portable `write-journal-articles` skill in initialization instructions, the read-only `get_writing_guide` tool, a Markdown resource and the `write_article` prompt. The same file is downloadable as Markdown at `/blog/ai-writing-skill.md` and as an authenticated ZIP through **Studio → AI connections**. Client support for resources/prompts varies, so the guide tool is the primary entry point; connecting does not silently install a skill into an AI account.

The guide covers hooks, clear wording, phone-readable paragraphs, selective emphasis, meaningful images, clickable source labels, SEO and AI discoverability. It calls for at least one relevant image by default and leaving a draft when a suitable image cannot be obtained. `list_images` exposes permitted uploaded images and their real IDs/URLs. `review_article` reports saved links, images and alt text, long paragraphs and search metadata; it does not fetch external URLs, fact-check or invent a ranking score. These are model instructions and structural feedback, not an automatic guarantee of editorial quality or AI citations.

`create_article_draft` and `update_article_draft` accept optional `seo_title` and `meta_description`. Omitting them during updates preserves existing values. Paragraphs and list items support `**bold**`, `*italic*` and labelled links. `bullets` and `steps` sections accept an `items` array and save as native rich-text lists. Published, publicly accessible articles return `public_url`; drafts and private pages return null. Refresh the client's tool discovery after deploying changed tool definitions.

### OAuth connection

Open **Studio → AI connections** (`/admin/ai/`). Copy `https://isack.space/mcp` into a compatible AI app's custom MCP connection screen and choose OAuth. The app discovers the authorization, registration and token endpoints automatically. Sign in to Studio, complete MFA, and approve the requested permissions. Direct publishing is unchecked by default even when requested by the client. Availability of custom MCP connections depends on the client and account; deployment does not install the connection in ChatGPT or Claude for you.

**Connected applications** shows access, last use and expiry. **Disconnect** revokes the connection, pending grants and OAuth access/refresh tokens. Manual bearer tokens can also be generated here and are shown only once. OAuth uses Django OAuth Toolkit, authorization code with S256 PKCE, one-hour access tokens, rotated refresh tokens with reuse protection, a maximum 30-day connection, and resource-bound tokens accepted only at this MCP endpoint. Discovery is at `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource/mcp`. Registration allows HTTPS callback addresses (loopback HTTP only during development), limits size and rate, and exposes no password or implicit grant. Reconnecting requires a fresh approval.

### OAuth troubleshooting and logs

For Claude, Studio also provides **Set up Claude**. This creates an owner-specific public OAuth client without granting access. Remove any failed Claude connector and add a new one with the MCP URL, **Sign in now**, and **Use your own OAuth client**. Copy the Studio client ID and leave the client secret blank. The registered callback is exactly `https://claude.ai/api/mcp/auth_callback`; normal MFA, consent, S256 PKCE and scope restrictions still apply. The setup is repeatable and preserves the client ID across deployments. A public client ID is an identifier, not a bearer credential. This explicit registration route avoids depending on a cached automatic-registration ID or fetching Claude's published identity.

Authorization failures display the native OAuth error code, a redacted reason and a diagnostic ID. **Studio → AI connections → Recent connection errors** shows the same user's last ten failures, including whether the client was registered, its callback matched, the PKCE method and any published-identity fetch failure. Records expire after 14 days and are bounded per user. Anonymous failures remain in server logs rather than a public database view.

JSON log events `oauth.metadata_failed`, `oauth.request_failed` and `oauth.request_succeeded` include timestamps, stage and correlation IDs. Credentials, authorization codes, OAuth state and raw sign-in URLs are excluded. The bundled Nginx and Gunicorn access logs omit query strings; an external reverse proxy has its own logging configuration. Inspect recent backend diagnostics with:

```bash
docker compose logs --since=15m journal
```

The MCP returns a `401` bearer discovery challenge for unauthenticated GET and POST probes. An authenticated GET returns `405` because the endpoint uses stateless POST responses. Regression tests cover Claude's hosted callback `https://claude.ai/api/mcp/auth_callback`, automatic registration, S256 PKCE, form-encoded token exchange and MCP initialization. Published-identity fetches retain HTTPS, public-IP pinning and certificate validation; a blocked metadata fetch is reported rather than bypassed. See [Claude's authentication requirements](https://claude.com/docs/connectors/building/authentication).

### Real site and article analytics

Microsoft Clarity project `z485ii73vk` and Google Analytics stream `G-XWWT4YVE88` also run asynchronously on production public portfolio and journal pages. The shared loader skips local/preview hosts, Studio/security/OAuth/MCP paths, Do Not Track and Global Privacy Control. Journal templates additionally exclude signed-in readers and article/ad previews. Advertising storage remains denied; analytics storage starts denied and can be explicitly allowed or withdrawn on `/blog/privacy/`. The script queues Clarity Consent V2 and Google Consent Mode defaults before loading either tracker. Clarity dashboards and session replays are viewed in Microsoft Clarity; GA4 traffic reports are viewed in Google Analytics. Both are separate from Studio's first-party aggregate reports. GA4 uses its standard automatic page-view measurement; keep Enhanced Measurement page views enabled to capture portfolio browser-history navigation without adding duplicate manual events. `node scripts/check_clarity.mjs` checks loading and consent without contacting Microsoft. `scripts/build_analytics.py` installs the same loader in the exported portfolio and regenerates compressed HTML.

**Studio → Analytics** (`/admin/analytics/`) shows real page views, active time, reading progress, top pages, referring domains and daily totals for 7, 30 or 90 days. The same aggregate data is available through `get_analytics` with optional article filtering. These are page-view counts, not unique people. The collector never stores IP addresses, analytics cookies or persistent visitor IDs, strips referrer query strings, and respects Do Not Track and Global Privacy Control. It is disabled on localhost and public draft previews. Raw events are pruned after 90 days by the existing scheduler. Google AdSense reports remain separate.

The first-party collector is included in public journal HTML and exported portfolio pages, including route changes. `python scripts/build_analytics.py` refreshes portfolio exports; it is also part of the normal content build. `/events/` accepts only bounded same-origin public-page events. The first report will be empty until real visits arrive after deployment.

## Appearance

The journal, article pages, login and Studio share paper/forest palettes and a light/dark appearance control. The choice persists in `localStorage` under `journal-theme`, synchronizes between tabs and defaults to the device setting. A tiny head script applies it before styles paint. Without JavaScript, content remains readable in light mode. Uploaded photographs retain their original colours; controls and backgrounds change together.

Dark mode uses a pure black page with muted text rather than a green-tinted background. Articles use locally hosted Source Serif 4 normal/italic fonts (SIL Open Font License in the assets folder), a restrained reading measure, shared left alignment for title/intro/image/body, and a responsive opening drop cap. Body size is 20px desktop and 18px mobile. The reading stylesheet and 54 KB normal font preload are article-only. Underline is available in the native editor as well as the MCP's `++underline++` syntax; named links are underlined automatically.

## Google AdSense

The authorized `ads.txt` record is in `content/ads.txt`, generated to `dist/ads.txt` for both Docker variants and served by Django during development. The portfolio homepage and journal include verification-only metadata for `ca-pub-4911606730643023`. Portfolio pages never load ad-serving scripts. `scripts/build_advertising.py` preserves the metadata and refreshes any precompressed homepage when content is rebuilt.

Three real Display ad units are preconfigured under **Studio → Your articles → Advertising settings** (the publication settings form):

| Unit | Slot | Placement |
| --- | --- | --- |
| Vertical | 1485658746 | 300 px desktop right rail, at viewport widths of 1200 px and above |
| Horizontal | 8873194178 | Between whole text blocks in articles of 450+ words; after the article for shorter pieces |
| Square | 6247030833 | Journal listing after two articles, only when there are at least three listed articles |

Articles of 1600+ words allow two horizontal breaks. At least 180 words precede and 150 words follow an in-article ad. Headlines, image/caption pairs, code and quote blocks are never split. Slots reserve their height, use asynchronous loading, and request once when near the viewport. Hidden desktop rails never request an ad on mobile; there is no refresh loop or sticky overlay. Full-width mobile expansion is disabled to protect the reading-column layout. Keep **Auto ads OFF** in AdSense so Google does not introduce additional placements.

Ad serving starts **off**. After site approval, publish Google's consent message for `isack.space` in AdSense **Privacy & messaging**; then check **Google consent message is published** and **Enable journal advertisements** in Studio. The form requires all three slot IDs and the consent confirmation. This flag records your account setup; it does not create a certified consent message. Google's CMP handles consent; the footer adds its preference-reopening control when the CMP API becomes available. `/blog/privacy/` explains essential storage and advertising. The conditions page is `/blog/terms/`. Both pages are included in the combined sitemap and linked in the footer. After deployment, use `https://isack.space/blog/privacy/` and `https://isack.space/blog/terms/` for Google’s privacy/conditions URL fields.

Ad requests never run in local development, Studio, staff sessions, or draft previews. **Preview ad placements** in Your articles opens the real layout with clearly labelled boxes, through MFA-protected `/admin/advertising/preview/`; add `?layout=journal` for the listing. This preview never includes Google ad-serving code and cannot generate impressions or clicks. It works even while advertising is disabled.

Deploy with `docker compose up -d --build` after pulling updates. Site approval, the consent message and real ad fill must be checked in your AdSense account; a passing build does not confirm Google approval or that an ad will be returned.

## Backups and restoration

Back up both named volumes and the private `.env`. A database-only backup does not include images. Store backups outside this server and test restoring them before relying on them. Example database dump:

```bash
docker compose exec -T journal-db pg_dump -U journal -d isack_journal > journal-backup.sql
```

For media, use your host's volume backup tooling or archive `/app/media` from the journal container. Do not use `docker compose down -v` on the production deployment: it removes the database and media volumes.

## Checks

```powershell
$env:JOURNAL_ENV='development'
backend/.venv/Scripts/python.exe backend/manage.py check
backend/.venv/Scripts/python.exe backend/manage.py test publishing --noinput
```

CI additionally verifies PostgreSQL behavior and builds/runs the complete production Docker deployment. Tests cover draft/privacy exclusion, publish/unpublish visibility, scheduled posts, search escaping, pagination, image renditions, mandatory two-factor setup, one-use recovery codes and CSRF protection.


### Import article photos through MCP

`import_image` accepts `title`, `image_url` (direct HTTPS JPEG/PNG/WebP),
`source_url` (the source/license page), `credit`, and `license` (verified reuse basis).
It downloads up to 10 MB on the server, validates up to 40 megapixels, resizes to
2560 pixels and stores WebP. It returns the image ID, URL and saved provenance;
`list_images` also returns provenance. Include credits in the article caption and
link the source in an adjacent paragraph. Licensing is supplied by the caller,
not automatically verified. The tool cannot search for images.

Imports require write scope and native image/page permissions. Every redirect is
checked against public DNS and pinned to the resolved IP with hostname-verified
TLS. Private/local addresses, non-HTTPS URLs, unexpected content, oversized files
and slow responses are rejected. No browser cookies or OAuth headers are forwarded.
Base64 upload remains available for clients that encode files programmatically.
After deploying, refresh/reconnect the AI connector to discover `import_image`
and the updated writing guide. Existing images need no backfill; the migration
adds optional provenance. Docker service names and port 3100 are unchanged.
