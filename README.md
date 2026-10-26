# Isack Lugata — portfolio

A freelance-focused portfolio for Isack Lugata, a full-stack and mobile developer in Dar es Salaam, Tanzania. The presentation retains the reference site's typography, responsive layouts, tactile project cards, animated navigation, character reveals, and motion runtime.

## Run on your server with Docker

Requires Docker Engine and the Docker Compose plugin. The finished site and its assets are already included; no Node.js, Python, or content generation is needed on the server.

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

The repository is private, so clone it using an authorised GitHub account or a server deploy key. Nginx serves clean page URLs, fonts, JavaScript modules, and media directly. Container health is checked at `/healthz`. GitHub Actions builds the image and verifies the live container on port 3100 after each push.

Without Compose:

```sh
docker build -t isack-portfolio .
docker run -d --name isack-portfolio --restart unless-stopped -p 3100:3100 isack-portfolio
```

## Run locally without Docker

Requires Node.js; no npm packages are needed to serve the site.

```sh
npm run dev
```

Open http://localhost:5173. Set `PORT` to change the port.

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
