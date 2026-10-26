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

Not yet connected: real analytics, custom analytics dashboard, ChatGPT/Claude OAuth sign-in and AI content scheduling. The old `design/blog/admin.html` is an illustrative prototype, not the real admin. Production never seeds sample posts or creates a shared default administrator.

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

The original `compose.yaml` remains a portfolio-only deployment. Opt into the journal with the additive override:

```bash
git pull
python3 scripts/setup_blog_env.py
docker compose --env-file .env.blog -f compose.yaml -f compose.blog.yaml up -d --build
docker compose --env-file .env.blog -f compose.yaml -f compose.blog.yaml exec journal python manage.py createsuperuser
```

The setup script generates a unique database password and Django signing key in the ignored `.env.blog`. It never prints or overwrites existing secrets. Set `PUBLIC_URL` if using another domain. Use the exact same Compose file arguments for future updates, backups and shutdowns; using only the original compose file omits the journal services.

Nginx Proxy Manager remains `http://isack-portfolio:3100` on `ecofy-network`, with HTTPS configured for `isack.space` and forwarded protocol headers preserved. Restrict direct external access to port 3100 to your reverse proxy as appropriate for your host. The journal and its PostgreSQL database use a separate Docker network; neither exposes a host port. No Ecofy application or database configuration is modified.

The database migration/bootstrap runs before the application becomes healthy. The scheduler checks due revisions once per minute. Wagtail's scheduling UI uses `Africa/Nairobi`. HTML always reflects the live published revision; changing a draft does not replace its currently published revision.

The production image runs as a non-root user. The Nginx container reads the shared image volume; uploads are limited to image formats with a 15 MB application limit and a 16 MB gateway limit. Admin/security responses are not cached or indexed. Production uses secure session cookies and HTTPS redirects, so use the HTTPS domain for real logins.

## Password recovery and recovery codes

Configure `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS` and `DEFAULT_FROM_EMAIL` in `.env.blog`, then recreate the journal container to enable actual email delivery. Development uses console email. Without SMTP, a server owner can reset a password with `python manage.py changepassword USERNAME` inside the journal container. Password recovery does not bypass two-factor authentication.

Recovery codes are shown once, are consumed on use and should be stored in a password manager. Keep the production signing key stable so existing sessions and signed links remain valid across deployments.

## MCP: read articles and create drafts

`/mcp/` is an authenticated, stateless Streamable HTTP MCP endpoint. It supports `initialize`, `ping`, `tools/list`, `tools/call` and initialization notifications, with JSON responses and protocol versions 2025-03-26, 2025-06-18 and 2025-11-25. There are no server-initiated streams. The tools are `list_categories`, `list_articles`, `get_article` and, with write access, `create_article_draft` and `upload_image`. Draft creation never publishes or schedules an article. Publication remains a Studio action.

Connections use individual expiring bearer tokens, stored only as hashes in the database, tied to an active staff account and its current article permissions. Browser login cookies cannot authenticate MCP requests. Cross-origin browser requests are rejected. Keep the endpoint behind HTTPS in production. Tokens must be treated as passwords; do not commit them or paste them into public configuration.

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

`upload_image` accepts `title` and `image_base64`: JPEG, PNG or WebP up to 2 MiB and 40 megapixels. It checks image collection permissions, strips metadata, scales to at most 2560 pixels and stores compressed WebP. No server-side fetching of arbitrary URLs or local files is exposed. Repeated identical uploads on the same connection reuse the image. Article references also check image permissions. The gateway and Django permit the bounded 3 MB JSON request.

The client can upload local images through MCP with `--image-file cover=/private/cover.webp --image-file inline=/private/inline.webp`. Use `"cover_image_id":"@cover"` or `"image_id":"@inline"` in the article JSON; the client replaces these references with the returned image IDs before calling the draft tool.

Use `list_categories` for category slugs, or omit the category. Keep the same `request_key` and content when retrying; changing content with an existing key is rejected. Responses include a Studio editor link. Drafts remain excluded from public pages, feeds and sitemaps. The draft-request record links creation to its connection for traceability.

This is a token-authenticated connection, **not yet an OAuth connector for ChatGPT or Claude**. Their sign-in flow, discovery metadata, scheduling tools and analytics tools are still pending. The optional test client does not dynamically install a tool into either application.

## Appearance

The journal, article pages, login and Studio share paper/forest palettes and a light/dark appearance control. The choice persists in `localStorage` under `journal-theme`, synchronizes between tabs and defaults to the device setting. A tiny head script applies it before styles paint. Without JavaScript, content remains readable in light mode. Uploaded photographs retain their original colours; controls and backgrounds change together.

## Google AdSense

The authorized `ads.txt` record is in `content/ads.txt`, generated to `dist/ads.txt` for both Docker variants and served by Django during development. The portfolio homepage and journal include verification-only metadata for `ca-pub-4911606730643023`. Portfolio pages never load ad-serving scripts. `scripts/build_advertising.py` preserves the metadata and refreshes any precompressed homepage when content is rebuilt.

Three real Display ad units are preconfigured under **Studio → Your articles → Advertising settings** (the publication settings form):

| Unit | Slot | Placement |
| --- | --- | --- |
| Vertical | 1485658746 | 300 px desktop right rail, at viewport widths of 1200 px and above |
| Horizontal | 8873194178 | Between whole text blocks in articles of 450+ words; after the article for shorter pieces |
| Square | 6247030833 | Journal listing after two articles, only when there are at least three listed articles |

Articles of 1600+ words allow two horizontal breaks. At least 180 words precede and 150 words follow an in-article ad. Headlines, image/caption pairs, code and quote blocks are never split. Slots reserve their height, use asynchronous loading, and request once when near the viewport. Hidden desktop rails never request an ad on mobile; there is no refresh loop or sticky overlay. Full-width mobile expansion is disabled to protect the reading-column layout. Keep **Auto ads OFF** in AdSense so Google does not introduce additional placements.

Ad serving starts **off**. After site approval, publish Google's consent message for `isack.space` in AdSense **Privacy & messaging**; then check **Google consent message is published** and **Enable journal advertisements** in Studio. The form requires all three slot IDs and the consent confirmation. This flag records your account setup; it does not create a certified consent message. Google's CMP handles consent; the footer adds its preference-reopening control when the CMP API becomes available. `/blog/privacy/` explains essential storage and advertising. This page is included in the combined sitemap.

Ad requests never run in local development, Studio, staff sessions, or draft previews. **Preview ad placements** in Your articles opens the real layout with clearly labelled boxes, through MFA-protected `/admin/advertising/preview/`; add `?layout=journal` for the listing. This preview never includes Google ad-serving code and cannot generate impressions or clicks. It works even while advertising is disabled.

Deploy with the existing additive Compose command after pulling updates. Site approval, the consent message and real ad fill must be checked in your AdSense account; a passing build does not confirm Google approval or that an ad will be returned.

## Backups and restoration

Back up both named volumes and the private `.env.blog`. A database-only backup does not include images. Store backups outside this server and test restoring them before relying on them. Example database dump:

```bash
docker compose --env-file .env.blog -f compose.yaml -f compose.blog.yaml exec -T journal-db pg_dump -U journal -d isack_journal > journal-backup.sql
```

For media, use your host's volume backup tooling or archive `/app/media` from the journal container. Do not use `docker compose down -v` on the production deployment: it removes the database and media volumes.

## Checks

```powershell
$env:JOURNAL_ENV='development'
backend/.venv/Scripts/python.exe backend/manage.py check
backend/.venv/Scripts/python.exe backend/manage.py test publishing --noinput
```

CI additionally verifies PostgreSQL behavior and builds/runs the complete production Docker deployment. Tests cover draft/privacy exclusion, publish/unpublish visibility, scheduled posts, search escaping, pagination, image renditions, mandatory two-factor setup, one-use recovery codes and CSRF protection.
