# Isack Lugata — portfolio

A freelance-focused portfolio for Isack Lugata, a full-stack and mobile developer in Dar es Salaam, Tanzania. The presentation retains the reference site's typography, responsive layouts, tactile project cards, animated navigation, character reveals, and motion runtime.

## Run on your server with Docker

Requires Docker Engine and the Docker Compose plugin. The finished site and its assets are already included; no Node.js, Python, or content generation is needed on the server. The portfolio joins the existing external **`ecofy-network`**, matching Ecofy backend's Docker Compose configuration. Start Ecofy first so that network exists.

```sh
git clone https://github.com/GhostWire619/isack-lugata-portfolio.git
cd isack-lugata-portfolio
docker compose up -d --build
```

Open `http://YOUR_SERVER_IP:3100`. The host and container both use port **3100**. If the server has a firewall, allow inbound TCP port 3100. For a domain with HTTPS, point your existing reverse proxy to this port.

```sh
# Check status and logs
docker compose ps
docker compose logs --tail=100

# Pull updates and rebuild
git pull --ff-only
docker compose up -d --build

# Stop the site
docker compose down
```

The repository is public. Nginx serves clean page URLs, fonts, JavaScript modules, and media directly. Container health is checked at `/healthz`. GitHub Actions checks the SEO files, builds the image, and verifies the live container on port 3100 and on the shared Docker network after each push.

### Nginx Proxy Manager

Container name: **`isack-portfolio`**. Compose service name: `portfolio`. Network name: **`ecofy-network`**.

With Nginx Proxy Manager attached to `ecofy-network`, create a Proxy Host with:

- Domain: `isack.space`
- Scheme: `http`
- Forward hostname: `isack-portfolio`
- Forward port: `3100`
- SSL: request a certificate for `isack.space`, then enable Force SSL.

To connect an existing proxy container, use `docker network connect ecofy-network YOUR_NPM_CONTAINER`. Also declare that external network in Nginx Proxy Manager's own Compose file so it survives a recreation. The portfolio configuration does not change Ecofy's services or the proxy manager's settings.

If the domain returns 502, check `docker compose ps`, `docker compose logs --tail=100`, and that the proxy container and portfolio both appear in `docker network inspect ecofy-network`. The proxy can use the server IP and published port 3100 instead if they do not share a Docker network.

Without Compose:

```sh
docker build -t isack-portfolio .
docker run -d --name isack-portfolio --network ecofy-network --restart unless-stopped -p 3100:3100 isack-portfolio
```

## Run locally without Docker

Requires Node.js; no npm packages are needed to serve the site.

```sh
npm run dev
```

Open http://localhost:5173. Set `PORT` to change the port.

## Search visibility for isack.space

`content/portfolio.json` declares `siteUrl: "https://isack.space"`. The content build generates unique page titles/descriptions, canonical links, social previews, Person/WebSite/ProfilePage/Service/case-study structured data, `robots.txt`, and a sitemap containing the ten main pages. Both the initial HTML and Framer's client metadata use the production domain. Auxiliary captures are excluded from indexing. Run `python scripts/check_seo.py` after changes.

After pulling and rebuilding on the server:

1. Confirm `https://isack.space/`, `/about`, `/robots.txt`, and `/sitemap.xml` return HTTP 200 without login. A 502 blocks discovery.
2. Verify the `isack.space` domain property in Google Search Console using its DNS TXT record. Submit `https://isack.space/sitemap.xml`, then inspect the homepage and request indexing.
3. Link the website from your GitHub, LinkedIn, and Instagram profiles. Ask project partners for genuine contributor links where appropriate.
4. Add specific, accurate project lessons and outcomes as you have evidence to share. The portfolio targets software, frontend/mobile/backend development, and applied AI in Tanzania, without inventing design credentials or rankings.

Search Console verification requires the domain owner's DNS access; the repository alone does not submit or verify the site. Search rankings, indexing, and AI citations are not guaranteed. No special AI text file is required for Google Search's AI features.

## Edit the content

The editable content is in `content/portfolio.json`. It contains the identity, introduction, services, seven project summaries, case-study narratives, technical stacks, and review notes. After editing it, run:

```sh
npm run content
```

Content generation requires Python 3 with Beautiful Soup 4 (`beautifulsoup4`) and Pillow (`Pillow`, used to inspect existing image bounds). It reads the immutable reference capture from Git commit `d644207659b68a8a866714bf4216042a9229802a`, applies personal content to both static HTML and hydrated Framer modules, and generates technical sketches. Keep that commit in the repository's history.

The original files are compiled Framer output, rather than an editable Framer canvas. The content layer makes the personalized material easier to maintain without replacing the layout and motion system.

## Pages

- `/`: freelance services and selected work.
- `/about`: background, experience, and former robotics chairperson role.
- `/ecofy`: frontend, backend, and applied AI.
- `/globoexpats`: mainly frontend work.
- `/wakili-msomi`: frontend and backend.
- `/habitek`: frontend and backend.
- `/osher-market`: backend work.
- `/falco`: internal management backend, distinct from the public company site.
- `/tanstack-tanzania`: backend development.
- `/robotics`: former lab leadership, backend contribution, and Nena AI team work.

Old project routes redirect to the current project names. The public project URLs, screenshot locations, and confirmed contribution scopes are recorded in `content/public-previews.json`.

## Editorial choices

The primary audience remains freelance clients. Isack confirmed frontend and backend work at Ecofy, Wakili Msomi, and Habitek; mainly frontend at GloboExpats; backend at Osher, TanStack, robotics, and Falco's internal management system.

Real public website captures replace the original generic covers. Public screenshots show product context; they do not imply frontend ownership on backend-only projects. Falco uses a conceptual backend diagram because the contribution was to an internal management system. No private dashboards or records are exposed.

Mobile applications are included in the service offering without inventing a specific framework, app-store release, or mobile contribution to any listed project. Nena AI is attributed as a shared lab project. The lab page follows Isack's correction that he is the former chairperson, even if the public lab website still shows an older label.

Formal degree conferral, unsupported project metrics, funding amounts, phone numbers, and exact unknown historical role dates are not invented. The old CV download remains replaced with an email request for a current résumé.

See `content/REVIEW.md` for source notes and remaining editorial details.

## Verification

Check the homepage, Story navigation, project cards, clean project routes, back navigation, contact links, and image loading after changing content. Because content appears in both HTML and hydrated modules, regenerate both with `npm run content`.

`scripts/mirror.py` is retained for provenance. `npm run capture:reference` captures the reference again and overwrites generated files; it is not the content-editing command.

## Visual assets

The original reference section structure and headings are retained, including How I got here, Where I stand, Ready for the next adventures, Companies I helped, and More projects coming soon.

`npm run content` regenerates code-native device mockups and paper compositions before applying the content. Real project screenshots, genuine company marks, the public GitHub portrait, and public lab photographs supply the imagery. The screenshots are composed inside licensed device frames; they are not generated product interfaces.

Social icons use genuine Simple Icons and Phosphor SVG artwork with consistent optical padding. Service icons combine the original globe/cursor artwork with Microsoft Fluent 3D assets. Licensing files are deployed alongside assets under `dist/assets/identity/`, and public asset source URLs are recorded in `content/asset-sources.json`.

Photo compositions retain real people and real photographs. Captions do not invent a family, pets, or personal events. The career timeline uses actual brand/university marks and a generic briefcase for practical training.
