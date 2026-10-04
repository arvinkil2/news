# Kilambi News

Personal daily briefing site. Built with Hugo, deployed on Cloudflare Pages,
custom domain `news.kilambi.com`.

## Layout

- `content/briefings/<YYYY-MM-DD>-<beat>/index.md` — one file per beat per day.
  Beats: `commodities`, `infra-deals`, `politics`, `rates`.
- `content/stories/<slug>/index.md` — living stories. Newest update on top
  under "Latest"; older entries below, reverse chronological.
- `archetypes/briefing.md`, `archetypes/story.md` — the frontmatter contract.

## Frontmatter contract

```yaml
title: "Daily Commodities Briefing"  # "Daily <Beat> Briefing": Commodities / Infrastructure / Politics / Rates
date: 2026-10-04T07:00:00-04:00      # RFC3339 with numeric offset
last_updated: 2026-10-04T07:00:00-04:00
beats: ["commodities"]               # one of the four beats
status: "edition"                    # or developing / resolved for stories (not displayed)
lede: "..."                          # one sentence: the day's most important development + its consequence; shown on homepage and article page; never placeholder text
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
The first section is always `## The day in brief`. Section headings are never
numbered. No producer process notes in reader-facing copy.

## Morning pipeline (automated)

The daily briefing run writes each beat's report to
`content/briefings/<date>-<beat>/index.md` following this contract, validates
(frontmatter schema, no placeholder text, duplicate-slug check), commits, and
pushes. Cloudflare Pages rebuilds automatically.

The catalyst watcher appends timestamped updates to
`content/stories/<slug>/index.md` and regenerates the `lede` each time.

## Local build

```
hugo --gc --minify
```

Pin `HUGO_VERSION` in the Cloudflare Pages project to match the local build.
