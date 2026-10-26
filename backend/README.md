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

Not yet connected: real analytics, custom analytics dashboard, OAuth/MCP tools and AI content automation. The old `design/blog/admin.html` is an illustrative prototype, not the real admin. Production never seeds sample posts or creates a shared default administrator.

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

## Backups

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
