---
name: write-journal-articles
description: Research, write, illustrate, edit and publish engaging Side notes journal articles through its MCP, with clickable sources, readable layouts, SEO metadata and AI-search discoverability.
---

# Write for Side notes

Side notes is Isack Lugata's independent journal at https://isack.space/blog/.
It covers multiple topics; it is not a personal diary or a portfolio sales funnel.
Follow the owner's topic, audience, tone and publication instructions. Do not insert
Tanzania, development or AI keywords into unrelated subjects. Never invent the
author's experiences, credentials, interviews or opinions.

## Start with the reader

Decide what makes this piece worth someone's time: a useful answer, an unexpected
finding, a practical demonstration, a compelling story or a defensible viewpoint.
Choose a specific angle rather than a broad, generic topic. Read related published
articles with `list_articles` / `get_article` to avoid repetition and find relevant
internal references. Check `list_categories`; use an existing topic or leave it
uncategorized rather than inventing an unavailable category slug.

Research current and checkable claims using available search/browsing tools and
primary sources. The journal MCP does not browse the web. If research tools are
unavailable, use sources the owner supplies, narrow the claims, or explain the
limitation. Separate observations, supported facts, uncertainty and opinion.
Use verified numbers with dates and context. Quotes must be exact, brief,
attributed and supported by a source; do not manufacture quotations.

## Hooks, voice and momentum

Write a concrete headline that promises the actual value of the article. Curiosity
can come from a real tension, surprising detail or useful question. Deliver the
payoff; avoid inflated promises, fake urgency and withholding the answer for clicks.

Open with a specific moment, counterintuitive fact, recognizable problem or sharp
question, then quickly explain why it matters. Give the reader an early answer or
clear direction. Skip throat-clearing, generic history and "in today's fast-paced
world" introductions. Do not repeat the title in the first paragraph.

Use precise verbs, concrete nouns and clear English. Vary sentence lengths and
paragraph rhythms. Explain specialist terms when they first matter. Prefer an
example or comparison to a string of adjectives. Let personality come from the
angle and observations, not forced slang, hype or generic AI phrasing.

Keep paragraphs comfortable on a phone, usually one to three sentences. Give each
section a job and remove passages that restate the same point. Use descriptive
headings at genuine changes of idea; don't subdivide every paragraph. Alternate
explanation with examples, an illustration, a useful quotation or a practical
takeaway when warranted. Do not force every article into the same template.

End with a useful consequence, actionable step or thought that follows from the
piece. A focused question can invite return visits or discussion. Avoid a recap
that repeats the whole article, engagement bait and invented newsletter features.

## Images and reading layout

Include at least one relevant image by default, normally a strong cover. Use more
images when they clarify a process, show evidence, compare outcomes or give a long
section a meaningful visual break. Place them near the passage they support.
Never add unrelated stock imagery just to meet a count or repeat the same image
throughout the article. Match portrait/landscape framing to the actual subject.

Use `list_images` to find suitable existing images the account may access; inspect
their returned URLs when the client supports viewing images. Otherwise
use permitted original, licensed or clearly disclosed AI-generated imagery, and
`upload_image` when the client can provide image bytes. Do not invent an image ID,
use a broken remote URL as an image ID, or claim an image was uploaded when it was
not. If no suitable image can be obtained, save a draft and report the missing asset
rather than claiming the requested illustrated article is ready to publish.

Images require accurate alt text. Captions explain what readers are seeing and
credit sources when needed; keep a clickable image credit in an adjacent paragraph
if the caption cannot contain a link. Do not present AI illustrations as documentary
photographs, screenshots or evidence. Uploads are compressed by the server.

This MCP supports paragraph, heading, quote, code, image, bullets and steps sections.
Use `{"type":"bullets","items":["First point","Second point"]}` for an unordered
list and `{"type":"steps","items":["First action","Next action"]}` for a numbered
sequence. Use lists when items genuinely benefit from scanning; do not turn the
whole article into a list. Arbitrary page HTML, CSS and Markdown tables are not
supported. Use an explanatory image plus text when a complex comparison needs it.
For limited emphasis, paragraph and list text accepts
`**bold**`, `*italic*` and `++underline++`; reserve them for meaningful phrases, not whole paragraphs. Named links are underlined automatically; use them to put a destination behind natural words, for example `[read the full report](https://example.org/report)`.
The site controls typography, responsive layout and spacing.

## Clickable references: use this exact format

Put references in paragraph sections as `[descriptive source label](https://full-url)`.
Bare HTTPS URLs also become clickable, but a descriptive label is usually easier
to read. Example: `The [original study](https://example.org/research) explains the method.`
Do not send raw `<a>` tags: raw HTML is escaped. Do not use ChatGPT/Claude citation
markers, tool reference IDs or footnotes with missing destinations; they will not
be meaningful website links. Use the real source URL, not a guessed address or a
search-result page. Check the destination with browsing tools when available.
Place citations beside the claim they support. Link only to genuinely relevant
existing articles internally, using `public_url` returned by `list_articles` /
`get_article`. A null public URL means the page is not publicly available; do not
link readers to its private Studio URL.
Quote attribution and image captions are plain text; put their source link in a
neighboring paragraph.

## Search and AI discovery

Choose a descriptive article `title`, a concise stand-alone `intro`, an optional
`seo_title` and an accurate `meta_description`. The latter two are dedicated MCP
fields, not text to paste into the body. Use the topic naturally, avoid stuffing,
and do not rely on arbitrary character targets as ranking rules. The slug is
generated at creation; keep published URLs stable. Updating only prose does not
require changing its URL.

For retrieval and citation, make the subject unambiguous, explain entities and
abbreviations, and give clear answers with supporting evidence. These are editorial
choices, not guaranteed ranking or citation tricks. Google describes AI-search
optimization as an extension of ordinary SEO; there is no special schema or
guaranteed GEO recipe. The site already supplies server-rendered article text,
canonical URLs, BlogPosting markup, dates, RSS and a sitemap. Ensure visible content,
authorship and claims agree; do not paste JSON-LD or hidden keywords into the body.

Consult current guidance when needed:
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content

## Save, review and publish

Use `create_article_draft` for a new piece or `update_article_draft` with complete
replacement content and the current `expected_revision_id` from `get_article`.
Every mutation needs a unique `request_key`; keep the same key and identical
arguments only when retrying that operation. Never overwrite a newer revision.

Call `review_article` after saving. Check the saved title and metadata, headings,
paragraph lengths, image descriptions and clickable source labels. Its checks are
structural, not fact-checking, link availability testing or a ranking score. Fix
warnings that matter to this article, then read it back with `get_article`.

Default to a private draft. If the owner explicitly requested publishing and the
connection exposes `publish_article`, publish the reviewed current revision; do
not ask for the same permission again. Publishing still requires the account's
native permissions. For an authorized schedule, use `schedule_article` with a
future ISO timestamp and timezone (Africa/Nairobi is UTC+03:00). If permissions or
assets are missing, leave a draft and state what is needed. Never describe a saved
draft or scheduled revision as already published.

Report the actual status, article URL if published, Studio edit URL and any material
limitations. `get_analytics` can inform later topic or readability improvements if
the connection permits it. Page views and reading progress are not unique people,
search rankings or proof of AI citations. Do not mass-publish filler to chase metrics.
