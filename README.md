# Kilambi News

Personal daily briefing site. Built with Hugo, deployed on Cloudflare Pages,
custom domain `news.kilambi.com`.

## Layout

- `content/stories/<YYYY-MM-DD>-<slug>.md` — **stories are the unit of
  the site.** One file per story (one development), not one file per beat.
  Beats: `commodities`, `infra-deals`, `politics`, `rates`.
- `content/archive/_index.md` — date-grouped story archive.
- `archetypes/story.md` — the frontmatter contract.

## Frontmatter contract

```yaml
title: "G7 backs 100-million-barrel coordinated reserve release"  # headline, 6-12 words, sentence case
date: 2026-10-04T07:00:00-04:00      # RFC3339 with numeric offset
last_updated: 2026-10-04T07:00:00-04:00
beats: ["commodities"]               # one of the four beats
status: "story"                      # or developing / resolved for catalyst stories (not displayed)
lede: "..."                          # one sentence: the dek — what happened, with the key number
why_it_matters: "..."                # one sentence: the consequence / why the reader should care
featured: true                       # top ~6-8 stories across beats appear in "What matters today"
evidence_grade: "A"                  # A / B / C (kept in frontmatter, not displayed)
sources:                             # structured source list
  - title: "..."
    publisher: "..."
    url: "https://..."
    published: "2026-10-04"
    archive_url: "https://web.archive.org/..."
tags: []
```

Body conventions: the first three lines are `**Data as of:**`, `**Issued:**`,
and the `**Evidence key:**` (CONFIRMED / REPORTED / RUMORED / ANALYTICAL).
Write in clean newsroom prose — plain headlines, natural paragraphs, structure
that varies with the story. No producer process notes in reader-facing copy.

## Homepage

`layouts/index.html` builds the homepage from the newest date's stories only:

1. "What matters today" — numbered, ranked: stories with `featured: true`
2. The four domain sections (Commodities, Infrastructure, Politics, Rates)
   with the remaining stories
3. "You're caught up." with an archive link

The nav shows a "Developing" link only when at least one story with
`status: "developing"` exists. Every story page shows the dek and a
"Why it matters" line under the headline.

## Morning pipeline (automated)

The daily briefing run researches each beat, then **splits the beat report
into individual stories** and writes them to
`content/stories/<date>-<slug>/index.md` following this contract. It flags
the day's ~6-8 most important stories `featured: true`, validates
(frontmatter schema, no placeholder text, duplicate-slug check), commits, and
pushes. Cloudflare Pages rebuilds automatically.

The catalyst watcher appends timestamped updates to the relevant existing
story in `content/stories/` (creating a new developing story only if none
fits) and regenerates the `lede` and `why_it_matters` each time.

## Local build

```
hugo --gc --minify
```

Pin `HUGO_VERSION` in the Cloudflare Pages project to match the local build.
