# patientvibes-main

Source for **[patientvibes.io](https://patientvibes.io)** — Chris Moore's portfolio for AI agent development and "vibe coding" consulting.

A single Astro 6 page in the "Sage Editorial" design language: Instrument Serif + Inter + JetBrains Mono on a sage-and-paper palette, no Tailwind, all tokens. Project rows are bound at build time to the public catalog at [agents.patientvibes.io/api/projects.json](https://agents.patientvibes.io/api/projects.json) — push a README to one of the `agent-*` sibling repos and it propagates here next build.

## Local dev

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # writes dist/
npm run preview  # serves dist/
npm run lint     # stylelint over src/**/*.css
```

`npm run build` runs `prebuild` first — fetches `https://agents.patientvibes.io/api/projects.json` into `.cache/projects.json`, falls back to `__fixtures__/projects.json` if the sibling site is unreachable. Node ≥22.12.

## Layout

```
src/
├── layouts/BaseLayout.astro    # head, fonts preload, favicon, RSS link
├── pages/
│   ├── index.astro             # the homepage
│   └── index.xml.ts            # RSS endpoint via @astrojs/rss
├── components/                 # ProjectRow, NoteRow, BenchPanel, Terminal
├── content/notes/              # markdown notes (Zod-validated frontmatter)
├── styles/                     # tokens.css · base.css · components.css · fonts.css
└── lib/load-projects.ts        # reads .cache/projects.json
public/
├── brand/                      # favicons
└── fonts/                      # 7 self-hosted woff2 (latin subset)
scripts/fetch-projects.mjs      # the prebuild fetcher
__fixtures__/projects.json      # offline fallback for builds
archive/                        # old gradient index + mockups, kept for reference
```

## Design tokens are the schema

All colors live in [`src/styles/tokens.css`](src/styles/tokens.css) as `--pv-*` custom properties. Everywhere else uses `var(--pv-*)`. `stylelint` enforces this — `color-no-hex` is on for `src/**/*.css` except `tokens.css`. Adding a color = adding a token first.

## Deploy

Cloudflare Pages project `patientvibes-main`, git-connected to this repo's `main` branch. Push to `main` is the deploy trigger (when the GitHub App webhook is healthy — see [CLAUDE.md](CLAUDE.md) for the manual-trigger fallback). Build command is `npm run build`, output is `dist/`.

## More

See [`CLAUDE.md`](CLAUDE.md) for the full operational guide: the cross-site contract, the 1Password vault layout, the Cloudflare account context, common ops, and what to watch out for.
