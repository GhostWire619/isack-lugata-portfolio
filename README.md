# Isack Lugata — portfolio

A freelance-focused portfolio for Isack Lugata, a backend and applied AI engineer in Dar es Salaam, Tanzania. The presentation retains the reference site's typography, responsive layouts, tactile project cards, animated navigation, character reveals, and motion runtime.

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

- `/`: home, selected projects, services, experiments, and contact.
- `/about`: personal story and experience.
- `/ecofy`: agricultural intelligence and applied AI.
- `/wakili-msomi`: bilingual legal-information assistant.
- `/rag-platform`: multi-tenant retrieval backend.
- `/energyopt`: energy-data analysis.
- `/marketplace`: marketplace and payment workflows.
- `/infrastructure`: deployment and operations.
- `/robotics`: lab leadership and technical exploration.

Old template routes remain usable as aliases with personalized content. `/test-1` serves the personalized homepage. `/404` retains the reference's error presentation with updated contact information.

## Editorial choices and remaining details

The primary goal is freelance clients and project enquiries, as confirmed by Isack. Both supplied briefs informed the content. Conflicting funding amounts, unverified user counts, pilot targets, phone numbers, and original-template client relationships are excluded.

The public GitHub account name matches Isack Lugata. Its public avatar appears on the Story page. New project visuals are labeled illustrative technical sketches, rather than product screenshots or evidence of production deployments. The client's logos are replaced with a technology marquee. Original showreel footage is hidden and replaced with technical sketches in the same motion containers. Long design galleries are curated to a smaller set of engineering diagrams.

Case studies contain visible `[CONFIRM]` notes for unresolved attribution, deployment status, and sharing permissions. Unknown dates remain marked for confirmation. Formal degree conferral is not asserted. The old CV download is replaced by an email request for a current engineering CV.

See `content/REVIEW.md` for remaining review items. Add reviewed project screenshots and an up-to-date résumé when available.

## Verification

Check the homepage, Story navigation, project cards, clean project routes, back navigation, contact links, and image loading after changing content. Because content appears in both HTML and hydrated modules, regenerate both with `npm run content`.

`scripts/mirror.py` is retained for provenance. `npm run capture:reference` captures the reference again and overwrites generated files; it is not the content-editing command.
