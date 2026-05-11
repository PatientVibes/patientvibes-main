# CLAUDE.md

Guidance for Claude Code working in this repo. Read first before any non-trivial change.

## What this repo is

Source for **[patientvibes.io](https://patientvibes.io)** — Chris Moore's portfolio for AI agent development & "vibe coding" consulting. Astro 6 site in the "Sage Editorial" design language. Homepage at `src/pages/index.astro`; project rows and bench panel are bound at build time to the public catalog at [agents.patientvibes.io/api/projects.json](https://agents.patientvibes.io/api/projects.json).

Repo: [`PatientVibes/patientvibes-main`](https://github.com/PatientVibes/patientvibes-main). Local clone: `D:/patientvibes-main/`.

## Stack

- **Astro 6** — matches the sibling `patientvibes-agents-site` stack. Build: `npm run build`. Output: `dist/`.
- **No Tailwind here.** The "Sage Editorial" design system lives in `src/styles/` (`tokens.css`, `base.css`, `components.css`) — vendored verbatim into `patientvibes-agents-site` for consistency.
- **Self-hosted fonts** in `public/fonts/` (Instrument Serif, Inter, JetBrains Mono — woff2, latin subset, font-display: swap). No Google Fonts CDN.
- **Tokens are the schema.** `stylelint` enforces `color-no-hex` outside `src/styles/tokens.css` — PRs that introduce a one-off hex fail lint. Run: `npm run lint`.
- **Node ≥22.12.** `package-lock.json` is committed; Cloudflare Pages uses `npm ci`.

## Deploy

- **Hosting:** Cloudflare Pages, project name `patientvibes-main`. Production branch: `main`. Build command: `npm run build`. Output dir: `dist`. `NODE_VERSION=22.12` env var set for both production and preview. Auto-deploys on push to `main` via the "Cloudflare Workers and Pages" GitHub App (must be installed on the `PatientVibes` GitHub account — see the lessons section for why this matters). The webhook fires `deployment_trigger.type: github:push`; if a recent deploy shows `ad_hoc` for a normal commit-driven build, the App grant has been removed.
- **DNS:** `patientvibes.io` is a CNAME (proxied) → `patientvibes-main.pages.dev` in zone `patientvibes.io`. Cloudflare auto-manages TLS.
- **Subdomains in the same zone:** `agents.patientvibes.io` (separate Pages project — see below), `plaza.patientvibes.io`, `nextcloud.patientvibes.io`, `paperless.patientvibes.io`, `stirling.patientvibes.io`, `pokemon.patientvibes.io`. Don't touch their CNAMEs.
- **History:** This project was a Cloudflare Pages "direct upload" project from 2025-08-05 to 2026-05-10. Last deploy before recreation was 2025-08-06 (commit `1ef38e5a`); the live site was 9 months stale relative to this repo until 2026-05-10. On 2026-05-10 the project was recreated as a git-connected Pages project (Cloudflare returns error 8000069 on PATCH for direct-upload sources, so the only path was delete + recreate, with the custom domain detached/re-attached around the recreation).

To verify a push deployed: https://dash.cloudflare.com → Workers & Pages → patientvibes-main → Deployments. Or via API:

```bash
curl -fsS -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/patientvibes-main/deployments" | head
```

## Local development

```bash
cd D:/patientvibes-main
npm install     # first time only
npm run dev     # http://localhost:4321
npm run build   # writes dist/
npm run preview # serves dist/ on http://localhost:4321
npm run lint    # stylelint over src/**/*.css
```

`npm run build` runs `prebuild` first (fetches `https://agents.patientvibes.io/api/projects.json` into `.cache/projects.json`, falls back to `__fixtures__/projects.json` on network failure). The fixture is committed as the safety net.

## Editing conventions

- **Pages live in `src/pages/`.** `index.astro` is the homepage; `index.xml.ts` is the RSS endpoint. Routed pages get one file each.
- **Shared chrome lives in `src/layouts/BaseLayout.astro`** (font preloads, favicon, RSS autodiscovery, `<head>` boilerplate).
- **Components in `src/components/`** — `ProjectRow.astro`, `NoteRow.astro`, `BenchPanel.astro`, `Terminal.astro`. Page-local CSS for the homepage stays inline in `index.astro`'s `<style>` block (`.hp-*` classes); design-system styles are global (`.pv-*` classes from `src/styles/`).
- **Notes are markdown** in `src/content/notes/*.md` with Zod-validated frontmatter (title, pubDate, summary, readMin, draft). Schema in `src/content.config.ts`. RSS at `/index.xml` reads from this collection.
- **Tokens are the schema.** Add a new color? It goes in `src/styles/tokens.css` first, then everything else uses `var(--pv-*)`. The `color-no-hex` lint rule allowlists only `tokens.css`.
- **Mobile responsive.** The homepage uses media queries below 720px (collapses hero/now to single column, drops project date column). Test mobile when changing layout.

## Cross-site contract

The homepage's project rows + bench panel are bound at build time to `https://agents.patientvibes.io/api/projects.json`. The catalog manifest of record lives in `patientvibes-agents-site/scripts/lib/manifest.mjs`.

To add a project to the homepage:
1. Add the repo entry to `patientvibes-agents-site/scripts/lib/manifest.mjs`
2. Push agents-site (Cloudflare Pages rebuilds; `pull-readmes` runs and the new tool gets a content collection entry; `/api/projects.json` reflects it within ~30s)
3. Push patientvibes-main (next build's `prebuild` hook fetches the updated JSON; homepage rebuilds)

Cache: 5-min edge cache on `/api/projects.json` (`s-maxage=300`). README edits propagate the same day. CORS is open (`*`) — public catalog data.

Fallback: if the build can't reach the endpoint, it uses `__fixtures__/projects.json` (committed) so a brief sibling-site outage doesn't break a deploy. The fixture should be refreshed periodically — `curl -fsS https://agents.patientvibes.io/api/projects.json > __fixtures__/projects.json && git add __fixtures__/projects.json` when convenient.

Tokens are vendored into both repos (`src/styles/tokens.css` in each). When you bump a token, edit both files in lockstep — there's no shared package.

## Related sites and repos

| Site | Repo | Stack | Hosting |
|---|---|---|---|
| **patientvibes.io** | `patientvibes-main` (this repo) | Astro 6 (Sage Editorial design system, no Tailwind) | Cloudflare Pages (git-connected) |
| **agents.patientvibes.io** | [`patientvibes-agents-site`](https://github.com/PatientVibes/patientvibes-agents-site) | Astro 6 + Tailwind 4 (`@tailwindcss/vite`) + content collections | Cloudflare Pages (git-connected) |
| **chrispaulmoore.com** | [`chrispaulmoore-website`](https://github.com/PatientVibes/chrispaulmoore-website) | Plain HTML + Cloudflare Worker (`comments-system`) | GitHub Pages (apex), Worker (comments subdomain) |

Both adjacent sites have nav links pointing back to `agents.patientvibes.io`. If you change the agents subdomain or rename the project, update the nav in both sibling repos.

The `agents.patientvibes.io` site auto-pulls READMEs from these 10 public sibling agent-* repos under github.com/PatientVibes:

- `agent-skills` (Claude Code plugin marketplace)
- `agent-tool-pr-reviewer`, `agent-tool-pdf-builder`, `agent-tool-marker-cleanup`, `agent-tool-figure-scanner`, `agent-tool-prose-quality`, `agent-tool-scrape-sources`, `agent-tool-llm-proofreader`, `agent-tool-book-builder` (8 tools)
- `agent-harness-kindle-pipeline` (1 harness)

Catalog of record for those: [`PatientVibes/ai-agents`](https://github.com/PatientVibes/ai-agents) (private). When the agents-site adds new entries, the manifest in `patientvibes-agents-site/scripts/lib/manifest.mjs` and `D:/ai-agents/README.md` both need updates.

## Cloudflare account context

- **Account:** Chris.paul.moore@gmail.com's Account
- **Account ID:** `aff9def13e8669be102b08b996491367`
- **Zone for `patientvibes.io`:** zone tag `33537d91eac78d628268ece5c6d8e5d0`
- **Pages project ID:** `8648f476-19de-41a9-81ad-b3e9aca3afd4` (created 2026-05-10 during the direct-upload → git-connected migration)

## GitHub account context

- **Owner:** `PatientVibes` — note this is a **GitHub user account, NOT an organization**. Use `/users/PatientVibes/repos` API endpoint, not `/orgs/...` (404s for users).
- **Owner ID:** `203562747`
- **This repo ID:** `1032781237`

## Secrets and tokens

This repo has no GitHub Actions secrets and no env file. All operational tokens live in 1Password's "Service Account" vault (`jkpi6kbttqrirancazuclw2tna`):

| 1P item | Item ID | Purpose |
|---|---|---|
| `Cloudflare - All API Token` | `3vlhufs6givjkmkbtms4drjcpm` | Broad CF token. Field `credential`. Used for ad-hoc admin (project create/delete/PATCH, DNS edits). Rotated 2026-05-10. |
| `cloudflare - patientvibes - pages` | `3uqk7spvqx4wyfkktbvyn7ere4` | Narrower CF token (Pages: Edit only — does NOT cover project create or trigger deploy in practice). Field `credential`. Account ID stored in custom field `Account ID`. |
| `cloudflare-pages-agents-site-builds` | `lwyhtpgw7dazvr4ra62efgpxwq` | GitHub fine-grained PAT, `contents:read` on the 10 agent-* repos. Field `password`. Used by the Cloudflare build for `agents.patientvibes.io` to bypass GitHub anonymous rate limits. |

Retrieval pattern (via the `op` CLI):

```bash
# Set the service-account token from PowerShell SecretManagement
OP_SERVICE_ACCOUNT_TOKEN=$(pwsh -NoProfile -NonInteractive -Command 'Get-Secret -Name OP_SERVICE_ACCOUNT_TOKEN -AsPlainText' | tr -d '\r\n')
export OP_SERVICE_ACCOUNT_TOKEN

# Pull a specific token (note: API_CREDENTIAL items have field "credential", LOGIN items have field "password")
CF_API_TOKEN=$(op read "op://jkpi6kbttqrirancazuclw2tna/3vlhufs6givjkmkbtms4drjcpm/credential")
```

`OP_SERVICE_ACCOUNT_TOKEN` is gated by an autoMode rule in `~/.claude/settings.json` that scopes it specifically to `op` CLI usage and forbids printing the token to chat. See `~/.claude/projects/d--ai-agents/memory/reference_op_service_account_token.md`.

## Things to be careful about

1. **The push triggers an immediate Cloudflare Pages BUILD (not a static upload).** No staging branch, no PR-based preview gate. Run `npm run build` locally first; preview with `npm run preview` and click through. Build pulls live data from `agents.patientvibes.io/api/projects.json` — verify the sibling site is up before pushing if you've made changes that depend on the latest catalog data.
2. **No external font CDNs.** Fonts are self-hosted in `public/fonts/` (Instrument Serif, Inter, JetBrains Mono). Don't reach for Google Fonts or any third-party stylesheet without explicit reason — adds a DNS round-trip and a privacy footprint, and breaks the "self-contained build" property.
3. **The nav link to `agents.patientvibes.io` is load-bearing for cross-site discoverability.** If you renumber sections or restructure the nav, keep the link pointing at the agents subdomain.
4. **Both repos vendor the design system.** `src/styles/tokens.css`, `base.css`, `components.css` are duplicated in `patientvibes-main` and `patientvibes-agents-site`. There's no shared npm package — by design, since this is a 2-repo personal portfolio. Token bumps require a coordinated PR in both repos. If you find drift, the canonical source is whichever was edited most recently — check git log on both.

## Common operations

**Edit and deploy a copy change** (2 minutes):

```bash
cd D:/patientvibes-main
# edit src/pages/index.astro (or src/components/*.astro)
npm run build && npm run preview   # sanity-check at http://localhost:4321
git add -A
git commit -m "feat: <what changed>"
git push origin main
# wait ~60-90s for Cloudflare Pages build, then:
curl -fsS https://patientvibes.io | head -1   # should reflect change
```

**Add a new section to the homepage** (5 minutes): edit `src/pages/index.astro`. Add an `<a href="#new">` inside the `<nav class="hp-nav__meta">` block, then add a new `<section id="new" class="hp-sec">...</section>` near the existing sections. Match the existing `.hp-sec` / `.hp-sec__head` / `.hp-sec__title` / `.hp-sec__num` patterns and increment the section number prefix (`01 · Harnesses` → `02 · Tools` → etc.). Page-local CSS lives in the `<style is:global>` block at the bottom of the same file.

**Refresh the agents-subdomain link in the nav**: search for `agents.patientvibes.io` in `src/pages/index.astro` (it appears in `.hp-nav__meta` and in the hero intro paragraph). Update both if the subdomain ever changes.

**Roll back a deploy**: in the Cloudflare Pages dashboard, Deployments tab → pick a previous deployment → "Retry deployment" or "Roll back to this deployment". Or push a revert commit (preferred — keeps git as source of truth).

## When you're stuck

- Site is 503 or 1016: check Cloudflare Pages dashboard for the latest deployment status. If the deployment shows an error, look at the build log. Most plausible failure mode is "no files found" — empty branch or wrong build output dir.
- Site serves but content is stale: the CDN cache for `patientvibes.io` is set to `Cache-Control: public, max-age=0, must-revalidate` so it shouldn't cache. Force-fresh fetch: `curl -H "Cache-Control: no-cache" https://patientvibes.io/?nocache=$(date +%s)`.
- DNS not resolving: check `https://api.cloudflare.com/client/v4/zones/33537d91eac78d628268ece5c6d8e5d0/dns_records?name=patientvibes.io` (with auth). The CNAME id at time of writing is `fe228e53c6549c7225328bc0da773709` and content `patientvibes-main.pages.dev`.

## Lessons captured (2026-05-10 redesign + CF migration)

- **Cloudflare can't convert direct-upload Pages projects to git-connected.** `PATCH /pages/projects/<name>` with a `source` field returns error 8000069 ("You cannot update the `source` object in a Direct Uploads project"). Delete + recreate is the only path. Detach the custom domain first (`DELETE /domains/<name>`), then delete the project, then create the new project with `source: {type: github, ...}`, then re-attach the custom domain.
- **Cloudflare's "Pages: Edit" permission template is misleading.** It doesn't include the `POST /pages/projects` (create) endpoint and seems not to cover deployment-trigger reliably. For a script that needs to create projects or trigger deployments, use a token with `Account: Account Settings: Edit` + `Account: Cloudflare Pages: Edit` together (or fall back to a broad token with caveats).
- **`PatientVibes` is a GitHub user, not an org.** All API calls that take an "owner" parameter must use the `/users/{owner}/repos` endpoint shape; `/orgs/{owner}/...` 404s.
- **A new CF Pages project created via API does NOT inherit `build_command` / `destination_dir` / `env_vars` from any previous project of the same name.** Defaults are empty. If the source repo needs a build step (Astro, Next, etc.), set them explicitly via `PATCH /pages/projects/<name>` right after creation — otherwise the first deploy succeeds at "build" and "deploy" stages but serves the repo root (no `index.html` → 404). Required minimum for this repo: `build_command="npm run build"`, `destination_dir="dist"`, `deployment_configs.{production,preview}.env_vars.NODE_VERSION=22.12`.
- **CF Pages "git-connected" status is not the same as "the webhook is working".** The API will accept `source.type: github` + `deployments_enabled: true` regardless of whether the "Cloudflare Workers and Pages" GitHub App is actually installed on the target account. The project will *look* git-connected in `GET /pages/projects/<name>` but pushes will not auto-deploy. Test: push a trivial commit and check `deployment_trigger.type` on the resulting deploy via `GET /pages/projects/<name>/deployments?per_page=1`. `github:push` = healthy. `ad_hoc` (for a commit you just pushed) = the App grant is missing — go to https://github.com/apps/cloudflare-workers-and-pages and grant repo access for `PatientVibes`.
- **Astro's scoped `<style>` blocks don't reach into imported components.** If a page-local CSS selector targets an element rendered by a child component (e.g. the homepage's `.hp-proj` / `.hp-note` / `.hp-now__list` classes target elements emitted by `ProjectRow.astro` / `NoteRow.astro` / `BenchPanel.astro`), the page's `<style>` block must be marked `is:global` or every component's elements get a different `data-astro-cid-*` scope hash and the selectors silently no-op. The build does NOT warn about this. Visible symptom: the page renders structurally but every project row is unstyled (default underlined link stack).
