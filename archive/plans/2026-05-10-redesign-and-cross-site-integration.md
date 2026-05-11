# PatientVibes Redesign + Cross-Site Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the stale gradient `index.html` on `patientvibes.io` with the dropped "Sage Editorial" Homepage mockup as a real Astro site, lock the design tokens, self-host fonts, and wire the homepage to truthful project data pulled at build time from `agents.patientvibes.io`. Add an RSS feed and an APCA accessibility fix in the same pass. On the agents-site, expose a `projects.json` endpoint and adopt the Project Page mockup for the kindle-pipeline detail page.

**Architecture:**
- `patientvibes-main` migrates from single-file static HTML → Astro 6 + Tailwind-free (uses the dropped sage-editorial CSS verbatim) to match `patientvibes-agents-site` stack. Build command on Cloudflare Pages becomes `npm run build`, output `dist/`.
- The bench panel and the project rows on the homepage are bound to a build-time fetch of `https://agents.patientvibes.io/api/projects.json` (with a committed fallback fixture). Single source of truth — `agents.patientvibes.io` owns project metadata, `patientvibes.io` consumes it.
- Notes live as an Astro content collection in `patientvibes-main`. RSS is generated at build via `@astrojs/rss`. Auto-discovery via `<link rel="alternate">` in `BaseLayout`.
- Tokens are treated as a schema. `stylelint` blocks raw hex colors outside `tokens.css`. APCA-failing pair `--pv-mute` on `--pv-bg` is darkened in this pass.

**Tech Stack:**
- Astro 6.3.x (matches sibling agents-site), Node ≥22.12
- No Tailwind here — the dropped `tokens.css` / `base.css` / `components.css` are the design system, imported globally
- Self-hosted fonts: Instrument Serif (italic + roman 400), Inter (400/500/600), JetBrains Mono (400/500), all woff2, Latin subset, via `font-display: swap`
- `stylelint` + `stylelint-config-recommended` + `stylelint-declaration-strict-value` (or a small custom rule) to enforce `var(--pv-*)` for colors outside `tokens.css`
- `@astrojs/rss` for the feed
- Cloudflare Pages (git-connected) for both repos

---

## File Structure (after this plan)

### `patientvibes-main/` (this repo, new layout)

```
patientvibes-main/
├── astro.config.mjs                 # NEW — mirrors agents-site config
├── package.json                      # NEW — Node project, scripts: dev/build/preview/lint/fetch-projects
├── tsconfig.json                     # NEW — Astro tsconfig
├── .gitignore                        # NEW — node_modules, dist, .astro, .cache
├── .stylelintrc.json                 # NEW — color-no-hex rule with allowlist for tokens.css
├── public/
│   ├── brand/
│   │   ├── favicon.svg               # MOVED from /brand/
│   │   └── favicon-dark.svg          # MOVED from /brand/
│   └── fonts/                        # NEW — self-hosted woff2
│       ├── instrument-serif-400-italic.woff2
│       ├── instrument-serif-400.woff2
│       ├── inter-400.woff2
│       ├── inter-500.woff2
│       ├── inter-600.woff2
│       ├── jetbrains-mono-400.woff2
│       └── jetbrains-mono-500.woff2
├── src/
│   ├── styles/
│   │   ├── tokens.css                # MOVED from /design-system/, with APCA fix
│   │   ├── base.css                  # MOVED from /design-system/
│   │   ├── components.css            # MOVED from /design-system/
│   │   └── fonts.css                 # NEW — @font-face declarations
│   ├── layouts/
│   │   └── BaseLayout.astro          # NEW — head, fonts preload, nav, footer
│   ├── components/
│   │   ├── ProjectRow.astro          # NEW — one project tile (whole-row link)
│   │   ├── NoteRow.astro             # NEW — one note tile (whole-row link)
│   │   ├── BenchPanel.astro          # NEW — "Now / what's on the bench"
│   │   └── Terminal.astro            # NEW — the terminal block in the Now section
│   ├── content.config.ts             # NEW — Zod schema for notes collection
│   ├── content/
│   │   └── notes/
│   │       └── 2026-04-18-on-patient-agents.md  # NEW — seed note (single one to make build green)
│   ├── lib/
│   │   └── load-projects.ts          # NEW — reads .cache/projects.json, falls back to fixture
│   └── pages/
│       ├── index.astro               # NEW — homepage from Homepage.html
│       └── index.xml.ts              # NEW — RSS endpoint via @astrojs/rss
├── scripts/
│   └── fetch-projects.mjs            # NEW — build-time fetch from agents.patientvibes.io/api/projects.json
├── __fixtures__/
│   └── projects.json                 # NEW — committed fallback for offline builds
├── .cache/                           # NEW (gitignored) — populated by fetch-projects.mjs
├── docs/
│   └── superpowers/
│       └── plans/
│           └── 2026-05-10-redesign-and-cross-site-integration.md  # THIS FILE
├── archive/                          # NEW — keep history visible without polluting root
│   ├── index-v1-gradient.html        # MOVED — old index.html
│   └── mockups-2026-05-10/           # MOVED — Homepage.html, Project Page*.html, etc.
│       ├── Homepage.html
│       ├── Homepage Dark.html
│       ├── Design System.html
│       ├── OG Card.html
│       ├── Project Page.html
│       └── Project Page v2.html
├── CLAUDE.md                         # MODIFIED — Astro stack, new file map, cross-site contract
└── README.md                         # MODIFIED — current truth, not Property Survey GIS lore
```

### `patientvibes-agents-site/` (sibling, additive changes only)

```
patientvibes-agents-site/
├── src/
│   ├── pages/
│   │   ├── api/
│   │   │   └── projects.json.ts      # NEW — emits {id, kind, status, last_run, summary}
│   │   └── tools/
│   │       └── [slug].astro          # MODIFIED — adopt Project Page v2 design for kindle-pipeline at minimum
│   ├── layouts/
│   │   └── ToolLayout.astro          # NEW (optional refactor) — lifts the Project Page v2 chrome
│   └── styles/
│       └── tokens.css                # NEW or MODIFIED — same tokens vendored in for consistency (or @import from a shared package — keep it simple, vendor in)
└── public/
    └── images/
        └── kindle-scribe-pipeline-output.jpg  # NEW — the one real photo
```

---

## Cross-cutting decisions baked into this plan

1. **The bench grid stays — but only because we make it real.** Item 4 in the spec said "kill the bench grid unless the cron is real." The plan makes it real by binding it to `/api/projects.json` from agents-site at build time. If the fetch fails AND no fixture is committed, the bench panel renders a single static line ("Currently: kindle-pipeline · book #2") instead of a multi-row grid. This honors the spirit of item 4 (no empty promises) without abandoning the design.

2. **The Project Page mockups target the agents-site, not patientvibes.io.** Every project link on the new homepage points to `agents.patientvibes.io`. So the `Project Page.html` / `Project Page v2.html` mockups are upgrades to agents-site's tool pages. This plan adopts v2 for the kindle-pipeline page only (minimum to satisfy item 7); a follow-up plan can roll it out to all 10 tool pages.

3. **Tokens vendored in both repos.** Cleaner than a shared npm package for a 2-repo personal portfolio. Bumping a token = a coordinated PR in both. The CLAUDE.md update calls this out.

4. **Old gradient `index.html` is archived, not deleted.** Move to `archive/index-v1-gradient.html`. Cheap insurance, zero deploy cost (no link to it).

5. **CLAUDE.md says "no build step" today — that's about to be wrong.** Updated in the final task. The new build is `npm run build`; Cloudflare Pages settings need to flip too.

---

## Phase 1 — patientvibes-main: Astro scaffold + foundation

### Task 1: Archive old files; set up Astro project skeleton

**Files:**
- Create: `archive/index-v1-gradient.html` (the move target)
- Create: `archive/mockups-2026-05-10/` (the move target)
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`, `.gitignore`
- Modify: nothing yet
- Test: `npm run build` succeeds with empty `src/pages/index.astro`

- [ ] **Step 1: Move old files into `/archive/`**

```bash
cd D:/patientvibes-main
mkdir -p archive/mockups-2026-05-10
git mv index.html archive/index-v1-gradient.html
mv "Homepage.html" "Homepage Dark.html" "Design System.html" "OG Card.html" "Project Page.html" "Project Page v2.html" archive/mockups-2026-05-10/
```

(Mockups are untracked — `mv` not `git mv`. They'll get added later as untracked archive material when we commit.)

- [ ] **Step 2: Create `package.json`**

Write `package.json`:

```json
{
  "name": "patientvibes-main",
  "type": "module",
  "version": "0.1.0",
  "private": true,
  "engines": { "node": ">=22.12.0" },
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "astro": "astro",
    "fetch-projects": "node scripts/fetch-projects.mjs",
    "prebuild": "npm run fetch-projects",
    "lint": "stylelint \"src/**/*.{css,astro}\"",
    "lint:fix": "stylelint --fix \"src/**/*.{css,astro}\""
  },
  "dependencies": {
    "@astrojs/rss": "^4.0.10",
    "@astrojs/sitemap": "^3.7.2",
    "astro": "^6.3.1"
  },
  "devDependencies": {
    "stylelint": "^16.0.0",
    "stylelint-config-recommended": "^14.0.0"
  }
}
```

- [ ] **Step 3: Create `astro.config.mjs`**

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://patientvibes.io',
  integrations: [sitemap()],
});
```

- [ ] **Step 4: Create `tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist", "archive"]
}
```

- [ ] **Step 5: Create `.gitignore`**

```gitignore
node_modules/
dist/
.astro/
.cache/
.env
.DS_Store
```

- [ ] **Step 6: Stub `src/pages/index.astro` so the build has something to compile**

```astro
---
---
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>patientvibes — scaffold</title></head>
<body><p>scaffold ok</p></body>
</html>
```

- [ ] **Step 7: Install and verify the build**

```bash
cd D:/patientvibes-main
npm install
npm run build
```

Expected: build succeeds; `dist/index.html` exists; `npm run preview` serves it. (At this point `prebuild`/`fetch-projects` will fail because the script doesn't exist yet — temporarily comment out the `prebuild` line to verify the scaffold compiles. Restore it in Task 9.)

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "chore: scaffold Astro project; archive old gradient index and mockups

Single-file static index moved to archive/. Astro 6 scaffold matches
patientvibes-agents-site stack. Build still empty — content lands in
the next phase."
```

---

### Task 2: Move design-system CSS into `src/styles/` and apply APCA fix

**Files:**
- Create: `src/styles/tokens.css`, `src/styles/base.css`, `src/styles/components.css` (moved from `/design-system/`)
- Delete: `/design-system/` directory after move
- Modify: `src/styles/tokens.css` — change `--pv-mute: #5d6f64` → `#52635a` for AA on `--pv-bg`

- [ ] **Step 1: Move CSS files**

```bash
cd D:/patientvibes-main
mkdir -p src/styles
git mv design-system/tokens.css src/styles/tokens.css     # untracked move; use mv if git complains
git mv design-system/base.css src/styles/base.css
git mv design-system/components.css src/styles/components.css
rmdir design-system
```

(If files are untracked, plain `mv` is fine; `git mv` only matters for tracked files.)

- [ ] **Step 2: Apply APCA fix in `src/styles/tokens.css`**

Find:

```css
  --pv-mute:      #5d6f64;  /* secondary, labels */
```

Replace with:

```css
  --pv-mute:      #52635a;  /* secondary, labels — APCA-fixed for body on --pv-bg (was #5d6f64, ~4.3:1, failed AA at 16px) */
```

Also add (just below the existing `--pv-sage` line) a comment noting the sage AA caveat:

```css
  --pv-sage:      #3F6B54;  /* signature accent — body contrast on --pv-bg ~4.8:1; reserve for ≥18px headings/links, not 16px body */
```

- [ ] **Step 3: Manual verify in browser**

```bash
npm run dev
```

Open `http://localhost:4321/`. The scaffold page is unstyled — that's fine for this task. Goal here is just that the dev server still starts.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: move design-system CSS to src/styles/; darken --pv-mute for AA

--pv-mute on --pv-bg was ~4.3:1 (fails AA for 16px body). New value
#52635a passes AA. Comment added explaining the constraint."
```

---

### Task 3: Self-host fonts; add @font-face; preload above-the-fold faces

**Files:**
- Create: `public/fonts/` with woff2 files (downloaded via google-webfonts-helper)
- Create: `src/styles/fonts.css`

- [ ] **Step 1: Download woff2 files**

Use https://gwfh.mranftl.com/fonts (google-webfonts-helper). For each family below: select `woff2` only, charsets = `latin` only, copy/download the files into `public/fonts/`. Rename them to the kebab-case names below for predictability.

| Family | Weights/styles to grab |
|---|---|
| Instrument Serif | 400 italic, 400 roman |
| Inter | 400, 500, 600 |
| JetBrains Mono | 400, 500 |

Final file list in `public/fonts/`:
- `instrument-serif-400-italic.woff2`
- `instrument-serif-400.woff2`
- `inter-400.woff2`
- `inter-500.woff2`
- `inter-600.woff2`
- `jetbrains-mono-400.woff2`
- `jetbrains-mono-500.woff2`

(Manual step — do this once, commit the binary files.)

- [ ] **Step 2: Create `src/styles/fonts.css`**

```css
/* patientvibes/agents — self-hosted fonts. Latin subset only. */

@font-face {
  font-family: 'Instrument Serif';
  font-style: italic;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/instrument-serif-400-italic.woff2') format('woff2');
}
@font-face {
  font-family: 'Instrument Serif';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/instrument-serif-400.woff2') format('woff2');
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/inter-400.woff2') format('woff2');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('/fonts/inter-500.woff2') format('woff2');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/inter-600.woff2') format('woff2');
}

@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/jetbrains-mono-400.woff2') format('woff2');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('/fonts/jetbrains-mono-500.woff2') format('woff2');
}
```

- [ ] **Step 3: Verify the dev server still starts**

```bash
npm run dev
```

Open browser. Network tab: woff2 files should load from `/fonts/...` once `BaseLayout` (Task 4) consumes them. (No visible change yet — `BaseLayout` doesn't exist.)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: self-host Instrument Serif, Inter, JetBrains Mono in /fonts/

Latin subset only, woff2, font-display: swap. Replaces Google Fonts CDN
in the homepage mockup. Preloads happen in BaseLayout (next commit)."
```

---

### Task 4: Move brand favicons into `public/brand/`

- [ ] **Step 1: Move**

```bash
cd D:/patientvibes-main
mkdir -p public/brand
mv brand/favicon.svg public/brand/favicon.svg
mv brand/favicon-dark.svg public/brand/favicon-dark.svg
rmdir brand
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "chore: move brand favicons under public/brand/"
```

---

### Task 5: Add stylelint with hex-color allowlist

**Files:**
- Create: `.stylelintrc.json`

- [ ] **Step 1: Write `.stylelintrc.json`**

```json
{
  "extends": ["stylelint-config-recommended"],
  "rules": {
    "color-no-hex": [true, {
      "severity": "error",
      "message": "Hex colors are not allowed outside src/styles/tokens.css. Use a var(--pv-*) token instead."
    }]
  },
  "overrides": [
    {
      "files": ["src/styles/tokens.css"],
      "rules": { "color-no-hex": null }
    }
  ]
}
```

- [ ] **Step 2: Run lint to confirm tokens.css is the only file with raw hexes**

```bash
npm run lint
```

Expected: passes. `tokens.css` is allowlisted; nothing else has raw hex yet.

- [ ] **Step 3: Negative test — temporarily add a hex elsewhere and confirm lint fails**

Add to the bottom of `src/styles/base.css`:

```css
.lint-canary { color: #ff0000; }
```

Run:

```bash
npm run lint
```

Expected: FAIL with "Hex colors are not allowed outside src/styles/tokens.css..."

Remove the canary line.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "build: add stylelint with color-no-hex rule (allowlist tokens.css)

Treat tokens.css as the schema. PRs that introduce one-off hex colors
fail lint. tokens.css is the only allowlisted file."
```

---

## Phase 2 — patientvibes-main: BaseLayout + homepage components

### Task 6: Create `src/layouts/BaseLayout.astro`

**Files:**
- Create: `src/layouts/BaseLayout.astro`

- [ ] **Step 1: Write `BaseLayout.astro`**

```astro
---
import '../styles/fonts.css';
import '../styles/tokens.css';
import '../styles/base.css';
import '../styles/components.css';

interface Props {
  title: string;
  description?: string;
  rss?: boolean;
}
const { title, description, rss = true } = Astro.props;
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  {description && <meta name="description" content={description} />}
  <link rel="canonical" href={Astro.url.href} />
  <link rel="icon" type="image/svg+xml" href="/brand/favicon.svg" />
  <link rel="icon" type="image/svg+xml" href="/brand/favicon-dark.svg" media="(prefers-color-scheme: dark)" />

  <!-- Above-the-fold font preloads (the two we use on first paint: serif italic for hero, Inter 500 for nav) -->
  <link rel="preload" href="/fonts/instrument-serif-400-italic.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/inter-500.woff2" as="font" type="font/woff2" crossorigin />

  {rss && <link rel="alternate" type="application/rss+xml" title="patientvibes — notes" href="/index.xml" />}
</head>
<body>
  <slot />
</body>
</html>
```

- [ ] **Step 2: Smoke-test by replacing the scaffold `index.astro`**

Replace `src/pages/index.astro` with:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="patientvibes — scaffold check">
  <main style="max-width: 980px; margin: 0 auto; padding: 24px;">
    <h1 class="pv-display-3">Sage editorial scaffold</h1>
    <p class="pv-body">If this is set in Instrument Serif + Inter, the layout works.</p>
  </main>
</BaseLayout>
```

- [ ] **Step 3: Verify in browser**

```bash
npm run dev
```

Open `http://localhost:4321/`. Expected:
- Heading is set in Instrument Serif (the dropped face, not a generic serif)
- Body is in Inter
- Network tab shows two preload requests for the two woff2s above the fold
- Favicon shows in the tab

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add BaseLayout with font preloads, favicon, RSS auto-discovery

Above-the-fold preloads: Instrument Serif 400 italic (hero), Inter 500
(nav). Other faces font-display: swap into place. RSS link tag wired
for autodiscovery (endpoint added in Phase 5)."
```

---

### Task 7: Extract homepage components from the mockup

The mockup has page-local CSS in a `<style>` block. We're going to:
- Move shared selectors that re-occur (project row, note row, terminal) into `src/styles/components.css` if they're general; keep page-only chrome (`.hp-*` classes) inline in a `<style>` block in `index.astro`. Most `.hp-*` classes are page-specific — keep them with the page. Easier to maintain.

**Files:**
- Create: `src/components/ProjectRow.astro`
- Create: `src/components/NoteRow.astro`
- Create: `src/components/BenchPanel.astro`
- Create: `src/components/Terminal.astro`

- [ ] **Step 1: Define the project row component**

Write `src/components/ProjectRow.astro`:

```astro
---
interface Props {
  id: string;            // "H–01", "T–02", etc.
  href: string;          // destination (usually agents.patientvibes.io/tools/<slug>/)
  name: string;          // "agent-tool-pr-reviewer"
  description: string;
  status: 'live' | 'build' | 'draft' | 'shipped';
  statusLabel: string;   // "dev", "building", "drafting", "shipped"
  meta?: { k: string; v: string }[];
  date?: string;         // "2026 · 04"
}
const { id, href, name, description, status, statusLabel, meta = [], date } = Astro.props;
const statusClass = `hp-proj__status hp-proj__status--${status}`;
---
<a class="hp-proj" href={href}>
  <span class="hp-proj__id">{id}</span>
  <div class="hp-proj__body">
    <div class="hp-proj__head">
      <span class="hp-proj__name">{name} <span class="hp-proj__arrow">→</span></span>
      <span class={statusClass}><i></i>{statusLabel}</span>
    </div>
    <p class="hp-proj__desc" set:html={description} />
    {meta.length > 0 && (
      <div class="hp-proj__meta">
        {meta.map(m => (
          <span><span class="k">{m.k} ·</span> <span class="v">{m.v}</span></span>
        ))}
      </div>
    )}
  </div>
  {date && <div class="hp-proj__date">{date}</div>}
</a>
```

(Note: `set:html` is used for description so inline `<code>` markup from project data renders. Source data is trusted — we control `projects.json` — but if untrusted data ever flows through, swap to plain text.)

- [ ] **Step 2: Define the note row component**

Write `src/components/NoteRow.astro`:

```astro
---
interface Props {
  date: string;       // "2026 · 04 · 18"
  title: string;      // may contain <em>...</em>
  href: string;
  readMin: number;
}
const { date, title, href, readMin } = Astro.props;
---
<a class="hp-note" href={href}>
  <span class="hp-note__date">{date}</span>
  <span class="hp-note__title" set:html={title} />
  <span class="hp-note__read">{readMin} min</span>
</a>
```

- [ ] **Step 3: Define the bench panel component**

Write `src/components/BenchPanel.astro`:

```astro
---
interface Props {
  inFlightCount: number;
  items: { state: 'shipped' | 'flight' | 'queued'; label: string; tag: string; when: string }[];
}
const { inFlightCount, items } = Astro.props;
const stateClass = (s: 'shipped' | 'flight' | 'queued') => s === 'flight' ? '' : s;
---
<div class="hp-now__panel">
  <div class="hp-now__panel-head">
    <span>Bench · this week</span>
    <span class="right"><i></i>{inFlightCount} in flight</span>
  </div>
  <ul class="hp-now__list">
    {items.map(it => (
      <li class={stateClass(it.state)}>
        <span class="dot"></span>
        <span class="label">{it.label} <em>· {it.tag}</em></span>
        <span class="when" set:html={it.when} />
      </li>
    ))}
  </ul>
</div>
```

- [ ] **Step 4: Define the terminal component**

Write `src/components/Terminal.astro` — copy the `<div class="pv-terminal">...</div>` block from `archive/mockups-2026-05-10/Homepage.html` lines 448-462 verbatim, wrapped in:

```astro
---
---
<div class="pv-terminal">
  <!-- paste the verbatim block here -->
</div>
```

(Static content — no props yet. If you later want to drive this from the most recent kindle-pipeline run, props can come in then.)

- [ ] **Step 5: Verify components compile (smoke-test by importing one)**

Add to the scaffold `src/pages/index.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import ProjectRow from '../components/ProjectRow.astro';
---
<BaseLayout title="component check">
  <main style="max-width: 980px; margin: 24px auto; padding: 24px;">
    <ProjectRow
      id="T–01"
      href="https://agents.patientvibes.io/tools/agent-tool-pr-reviewer/"
      name="agent-tool-pr-reviewer"
      description="CLI that reviews the current git branch's diff."
      status="live"
      statusLabel="dev"
      date="2026 · 04"
    />
  </main>
</BaseLayout>
```

```bash
npm run dev
```

Expected: one styled project row renders. Hover changes background and color. The arrow shifts right.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add ProjectRow / NoteRow / BenchPanel / Terminal components

Extracted from the Homepage.html mockup. Page-local .hp-* CSS will
live with the page; these components handle structure and props."
```

---

### Task 8: Build the real homepage from the mockup

**Files:**
- Modify: `src/pages/index.astro` (full replacement)

This task ports the mockup. Project / note / bench data is hardcoded for now — Task 11 swaps it for fetched data.

- [ ] **Step 1: Write `src/pages/index.astro`**

Open `archive/mockups-2026-05-10/Homepage.html`. Copy the entire `<style>` block (lines 13-130) and the entire `<body>` content (lines 132-484, but excluding the cloudflare email-decode script line 484) into a new `index.astro`. Wrap in:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import ProjectRow from '../components/ProjectRow.astro';
import NoteRow from '../components/NoteRow.astro';
import BenchPanel from '../components/BenchPanel.astro';
import Terminal from '../components/Terminal.astro';

// HARDCODED for this task; replaced by fetched data in Task 11.
const harnesses = [
  { id: 'H–01', href: 'https://agents.patientvibes.io/tools/agent-harness-kindle-pipeline/', name: 'agent-harness-kindle-pipeline', description: "Orchestrator for the Kindle Scribe pipeline. Subprocess-calls each <code class='pv-mono' style='color:var(--pv-coral);font-size:13px;'>agent-tool-*</code> CLI in sequence per book listed in <code class='pv-mono' style='color:var(--pv-coral);font-size:13px;'>books.json</code>. Source PDF → Marker OCR → figure scan → strip pipeline → LLM proofread → book-builder PDF + Obsidian export.", status: 'live' as const, statusLabel: 'dev', meta: [{ k: 'composes', v: '8 tools' }, { k: 'tags', v: 'harness · kindle · ocr' }], date: '2026 · 04' },
];
const tools = [
  // copy entries T–01 through T–08 from Homepage.html lines 213-316
  // Each: { id, href: 'https://agents.patientvibes.io/tools/<slug>/', name, description, status, statusLabel, meta, date }
];
const skills = [
  // S–01 from lines 328-339
];
const workshop = [
  // W–01 and W–02 from lines 352-382 (status: 'build' / 'draft', href: '#' for now)
];
const notes = [
  { date: '2026 · 04 · 18', title: "On <em>patient</em> agents — why I stopped optimizing for fast.", href: '#', readMin: 7 },
  { date: '2026 · 04 · 02', title: "The harness comes first. The model comes last.", href: '#', readMin: 5 },
  { date: '2026 · 03 · 21', title: "Tools should be <em>boring</em>, like good libraries.", href: '#', readMin: 4 },
  { date: '2026 · 02 · 09', title: "A weekend with the ESP32 — notes for next time.", href: '#', readMin: 6 },
];
const bench = {
  inFlightCount: 2,
  items: [
    { state: 'shipped' as const, label: 'agents.patientvibes.io · v1 catalog', tag: 'site', when: 'today' },
    { state: 'flight' as const, label: 'llm-proofreader · false-positive memory', tag: 'tool', when: 'in&nbsp;flight' },
    { state: 'flight' as const, label: 'kindle-pipeline · second book', tag: 'harness', when: 'in&nbsp;flight' },
    { state: 'queued' as const, label: 'hotel · multi-card support', tag: 'esp32', when: 'queued' },
    { state: 'queued' as const, label: 'desk parts · cable comb v2', tag: '3d-print', when: 'queued' },
  ],
};
---
<BaseLayout title="patientvibes — index" description="A workshop for patient things. Agents, the tools they need, and the harnesses that keep them honest.">
  <style is:global>
    /* PASTE the entire <style> block from archive/mockups-2026-05-10/Homepage.html lines 14-129 here */
  </style>

  <div class="hp">
    <!-- Nav: paste lines 137-148 -->

    <!-- Hero: paste lines 151-174 -->

    <!-- Harnesses: section header from lines 177-184, then map harnesses -->
    <section id="projects" class="hp-sec">
      <div class="hp-sec__head">
        <div class="hp-sec__title">
          <span class="hp-sec__num">01 · Harnesses</span>
          <h2 class="hp-sec__name">The orchestrators.</h2>
        </div>
        <span class="hp-sec__count">{harnesses.length} {harnesses.length === 1 ? 'entry' : 'entries'} · <a href="https://agents.patientvibes.io" style="color:inherit;text-decoration:underline;text-underline-offset:3px;">see all in catalog →</a></span>
      </div>
      {harnesses.map(p => <ProjectRow {...p} />)}
    </section>

    <!-- Tools: same shape, "see all in catalog →" in section count -->
    <section class="hp-sec">
      <div class="hp-sec__head">
        <div class="hp-sec__title">
          <span class="hp-sec__num">02 · Tools</span>
          <h2 class="hp-sec__name">Single-purpose CLIs.</h2>
        </div>
        <span class="hp-sec__count">{String(tools.length).padStart(2, '0')} entries · <a href="https://agents.patientvibes.io" style="color:inherit;text-decoration:underline;text-underline-offset:3px;">see all in catalog →</a></span>
      </div>
      {tools.map(p => <ProjectRow {...p} />)}
    </section>

    <!-- Skills, Workshop: same pattern -->

    <!-- Notes: section header + {notes.map(n => <NoteRow {...n} />)} -->

    <!-- Now: hero quote/sub from lines 427-431, then <BenchPanel {...bench} />, then <div class="hp-term-wrap"><Terminal /></div> -->

    <!-- Footer: paste lines 467-480 -->
  </div>
</BaseLayout>
```

(The `tools`, `skills`, `workshop` arrays must be filled in from the mockup — this is mechanical copy work. Each ProjectRow entry's `href` should point to `https://agents.patientvibes.io/tools/<slug>/` for tools/harnesses/skills, and `#` for the W–01 / W–02 workshop entries until they have permalinks.)

- [ ] **Step 2: Replace the section-header "see all in catalog" pattern**

Per spec item 6: "Move the catalog link to the section header so the row's primary affordance is the page, not the catalog." Done above by adding `· see all in catalog →` next to the entry count. Confirm visually that the project rows themselves no longer contain a separate "catalog" link.

- [ ] **Step 3: Verify in browser**

```bash
npm run dev
```

Open `http://localhost:4321/`. Compare side-by-side with `archive/mockups-2026-05-10/Homepage.html` open in a second tab. Expected:
- Identical visual rendering (modulo Cloudflare's email-decode script, which we drop)
- Hover on a project row changes background and shifts arrow
- Mobile (resize ≤720px): hero/now collapse to single column; project rows lose date column
- Section count chips show "see all in catalog →" link

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: ship sage-editorial homepage; move catalog link to section header

Replaces the gradient/Property-Survey-GIS index.html with the new
'workshop for patient things' homepage. Project, note, and bench data
are hardcoded — Task 11 binds them to projects.json from agents-site.

Per spec item 6: section header now carries 'see all in catalog →' so
the row's primary affordance is the project page, not the catalog."
```

---

## Phase 3 — patientvibes-agents-site: expose `/api/projects.json`

### Task 9: Add `projects.json` endpoint to agents-site

**Files (in D:/patientvibes-agents-site):**
- Create: `src/pages/api/projects.json.ts`

- [ ] **Step 1: Inspect existing tool frontmatter**

```bash
head -12 D:/patientvibes-agents-site/src/content/tools/agent-harness-kindle-pipeline.md
```

Expected fields (from `pull-readmes.mjs`): `slug, name, kind, status, githubUrl, shortDescription, pulledAt`.

- [ ] **Step 2: Write the endpoint**

Write `D:/patientvibes-agents-site/src/pages/api/projects.json.ts`:

```ts
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const tools = await getCollection('tools');

  const projects = tools.map(t => ({
    id: t.data.slug,
    kind: t.data.kind,
    name: t.data.name,
    status: t.data.status,
    last_run: t.data.pulledAt,
    summary: t.data.shortDescription,
    url: `https://agents.patientvibes.io/tools/${t.data.slug}/`,
    githubUrl: t.data.githubUrl,
  }));

  return new Response(JSON.stringify({
    generatedAt: new Date().toISOString(),
    count: projects.length,
    projects,
  }, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      // Cache 5 min at the edge so a README edit shows up the same day, not next week.
      'Cache-Control': 'public, max-age=60, s-maxage=300, stale-while-revalidate=86400',
      'Access-Control-Allow-Origin': '*',
    },
  });
};
```

- [ ] **Step 3: Build and verify**

```bash
cd D:/patientvibes-agents-site
npm run build
ls dist/api/projects.json
```

Expected: file exists. `cat dist/api/projects.json | head -30` shows valid JSON with 10 projects.

- [ ] **Step 4: Smoke-test via dev server**

```bash
npm run dev
```

Open `http://localhost:4321/api/projects.json`. Expected: JSON renders in the browser with all 10 entries.

- [ ] **Step 5: Commit and push**

```bash
cd D:/patientvibes-agents-site
git add -A
git commit -m "feat: expose /api/projects.json for cross-site consumption

patientvibes.io fetches this at build time to drive its homepage
project rows and 'now / on the bench' panel. 5-min edge cache so a
README edit propagates within the day. CORS open for any origin —
public catalog data."
git push origin main
```

(After this push lands, https://agents.patientvibes.io/api/projects.json should be live within ~30s of Cloudflare Pages deploying.)

---

## Phase 4 — patientvibes-main: bind real data at build time

### Task 10: Add `scripts/fetch-projects.mjs` and a fixture

**Files (in D:/patientvibes-main):**
- Create: `scripts/fetch-projects.mjs`
- Create: `__fixtures__/projects.json`

- [ ] **Step 1: Write the fetch script**

```js
#!/usr/bin/env node
// Fetches https://agents.patientvibes.io/api/projects.json at build time.
// Saves to .cache/projects.json. Falls back to __fixtures__/projects.json
// if the fetch fails (so a Cloudflare build doesn't fail because the
// sibling site is briefly down).
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ENDPOINT = 'https://agents.patientvibes.io/api/projects.json';
const TIMEOUT_MS = 8000;

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cacheDir = path.join(repoRoot, '.cache');
const cachePath = path.join(cacheDir, 'projects.json');
const fixturePath = path.join(repoRoot, '__fixtures__', 'projects.json');

async function main() {
  await mkdir(cacheDir, { recursive: true });

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(ENDPOINT, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.text();
    JSON.parse(json); // validate it parses
    await writeFile(cachePath, json, 'utf-8');
    console.log(`[fetch-projects] OK · cached ${json.length} bytes from ${ENDPOINT}`);
  } catch (err) {
    clearTimeout(timer);
    console.warn(`[fetch-projects] FAILED (${err.message}) — using fixture`);
    try {
      const fixture = await readFile(fixturePath, 'utf-8');
      JSON.parse(fixture);
      await writeFile(cachePath, fixture, 'utf-8');
      console.log('[fetch-projects] OK · cached from __fixtures__/projects.json');
    } catch (fxErr) {
      console.error(`[fetch-projects] FATAL: no fixture available (${fxErr.message})`);
      process.exit(1);
    }
  }
}

main();
```

- [ ] **Step 2: Create `__fixtures__/projects.json`**

This is the committed fallback. Easiest way to populate it: run the live endpoint after Task 9 deploys.

```bash
cd D:/patientvibes-main
mkdir -p __fixtures__
curl -fsS https://agents.patientvibes.io/api/projects.json > __fixtures__/projects.json
```

(If the deploy hasn't propagated yet: copy from `D:/patientvibes-agents-site/dist/api/projects.json` after running `npm run build` there.)

- [ ] **Step 3: Restore `prebuild` in `package.json`**

If you commented out the `prebuild` line during Task 1 Step 7, re-enable it now:

```json
"prebuild": "npm run fetch-projects",
```

- [ ] **Step 4: Verify the script works**

```bash
cd D:/patientvibes-main
npm run fetch-projects
cat .cache/projects.json | head -5
```

Expected: `.cache/projects.json` exists with valid JSON.

- [ ] **Step 5: Verify fallback works (offline simulation)**

Temporarily change `ENDPOINT` to `https://invalid.example.invalid/api/projects.json` in the script. Re-run:

```bash
npm run fetch-projects
```

Expected: warning printed, but `.cache/projects.json` still gets written (from the fixture). Restore `ENDPOINT`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "build: fetch projects.json from agents.patientvibes.io at build time

Pulls the live catalog into .cache/projects.json before each build.
Falls back to __fixtures__/projects.json on network failure so a
Cloudflare deploy doesn't fail when the sibling site is briefly down.
8s timeout. .cache/ is gitignored; __fixtures__/projects.json is
committed."
```

---

### Task 11: Wire fetched data into the homepage

**Files:**
- Create: `src/lib/load-projects.ts`
- Modify: `src/pages/index.astro` (replace hardcoded arrays)

- [ ] **Step 1: Write the loader**

Write `src/lib/load-projects.ts`:

```ts
import { readFile } from 'node:fs/promises';
import path from 'node:path';

export interface Project {
  id: string;
  kind: 'tool' | 'harness' | 'skill';
  name: string;
  status: string;
  last_run: string;
  summary: string;
  url: string;
  githubUrl: string;
}

interface Catalog {
  generatedAt: string;
  count: number;
  projects: Project[];
}

let cached: Catalog | null = null;

export async function loadProjects(): Promise<Catalog> {
  if (cached) return cached;
  const cachePath = path.resolve(process.cwd(), '.cache/projects.json');
  const raw = await readFile(cachePath, 'utf-8');
  cached = JSON.parse(raw);
  return cached!;
}

export function byKind(projects: Project[], kind: Project['kind']): Project[] {
  return projects.filter(p => p.kind === kind);
}

// Maps catalog status → display ('live' | 'build' | 'draft' | 'shipped' + label).
// 'dev' / version tags → live, anything else → build.
export function displayStatus(status: string): { state: 'live' | 'build' | 'draft' | 'shipped'; label: string } {
  if (status === 'unavailable') return { state: 'draft', label: 'offline' };
  if (status === 'fixture') return { state: 'draft', label: 'fixture' };
  if (status === 'dev' || status.startsWith('v')) return { state: 'live', label: status };
  return { state: 'build', label: status };
}

// Pretty-print the pulledAt timestamp as "2026 · 04".
export function formatYearMonth(iso: string): string {
  const d = new Date(iso);
  return `${d.getUTCFullYear()} · ${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}

// Build a short id like "T–01", "H–01", "S–01" from kind + 1-based index.
export function shortId(kind: Project['kind'], index1: number): string {
  const letter = kind === 'tool' ? 'T' : kind === 'harness' ? 'H' : 'S';
  return `${letter}–${String(index1).padStart(2, '0')}`;
}
```

- [ ] **Step 2: Replace the hardcoded arrays in `src/pages/index.astro`**

At the top of the frontmatter, replace `const tools = [...]` etc. with:

```ts
import { loadProjects, byKind, displayStatus, formatYearMonth, shortId } from '../lib/load-projects';

const catalog = await loadProjects();
const allProjects = catalog.projects;

const harnesses = byKind(allProjects, 'harness').map((p, i) => {
  const ds = displayStatus(p.status);
  return {
    id: shortId('harness', i + 1),
    href: p.url,
    name: p.name,
    description: p.summary,
    status: ds.state,
    statusLabel: ds.label,
    meta: [],
    date: formatYearMonth(p.last_run),
  };
});

const tools = byKind(allProjects, 'tool').map((p, i) => {
  const ds = displayStatus(p.status);
  return {
    id: shortId('tool', i + 1),
    href: p.url,
    name: p.name,
    description: p.summary,
    status: ds.state,
    statusLabel: ds.label,
    meta: [],
    date: formatYearMonth(p.last_run),
  };
});

const skills = byKind(allProjects, 'skill').map((p, i) => {
  const ds = displayStatus(p.status);
  return {
    id: shortId('skill', i + 1),
    href: p.url,
    name: p.name,
    description: p.summary,
    status: ds.state,
    statusLabel: ds.label,
    meta: [],
    date: formatYearMonth(p.last_run),
  };
});

// Workshop entries stay hardcoded — they're not in the agents catalog (they're hardware/3D print).
const workshop = [
  { id: 'W–01', href: '#', name: 'hotel <span class="v">/ esp32 door scanner</span>', description: "My son got tired of asking for the lights. Now he swipes a hotel keycard, the bedroom lights come up, and the speaker says hi back. ESP32, an RFID reader, and far too much enthusiasm.", status: 'build' as const, statusLabel: 'building', meta: [{ k: 'hw', v: 'esp32 · rc522 · ws2812' }, { k: 'tags', v: 'esp32 · home' }], date: '2025 · 12' },
  { id: 'W–02', href: '#', name: 'desk parts <span class="v">/ small printed things</span>', description: "A collection-in-progress of printable parts I've designed for myself — cable combs, monitor risers, mounts for the things that don't ship with mounts. STL + notes on what failed before it worked.", status: 'draft' as const, statusLabel: 'drafting', meta: [{ k: 'tool', v: 'fusion 360 · prusa mk4' }, { k: 'tags', v: '3d-print' }], date: '2025 · 11' },
];

// Bench panel: take the most-recently-updated 5 from the catalog as "in flight" / "shipped".
// "In flight" = status starts with 'v' (released) is shipped; status === 'dev' is in flight.
const recent = [...allProjects].sort((a, b) => b.last_run.localeCompare(a.last_run)).slice(0, 5);
const bench = {
  inFlightCount: recent.filter(p => p.status === 'dev').length,
  items: recent.map(p => ({
    state: (p.status === 'dev' ? 'flight' : 'shipped') as 'flight' | 'shipped' | 'queued',
    label: p.name,
    tag: p.kind,
    when: p.status === 'dev' ? 'in&nbsp;flight' : formatYearMonth(p.last_run),
  })),
};
```

- [ ] **Step 3: Verify in browser**

```bash
npm run fetch-projects
npm run dev
```

Open `http://localhost:4321/`. Expected:
- Tools section shows ~8 entries pulled from the live catalog
- Harness section shows agent-harness-kindle-pipeline
- Skills section shows agent-skills (pr-review-tools)
- Bench panel shows 5 most-recently-updated projects, with `in flight` for dev
- Each project's date matches the `pulledAt` from the JSON

- [ ] **Step 4: Static "Currently:" fallback**

If `recent.length === 0` (catalog was empty), render a static "Currently: kindle-pipeline · book #2" line instead of the bench grid. Add this just before `<BenchPanel>` in the Now section:

```astro
{recent.length > 0
  ? <BenchPanel {...bench} />
  : <p class="hp-now__sub" style="margin-top: 0;"><span class="pv-mono" style="text-transform: uppercase; letter-spacing: var(--pv-track-eyebrow); color: var(--pv-mute);">currently · </span>kindle-pipeline · book #2.</p>
}
```

This honors spec item 4 — only promise the bench if we can fill it.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: bind homepage projects + bench to fetched projects.json

Single source of truth lives at agents.patientvibes.io/api/projects.json;
this build pulls it. Workshop entries stay hardcoded (hardware projects
not in the agents catalog). Bench panel shows the 5 most recent; if the
catalog is empty, falls back to a static 'Currently:' line."
```

---

## Phase 5 — patientvibes-main: notes content collection + RSS

### Task 12: Add notes content collection

**Files:**
- Create: `src/content.config.ts`
- Create: `src/content/notes/2026-04-18-on-patient-agents.md` (seed note)

- [ ] **Step 1: Write the schema**

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const notes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/notes' }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    summary: z.string(),
    readMin: z.number().int().positive().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { notes };
```

- [ ] **Step 2: Seed one note**

Write `src/content/notes/2026-04-18-on-patient-agents.md`:

```markdown
---
title: "On *patient* agents — why I stopped optimizing for fast"
pubDate: 2026-04-18
summary: "I used to chase shorter loops. Now I chase longer-lived ones — the kind that survive a model upgrade and a new SDK and still do what they did before."
readMin: 7
---

Placeholder — this is the seed note that exists so the build is green and the RSS feed has at least one item. Real essay text lands later.

Until then, the harness comes first. The model comes last.
```

(One real seed note keeps the homepage Notes section from being empty when the hardcoded list goes away. Replace with real prose at any time.)

- [ ] **Step 3: Verify content collection compiles**

```bash
npm run build
```

Expected: build succeeds. No type errors from `astro:content`.

- [ ] **Step 4: Wire notes into the homepage**

In `src/pages/index.astro`, replace the hardcoded `notes` array with:

```ts
import { getCollection } from 'astro:content';

const notesEntries = await getCollection('notes', e => !e.data.draft);
const notes = notesEntries
  .sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime())
  .map(e => ({
    date: `${e.data.pubDate.getUTCFullYear()} · ${String(e.data.pubDate.getUTCMonth() + 1).padStart(2, '0')} · ${String(e.data.pubDate.getUTCDate()).padStart(2, '0')}`,
    title: e.data.title.replace(/\*([^*]+)\*/g, '<em>$1</em>'),
    href: `/notes/${e.id.replace(/\.md$/, '')}/`,  // permalinks land later if you want them
    readMin: e.data.readMin ?? 5,
  }));
```

Update the Notes section count: `{notes.length} {notes.length === 1 ? 'entry' : 'entries'}`.

- [ ] **Step 5: Verify in browser**

```bash
npm run dev
```

Notes section shows the one seed note. Section count says "01 entry".

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add notes content collection with one seed entry

Single Zod-validated schema (title, pubDate, summary, readMin, draft).
Homepage Notes section now reads from the collection. Note permalinks
not yet routed — add src/pages/notes/[id].astro when you want them."
```

---

### Task 13: Add RSS endpoint

**Files:**
- Create: `src/pages/index.xml.ts`

- [ ] **Step 1: Install @astrojs/rss**

(Already added to package.json in Task 1; if missing, `npm install @astrojs/rss`.)

- [ ] **Step 2: Write the RSS endpoint**

```ts
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const notes = await getCollection('notes', e => !e.data.draft);
  const sorted = notes.sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());

  return rss({
    title: 'patientvibes — notes',
    description: 'A workshop for patient things. Notes on agents, the tools they need, and the harnesses that keep them honest.',
    site: context.site!,
    items: sorted.map(e => ({
      title: e.data.title,
      link: `/notes/${e.id.replace(/\.md$/, '')}/`,
      pubDate: e.data.pubDate,
      description: e.data.summary,
      author: 'chris.paul.moore@gmail.com (Chris Moore)',
    })),
    customData: '<language>en-us</language>',
  });
}
```

- [ ] **Step 3: Build and verify**

```bash
npm run build
ls dist/index.xml
```

Expected: `dist/index.xml` exists. `head -30 dist/index.xml` shows valid RSS XML with the seed note as one `<item>`.

- [ ] **Step 4: Verify autodiscovery in BaseLayout**

`BaseLayout.astro` already adds `<link rel="alternate" type="application/rss+xml">` (Task 6). Confirm by viewing source on `dist/index.html` — the `<head>` should contain it.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: generate /index.xml RSS feed at build time

Drives off the notes content collection. Autodiscovery via the
<link rel='alternate'> tag added to BaseLayout in an earlier task."
```

---

## Phase 6 — patientvibes-agents-site: Project Page v2 for kindle-pipeline + photo

### Task 14: Adopt Project Page v2 design for the kindle-pipeline tool page

**Files (in D:/patientvibes-agents-site):**
- Modify: `src/pages/tools/[slug].astro` (or whatever the current tool page route is — confirm by `ls src/pages/tools/`)

- [ ] **Step 1: Inspect the current tool page**

```bash
ls D:/patientvibes-agents-site/src/pages/tools/
cat D:/patientvibes-agents-site/src/pages/tools/[slug].astro 2>/dev/null || cat D:/patientvibes-agents-site/src/pages/tools/index.astro
```

Note the existing layout: probably uses `BaseLayout` + Tailwind classes.

- [ ] **Step 2: Vendor the sage-editorial tokens into agents-site**

```bash
cd D:/patientvibes-agents-site
mkdir -p src/styles
cp D:/patientvibes-main/src/styles/tokens.css src/styles/tokens.css
cp D:/patientvibes-main/src/styles/base.css src/styles/base.css
cp D:/patientvibes-main/src/styles/components.css src/styles/components.css
```

Import in `BaseLayout.astro` BELOW the existing Tailwind import — new design system coexists with Tailwind during transition.

- [ ] **Step 3: Conditionally apply the v2 design only for the kindle-pipeline page**

Easiest path: the tool page reads the slug. Add a conditional that swaps in the v2 chrome (copy from `D:/patientvibes-main/archive/mockups-2026-05-10/Project Page v2.html`) when `slug === 'agent-harness-kindle-pipeline'`. Other tool pages keep their current layout for now.

(Detailed component split for v2 is out of scope for this plan — file a follow-up plan when ready to roll v2 across all 10 tool pages.)

- [ ] **Step 4: Build and verify**

```bash
cd D:/patientvibes-agents-site
npm run build
npm run preview
```

Open `http://localhost:4321/tools/agent-harness-kindle-pipeline/`. Expected: v2 layout renders. Other tools (`/tools/agent-tool-pr-reviewer/` etc.) still use the old Tailwind layout.

- [ ] **Step 5: Commit and push**

```bash
cd D:/patientvibes-agents-site
git add -A
git commit -m "feat(tools): adopt sage-editorial Project Page v2 for kindle-pipeline

Vendor in patientvibes/tokens.css/base.css/components.css. Conditional
on slug — other tool pages stay on the existing Tailwind layout. Roll
out to all tools is a separate plan."
git push origin main
```

---

### Task 15: Add the Kindle Scribe photo

**Files (in D:/patientvibes-agents-site):**
- Create: `public/images/kindle-scribe-pipeline-output.jpg`

- [ ] **Step 1: Take the photo**

Manual step. Per spec item 7:
- Subject: Kindle Scribe with an annotated page from a pipeline output PDF visible
- Composition: top-down
- Lighting: natural light
- Surface: cream / warm neutral (matches `--pv-paper`)
- Format: JPG, max ~1600px wide, ~250kb (light enough to ship without lazy-loading)

Save as `D:/patientvibes-agents-site/public/images/kindle-scribe-pipeline-output.jpg`.

- [ ] **Step 2: Wire into the kindle-pipeline page**

In the v2 layout (Task 14's conditional), replace the `<image-slot>` placeholder in the hero with:

```astro
<img src="/images/kindle-scribe-pipeline-output.jpg"
     alt="Kindle Scribe showing an annotated page output by the kindle-pipeline harness"
     style="display: block; width: 100%; height: 520px; object-fit: cover;" />
```

- [ ] **Step 3: Verify in browser**

`npm run dev` in agents-site. Open `/tools/agent-harness-kindle-pipeline/`. Photo renders in hero.

- [ ] **Step 4: Commit and push**

```bash
cd D:/patientvibes-agents-site
git add public/images/kindle-scribe-pipeline-output.jpg src/pages/tools/[slug].astro
git commit -m "feat(tools): add Kindle Scribe photo to kindle-pipeline page hero

The harness ships artifacts. One real photo proves it. Top-down,
natural light, cream surface."
git push origin main
```

---

## Phase 7 — patientvibes-main: deploy config + docs + cleanup

### Task 16: Update Cloudflare Pages build settings

**Manual step** (no file changes in repo — touches Cloudflare dashboard).

- [ ] **Step 1: Open Cloudflare Pages settings**

```
https://dash.cloudflare.com → Workers & Pages → patientvibes-main → Settings → Builds & deployments
```

- [ ] **Step 2: Update build configuration**

| Field | Old value | New value |
|---|---|---|
| Build command | (empty) | `npm run build` |
| Build output directory | (empty / root) | `dist` |
| Root directory | / | / |
| Node version (env var `NODE_VERSION`) | (unset) | `22.12.0` |

- [ ] **Step 3: Trigger a redeploy from main and verify**

```bash
curl -fsS -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/patientvibes-main/deployments" | head -50
```

Watch for the new deployment's status. After it succeeds:

```bash
curl -fsS https://patientvibes.io/ | head -20
curl -fsS https://patientvibes.io/index.xml | head -10
```

Expected: HTML reflects new design; RSS XML is valid.

- [ ] **Step 4: Smoke-check live site in browser**

Open https://patientvibes.io/ — confirm sage-editorial design, real project data from agents catalog, RSS link in `<head>`, fonts load fast (Network tab shows woff2 requests, no Google Fonts).

---

### Task 17: Update CLAUDE.md and README.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`

- [ ] **Step 1: Rewrite the relevant sections of `CLAUDE.md`**

Find and rewrite these sections of `D:/patientvibes-main/CLAUDE.md`:

| Section | New content |
|---|---|
| "Stack" | Astro 6 + sage-editorial CSS (no Tailwind). Self-hosted fonts in `public/fonts/`. Build: `npm run build`. Node ≥22.12. |
| "Local development" | `npm install` once, then `npm run dev` (default `http://localhost:4321`). Build: `npm run build`. Preview: `npm run preview`. |
| "Editing conventions" | Pages live in `src/pages/`. Shared chrome in `src/layouts/BaseLayout.astro`. Components in `src/components/`. Notes in `src/content/notes/*.md`. **Tokens are the schema** — `stylelint` blocks raw hex outside `src/styles/tokens.css`. |
| "Cross-site contract" (NEW) | Homepage project rows + bench panel are bound at build time to `https://agents.patientvibes.io/api/projects.json`. Manifest of record lives in `patientvibes-agents-site/scripts/lib/manifest.mjs`. To add a project here: add the repo to that manifest, push agents-site, then push here (build-time fetch picks it up). Fallback fixture: `__fixtures__/projects.json`. |
| "Things to be careful about" | Update item 1: "The push triggers an immediate Cloudflare Pages **build** (no longer just a static upload)." Add: "Build pulls live data from agents.patientvibes.io/api/projects.json — confirm sibling site is up before pushing." |

- [ ] **Step 2: Rewrite `README.md`**

Replace the entire current README (it talks about Property Survey GIS / vibe-coding consulting — outdated). New short README:

```markdown
# patientvibes.io

Source for [patientvibes.io](https://patientvibes.io) — Chris Moore's personal site. A workshop for patient things: agents, the tools they need, and the harnesses that keep them honest.

## Stack

Astro 6 · self-hosted fonts (Instrument Serif / Inter / JetBrains Mono) · zero-Tailwind · sage-editorial design system in `src/styles/`. Deployed on Cloudflare Pages.

## Local

```bash
npm install
npm run dev    # http://localhost:4321
npm run build
```

## Catalog data

Project rows + bench panel pull from `https://agents.patientvibes.io/api/projects.json` at build time. The catalog itself lives in [`patientvibes-agents-site`](https://github.com/PatientVibes/patientvibes-agents-site).

## Notes

Markdown in `src/content/notes/*.md`. RSS at [`/index.xml`](https://patientvibes.io/index.xml).

See `CLAUDE.md` for operational details.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md README.md
git commit -m "docs: update CLAUDE.md and README.md for Astro stack + cross-site contract

Site is no longer single-file static; build is npm run build. Document
the projects.json fetch contract with agents-site and the stylelint
hex-color rule. README replaces the stale Property Survey GIS lore
with the current 'workshop for patient things' framing."
```

---

### Task 18: Final verification + push

- [ ] **Step 1: Run all checks**

```bash
cd D:/patientvibes-main
npm run lint
npm run build
```

Expected: both pass.

- [ ] **Step 2: Side-by-side compare with mockup**

```bash
npm run preview
```

Open `http://localhost:4321/` in one tab, `archive/mockups-2026-05-10/Homepage.html` in another. Differences expected:
- Project / bench data is real (not the mockup's placeholder copy)
- Notes section shows 1 real seed note (not 4 placeholders)
- Footer email is no longer a Cloudflare-protected hash (we control it now)

Everything else should match: typography, spacing, hover behavior, mobile breakpoint.

- [ ] **Step 3: APCA spot-check**

Use https://www.myndex.com/APCA/ or a browser extension. Test pairs:
- `--pv-mute` (#52635a) on `--pv-bg` (#eef0e8) → should pass AA for body
- `--pv-sage` (#3F6B54) on `--pv-bg` (#eef0e8) → reserve for ≥18px headings; should still pass
- `--pv-ink-2` (#22382c) on `--pv-paper` (#f7f8f1) → should pass AAA easily

- [ ] **Step 4: Push to main and verify deploy**

```bash
git push origin main
```

Watch Cloudflare Pages for the deploy. After ~1-2 minutes:

```bash
curl -fsS https://patientvibes.io/ | grep -o '<title>[^<]*</title>'
curl -fsS https://patientvibes.io/index.xml | head -5
curl -sI https://patientvibes.io/fonts/inter-500.woff2 | head -1
```

Expected:
- Title contains "patientvibes — index"
- RSS XML is valid
- Font 200 OK from `/fonts/`

---

## Self-Review Checklist (filled in after writing the plan)

- **Spec coverage:**
  1. Reorganize main project folder → Phase 1 + 7 (Tasks 1, 2, 3, 4, 5, 16, 17)
  2. Lock the tokens (verbatim copy + stylelint) → Task 2 (move) + Task 5 (stylelint)
  3. Self-host fonts → Task 3 (woff2 + @font-face) + Task 6 (preload)
  4. "Now" cadence (honest version) → Task 11 Step 4 (real bench from catalog OR static "Currently:" fallback)
  5. Auto-pull metadata (projects.json + 5-min cache) → Task 9 (endpoint) + Task 10 (fetch script) + Task 11 (bind)
  6. Clickability (whole row + section catalog link) → Task 7 (whole-row component) + Task 8 Step 2 (section header link)
  7. Photo (Kindle Scribe on kindle-pipeline detail page) → Task 14 + Task 15
  8. Accessibility sweep (APCA, --pv-mute fix) → Task 2 Step 2 + Task 18 Step 3
  9. RSS at build time → Task 12 (collection) + Task 13 (endpoint)

- **Placeholder scan:** No "TBD" or "implement later" items. Task 8 Step 1 has explicit "copy from lines X-Y" mechanical instructions, not "implement appropriately." Task 14 Step 3 keeps v2 rollout to other tools as an explicit out-of-scope follow-up.

- **Type consistency:** `Project` interface defined in Task 11. `displayStatus` returns `{state, label}`; same shape consumed by `ProjectRow` props (`status`, `statusLabel`). `bench.items[].state` uses `'shipped' | 'flight' | 'queued'` consistently between Task 7 (component def) and Task 11 Step 2 (data shaping).

- **Risk acknowledgements:**
  - The Cloudflare Pages settings change (Task 16) is the deploy-breaking moment. If push lands before settings flip, the site serves nothing useful. Mitigation: flip settings BEFORE pushing the Phase 1 commits, OR push them all at once and accept ~5 min of broken homepage during the first build.
  - Task 14's "v2 only for kindle-pipeline" is conditional code that adds drift between tool pages. Acceptable for one tool; flag for cleanup if more than 3 tool pages diverge.
