# CLAUDE.md

Guidance for Claude Code working in this repo. Read first before any non-trivial change.

## What this repo is

Source for **[patientvibes.io](https://patientvibes.io)** — Chris Moore's portfolio for AI agent development & "vibe coding" consulting. Single static page (`index.html`, ~633 lines, ~21 KB) with all CSS/JS inlined. No build step.

Repo: [`PatientVibes/patientvibes-main`](https://github.com/PatientVibes/patientvibes-main). Local clone: `D:/patientvibes-main/`.

## Stack

- **Plain HTML** — no framework, no build, no bundler. CSS and JS are inlined in `<style>` / `<script>` blocks inside `index.html`.
- **No package.json**, no `node_modules`. Local "preview" is `start index.html` (Windows) or any browser.
- **Self-contained.** Edit `index.html`, push, deploy.

This is *not* Astro and not the same stack as the related sites — see "Related sites" below.

## Deploy

- **Hosting:** Cloudflare Pages, project name `patientvibes-main`. Production branch: `main`. Build command: empty. Output dir: empty (root). Auto-deploys on push to `main`.
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
start index.html      # Windows; opens in default browser
# or
python -m http.server 8000  # then http://localhost:8000
```

The site has no JS-driven routing, no API calls. What you see on disk is what serves.

## Editing conventions

- **One file.** All edits go in `index.html`. CSS in the `<style>` block (top of `<head>`), JS in inline `<script>` tags.
- **Sections are anchor-routed.** The nav uses `#about`, `#skills`, `#portfolio`, `#approach`, `#contact` anchors plus an external `https://agents.patientvibes.io` link. Add new sections by adding a `<section id="...">` and a corresponding nav `<a href="#...">`.
- **Mobile responsive.** Existing media queries hide `.nav-links` and adjust layout below ~768px. Test mobile when changing layout.
- **No external CSS/JS dependencies in v1.** Adding any (e.g., a fonts CDN, an analytics tag) is a meaningful change worth committing on its own with the rationale.

## Related sites and repos

| Site | Repo | Stack | Hosting |
|---|---|---|---|
| **patientvibes.io** | `patientvibes-main` (this repo) | Plain HTML | Cloudflare Pages (git-connected) |
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

1. **The push triggers an immediate production deploy.** No staging branch, no PR-based preview gate. Run the change locally first; sanity-check that the `index.html` opens cleanly in a browser before pushing.
2. **CSS/JS is inlined.** Don't reach for an external `<link rel="stylesheet">` or `<script src>` without explicit reason — keeps the deploy single-artifact and breaks-once means breaks-totally.
3. **The nav link to `agents.patientvibes.io` is load-bearing for cross-site discoverability.** If you renumber sections or restructure the nav, keep the link pointing at the agents subdomain.
4. **Don't move this site under a build framework casually.** It's been single-file static HTML since inception; switching to Astro/Next/etc. is a real migration that needs a spec — and the Cloudflare Pages project's build command would need to be updated to match. The user's build pattern for catalogs lives in `patientvibes-agents-site` (Astro); this repo stays plain.

## Common operations

**Edit and deploy a copy change** (1 minute):

```bash
cd D:/patientvibes-main
# edit index.html
git add index.html
git commit -m "feat: <what changed>"
git push origin main
# wait ~30s, then:
curl -fsS https://patientvibes.io | head -1   # should reflect change
```

**Add a new section** (5 minutes): edit the `<nav class="nav-links">` block to add an `<a href="#new">`, then add `<section id="new" class="section section-white">...</section>` near the existing sections (~line 433+). Match the existing class patterns.

**Refresh the agents-subdomain link in the nav**: search for `agents.patientvibes.io` in `index.html` (currently line in `nav-links` block). Update the URL there if the subdomain ever changes.

**Roll back a deploy**: in the Cloudflare Pages dashboard, Deployments tab → pick a previous deployment → "Retry deployment" or "Roll back to this deployment". Or push a revert commit (preferred — keeps git as source of truth).

## When you're stuck

- Site is 503 or 1016: check Cloudflare Pages dashboard for the latest deployment status. If the deployment shows an error, look at the build log. Most plausible failure mode is "no files found" — empty branch or wrong build output dir.
- Site serves but content is stale: the CDN cache for `patientvibes.io` is set to `Cache-Control: public, max-age=0, must-revalidate` so it shouldn't cache. Force-fresh fetch: `curl -H "Cache-Control: no-cache" https://patientvibes.io/?nocache=$(date +%s)`.
- DNS not resolving: check `https://api.cloudflare.com/client/v4/zones/33537d91eac78d628268ece5c6d8e5d0/dns_records?name=patientvibes.io` (with auth). The CNAME id at time of writing is `fe228e53c6549c7225328bc0da773709` and content `patientvibes-main.pages.dev`.

## Lessons captured (2026-05-10 recreation)

- **Cloudflare can't convert direct-upload Pages projects to git-connected.** `PATCH /pages/projects/<name>` with a `source` field returns error 8000069 ("You cannot update the `source` object in a Direct Uploads project"). Delete + recreate is the only path. Detach the custom domain first (`DELETE /domains/<name>`), then delete the project, then create the new project with `source: {type: github, ...}`, then re-attach the custom domain.
- **Cloudflare's "Pages: Edit" permission template is misleading.** It doesn't include the `POST /pages/projects` (create) endpoint and seems not to cover deployment-trigger reliably. For a script that needs to create projects or trigger deployments, use a token with `Account: Account Settings: Edit` + `Account: Cloudflare Pages: Edit` together (or fall back to a broad token with caveats).
- **`PatientVibes` is a GitHub user, not an org.** All API calls that take an "owner" parameter must use the `/users/{owner}/repos` endpoint shape; `/orgs/{owner}/...` 404s.
