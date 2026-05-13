---
name: github-pages-site
description: Build and deploy a static website (business landing page, portfolio, docs) to GitHub Pages. Covers repo creation, content deployment, and Pages enabling via GitHub API.
trigger: build a website on github, github pages for business, deploy static site to github, create landing page on github
---

# GitHub Pages Static Site

Deploy a static website (business landing page, portfolio, product showcase) to GitHub Pages.

## Workflow

### Step 1: Create Repository

```bash
# Using gh CLI (must be authenticated with target account)
gh repo create owner/repo-name --public --description "Site description" --clone=false
```

### Step 2: Clone and Initialize

```bash
# If repo already exists locally (e.g. from prior work):
cd existing-dir
git init
git remote add origin https://TOKEN@github.com/owner/repo-name.git

# If fresh clone:
git clone https://TOKEN@github.com/owner/repo-name.git
cd repo-name
```

### Step 3: Add Content

- `index.html` — main page (mobile-responsive recommended)
- `README.md` — repo documentation
- `/images/` — product photos, assets

### Step 4: Push to GitHub

```bash
git add .
git commit -m "Initial site content"
git push origin master
```

### Step 5: Enable GitHub Pages (API)

```bash
# IMPORTANT: For simple static HTML sites, use build_type "legacy" (no GitHub Actions needed)
# Only use "workflow" if you have a .github/workflows/pages.yml file

# For static HTML/CSS/JS sites (recommended):
curl -s -X POST \
  -H "Authorization: token TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/owner/repo-name/pages \
  -d '{"build_type":"legacy","source":{"branch":"master","path":"/"}}'

# For sites requiring build (Jekyll, Hugo, etc.) - needs workflow file first:
# Create .github/workflows/pages.yml, then use:
curl -s -X POST \
  -H "Authorization: token TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/owner/repo-name/pages \
  -d '{"build_type":"workflow"}'
```

Response includes `"html_url": "https://owner.github.io/repo-name/"`.

## Token Handling (Critical)

- **Building for a different account than your default gh auth?** The gh CLI uses your default auth account. If you need to push to a different account's repo, pass the token explicitly in the git remote URL: `https://TOKEN@github.com/owner/repo.git`
- **Creating repo for different account:** Use `gh repo create` with `--token` flag or use API directly with that account's PAT
- **gh CLI default account check:** `gh auth status`
- **If gh is logged to wrong account and you need the right one:** Either logout/login (`gh auth logout` && `gh auth login`) OR just use token-in-URL method for all operations

## Business Site Template Sections

For a B2B/export business landing page:
- **Hero** — value proposition + CTA buttons
- **Products** — product cards with specs/features
- **Specifications** — comparison table
- **Why Choose Us** — trust signals (years experience, countries served, certifications)
- **Contact** — name, phone, email, WhatsApp, address
- **Footer** — links, copyright

## Custom Domain (Optional)

After Pages is live, add custom domain in repo Settings → Pages → Custom domain. Requires:
- Domain DNS pointing to GitHub IPs
- Optional HTTPS enforcement

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pages not showing | Wait 2-5 min for deployment; check repo Settings → Pages |
| 404 on site | 1) Verify `index.html` is at repo root (not in subfolder) 2) Check Pages is enabled in repo Settings → Pages 3) If using "workflow" build_type but no workflow file exists, switch to "legacy" |
| Git push fails | Check token has `repo` scope |
| Wrong account in gh | `gh auth logout` then `gh auth login` with correct account, OR use token in URL |
| Pages status shows "building" but never completes | Delete Pages settings first, then re-enable with correct build_type |

**Quick fix for 404:** If site shows 404, disable Pages in Settings → Pages, wait 30s, then re-enable with `build_type: "legacy"`.

## SEO for Business Sites

Add to `<head>`:
```html
<meta name="description" content="Your site description for Google">
<meta name="keywords" content="tractor, agricultural, export, china">
<link rel="canonical" href="https://your-domain.com">
```

GitHub repo topics also help discoverability: set via API or repo Settings.

## SEO for Business Sites

Add to `<head>` for each page:
```html
<meta name="description" content="Your site description for Google (155 chars max)">
<meta name="keywords" content="tractor, agricultural, export, china, farm machinery">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://your-domain.com/page.html">
```

Open Graph (for social sharing):
```html
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Description for social sharing">
<meta property="og:type" content="website">
<meta property="og:url" content="https://your-domain.com/page.html">
```

Additional SEO files:
- `sitemap.xml` — list all pages for Google
- `robots.txt` — control crawler access

## Support Files

- `templates/business-landing.html` — Starter business landing page template (copy & modify)
- `references/pages-api.md` — GitHub Pages API endpoints, build types, troubleshooting