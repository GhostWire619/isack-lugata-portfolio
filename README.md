# Isack Lugata — portfolio

A freelance-focused portfolio for Isack Lugata, a full-stack and mobile developer in Dar es Salaam, Tanzania. The presentation retains the reference site's typography, responsive layouts, tactile project cards, animated navigation, character reveals, and motion runtime.

## Run locally

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

Content generation requires Python 3 with Beautiful Soup 4 (`beautifulsoup4`). It reads the immutable reference capture from Git commit `d644207659b68a8a866714bf4216042a9229802a`, applies personal content to both static HTML and hydrated Framer modules, and generates technical sketches. Keep that commit in the repository's history.

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
