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

### DNS Setup (Critical — must match your CDN/registrar)

**GitHub Pages requires one of:**
- CNAME record pointing to `username.github.io`
- A records pointing to GitHub's IPs: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`

**Cloudflare users:** Set proxy mode to **DNS only** (grey cloud) for the A/CNAME records first. After GitHub validates the domain, you can enable Cloudflare proxy (orange cloud) — but Cloudflare's SSL must be set to "Flexible" or "Full" and the origin must be reachable.

**Common DNS patterns:**

| Provider | www (@) | Root (@) | Notes |
|----------|---------|----------|-------|
| Cloudflare | CNAME → `username.github.io` (DNS only) | CNAME → `username.github.io` (DNS only) | Proxy OFF until GitHub validates |
| Namecheap | CNAME → `username.github.io` | URL Redirect → `username.github.io` | Or use A records |
| 阿里云 | CNAME → `username.github.io` | A → GitHub IP | |

### After DNS Points to GitHub

1. Go to **GitHub repo → Settings → Pages → Custom domain** — enter your domain
2. Check **Enforce HTTPS** (GitHub auto-provisions Let's Encrypt cert, takes ~5 min)
3. Test: `curl -sI https://your-domain.com/` — should return HTTP 200

### SSL 525 Error (Cloudflare can't reach GitHub)

```
HTTP/2 525 SSL handshake failed
CF-RAY: xxxxx-ICN
server: cloudflare
```

**Cause:** Cloudflare is in proxy mode (orange cloud) but cannot establish SSL with GitHub Pages origin.

**Fix in order:**
1. **Immediately:** In Cloudflare DNS settings, set both `@` and `www` records to **DNS only** (click the orange cloud → grey)
2. Wait 2-3 min, test `https://your-domain.com/` — should now work over HTTPS
3. **Then** in GitHub Pages Settings → Custom domain — enter domain, enable HTTPS
4. GitHub provisions Let's Encrypt cert (takes 5 min)
5. **Only after** GitHub cert is active: re-enable Cloudflare proxy (orange cloud) if desired

**Root cause:** Cloudflare's default SSL mode ("Full" strict) requires the origin server to have a valid SSL cert. GitHub Pages handles SSL automatically on their end, but the handshake fails if Cloudflare tries to validate against an unconfigured origin.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pages not showing | Wait 2-5 min for deployment; check repo Settings → Pages |
| 404 on site | 1) Verify `index.html` is at repo root (not in subfolder) 2) Check Pages is enabled in repo Settings → Pages 3) If using "workflow" build_type but no workflow file exists, switch to "legacy" |
| Git push fails | Check token has `repo` scope |
| Wrong account in gh | `gh auth logout` then `gh auth login` with correct account, OR use token in URL |
| Pages status shows "building" but never completes | Delete Pages settings first, then re-enable with correct build_type |
| SSL 525 Cloudflare→GitHub Pages | After GitHub provisions cert, re-enable Cloudflare proxy but keep SSL at **"Full"** (not "Strict"). GitHub's Let's Encrypt rotation can fail Strict mode validation. |
| SSL 525 Cloudflare→Windows IIS | Server has no SSL cert for that domain. Either set Cloudflare SSL to **"Flexible"** (no server changes), OR install cert via IIS Manager/RDP/control panel. FTP alone cannot install SSL. |
| Google Search Console verification stuck | Use HTML meta tag method: user copies the `content` value from Google's meta tag, you paste it into `<head>` as `<meta name="google-site-verification" content="VALUE">`. Wait 2-3 min for Pages deploy, user clicks verify. |

**Quick fix for 404:** If site shows 404, disable Pages in Settings → Pages, wait 30s, then re-enable with `build_type: "legacy"`.

## SEO for Business Sites (Complete Checklist)

Add to `<head>` on **every page**:

```html
<!-- Core -->
<title>Page Title | Brand Name</title>
<meta name="description" content="Unique 155-char description for Google snippet">
<meta name="keywords" content="comma, separated, keywords">
<meta name="robots" content="index, follow">
<meta name="author" content="Company Name">

<!-- Canonical (prevents duplicate content penalties) -->
<link rel="canonical" href="https://your-domain.com/page.html">

<!-- Open Graph (social sharing: Facebook, LinkedIn, messaging apps) -->
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Description for social sharing (150-200 chars)">
<meta property="og:type" content="website">
<meta property="og:url" content="https://your-domain.com/page.html">
<meta property="og:image" content="https://your-domain.com/og-image.jpg">
<meta property="og:locale" content="en_US">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Description for Twitter/X sharing">
<meta name="twitter:image" content="https://your-domain.com/og-image.jpg">

<!-- Favicon & Theme -->
<link rel="icon" type="image/png" href="images/logo.png">
<meta name="theme-color" content="#1a1a2e">
```

**OG image specs:** 1200×630px minimum, 1.91:1 ratio preferred. Place at site root or `/images/`.

### JSON-LD Structured Data

Add inside `<head>` as `<script type="application/ld+json">`. Use `@graph` to bundle multiple types:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://your-domain.com/#organization",
      "name": "Company Name",
      "url": "https://your-domain.com/",
      "logo": "https://your-domain.com/images/logo.png",
      "description": "Company description",
      "foundingDate": "2010",
      "address": { "@type": "PostalAddress", "addressLocality": "City", "addressCountry": "CN" }
    },
    {
      "@type": "WebSite",
      "@id": "https://your-domain.com/#website",
      "url": "https://your-domain.com/",
      "name": "Site Name",
      "publisher": { "@id": "https://your-domain.com/#organization" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://your-domain.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "WebPage",
      "@id": "https://your-domain.com/#webpage",
      "url": "https://your-domain.com/",
      "name": "Page Title",
      "description": "Page description",
      "isPartOf": { "@id": "https://your-domain.com/#website" },
      "about": { "@id": "https://your-domain.com/#organization" }
    }
  ]
}
```

For e-commerce/product sites, add a `Product` node too with `brand`, `manufacturer`, and `offers` (price/currency).

### sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  <url>
    <loc>https://your-domain.com/</loc>
    <lastmod>2025-05-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

Always use the xsi:schemaLocation with the two URLs. Keep `lastmod` current — Google ignores stale dates.

### robots.txt

```
User-agent: *
Allow: /

Sitemap: https://your-domain.com/sitemap.xml
```

**Common mistakes:**
- `Disallow: /images/` — blocks crawlers from image files, hurts image search and OG image loading
- Forgetting the Sitemap: directive at the bottom
- Using `Disallow: /` without `Allow: /` on a separate line — ambiguous, some bots interpret as full block

### GitHub-Specific SEO Actions

- Set repo **Topics** in repo Settings (comma-separated tags shown in GitHub search)
- Keep `lastmod` in sitemap.xml updated — stale sitemaps signal abandoned sites
- Every page needs its own `<title>` and `<meta name="description">` — don't reuse the homepage meta across all pages

### Google Search Console Setup

After domain is live and verified:

1. **Add property** in [Search Console](https://search.google.com/search-console) — use "HTML tag" method (not file upload which GitHub Pages doesn't support)
2. **Get verification tag:** Google gives `<meta name="google-site-verification" content="XXXX">`
3. **User sends you the `content` value** (the long string after `content="`)
4. **You add to index.html** `<head>`: `<meta name="google-site-verification" content="THE_STRING">`
5. **Push → wait 2-3 min for Pages deploy**
6. **User clicks "Verify"** in Search Console
7. **Submit sitemap:** `https://your-domain.com/sitemap.xml` in Search Console → Sitemaps
8. **Request indexing** for the homepage via URL inspection tool

**SEO is site-dependent, not repo-dependent:** If you have both `githubtalk.github.io/repo` and `custom-domain.com`, they are separate Search Console properties. Set up the custom domain property for SEO tracking on the real domain.

## Support Files

- `templates/business-landing.html` — Starter business landing page template (copy & modify)
- `references/pages-api.md` — GitHub Pages API endpoints, build types, troubleshooting
- `references/product-site-verification.md` — **Critical:** How to cross-reference source product HTML pages to get correct product name→image mappings before building a product showcase site. Covers extraction commands, mapping tables, and common mistakes.
- `references/seo-checklist.md` — Detailed SEO implementation guide for GitHub Pages business sites
- `references/fork-to-satellite-site.md` — **Fork an existing repo to create a new domain's site** (e.g. mitalkcoin/sd-tractor → www.sadin-tractor.com). Covers DNS setup, search engine re-submission, and common pitfalls.
- `scripts/compress-images.js` — Node.js image compression script (Sharp) for product showcase sites

## Performance Optimization

GitHub Pages automatically serves Gzip-compressed text files. The main bottleneck on image-heavy sites is **image payload size**. Target: compress all images before deployment.

### Image Compression Workflow

```bash
# 1. Install dependencies
npm init -y
npm install --save-dev sharp

# 2. Create compress-images.js (see support files)

# 3. Run compression (JPEG 75% quality + progressive, PNG max compression)
node compress-images.js

# 4. Commit compressed images
git add images/
git commit -m "Compress product images for performance"
```

### Performance Head Tags

Add inside `<head>` before other resources:

```html
<!-- Preconnect to critical third-party domains -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="https://your-domain.github.io">

<!-- Preload the LCP (largest contentful paint) image -->
<link rel="preload" as="image" href="images/hero-product.jpg" fetchpriority="high">

<!-- Preload Google Fonts -->
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" crossorigin>
```

### Product Card Image Scaling

For product showcase grids, use `contain` with `max-width/max-height` so entire product images fit without cropping:

```css
.product-image {
  height: 180px;
  background: #f0f0f0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}
.product-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
```

**Pitfall: `object-fit: cover` on product images** crops the product, potentially hiding model numbers or important details. Use `contain` for product photos, `cover` only for decorative hero backgrounds.

### Image Format Priority

- Product photos: **JPEG 75%** quality, progressive scan (interlace)
- Diagrams/logos/transparencies: **PNG** with `compressionLevel: 9`
- **Never** use BMP or uncompressed TIFF
- Target: product card images under 100KB each

## Server-Agnostic SSL & Cloudflare Troubleshooting

### Identifying Server Type via FTP

FTP directory structure reveals the server OS:

| FTP root contents | Server type | Notes |
|-------------------|-------------|-------|
| `wwwroot/`, `aspnet_client/`, `.html` files | **Windows / IIS** | ASP.NET sites; SSL must be installed via IIS Manager or hosting panel |
| `public_html/`, `logs/`, `.htaccess` | **Linux / Apache** | SSL via `.htaccess` or hosting panel |
| `wwwroot/`, `databases/`, `logfiles/` | **Windows (hosting provider)** | No RDP/SSH — SSL via control panel only |

**Critical: FTP ≠ server admin.** FTP credentials only allow file transfer. SSL certificate installation requires:
- RDP/SSH access to the server
- Hosting control panel (Plesk, cPanel, websitepanel, etc.)
- OR hosting provider support to install cert on your behalf

If you only have FTP, you **cannot** install SSL certificates yourself. You must ask the hosting provider or use a Cloudflare "Flexible" SSL mode.

### Cloudflare SSL Modes Explained

| Mode | Visitor→CF | CF→Origin | Origin needs SSL cert? |
|------|-----------|-----------|----------------------|
| **Flexible** | HTTPS ✅ | HTTP | No |
| **Full** | HTTPS ✅ | HTTPS | Yes, but cert can be self-signed |
| **Strict** | HTTPS ✅ | HTTPS | Yes, and must be valid (not self-signed) |

### 525 Error: Cloudflare Can't Reach Origin

```
HTTP/2 525 SSL handshake failed
CF-RAY: xxxxx-ICN  
server: cloudflare
```

**Generic fix (Cloudflare → any origin):**
1. Cloudflare DNS → set `@` and `www` to **DNS only** (grey cloud)
2. Wait 2 min, test HTTPS
3. Configure origin SSL, then re-enable proxy

**Windows IIS server + Cloudflare — two paths:**

**Path A: Flexible SSL (5 min, no server changes)**
1. Cloudflare → SSL/TLS → set to **"Flexible"**
2. Done. No server cert needed.

**Path B: Install SSL on IIS (permanent, requires control panel or RDP)**
1. Get SSL cert (Let's Encrypt free, or Cloudflare Origin Certificate)
2. In IIS Manager → Server Certificates → import cert
3. In site bindings → add HTTPS binding with the cert
4. Force redirect HTTP→HTTPS in site settings
5. In Cloudflare SSL/TLS → set to **"Full"** or **"Strict"**

**How to diagnose the origin SSL issue:**
```bash
# Test origin SSL directly  
openssl s_client -connect origin-server.com:443

# Check if cert exists and is valid
echo | openssl s_client -connect origin-server.com:443 2>&1 | openssl x509 -noout -dates
```

If `no peer certificate available` or TLS alert 80 appears → origin has no SSL cert for that domain.

### GitHub Pages + Cloudflare (Distinct Case)

For **GitHub Pages** (not self-hosted), the procedure is different:
1. Set Cloudflare DNS records to **DNS only** (grey cloud) first
2. GitHub repo → Settings → Pages → Custom domain
3. GitHub auto-provisions Let's Encrypt cert
4. Wait 5 min, then optionally re-enable Cloudflare proxy
5. If 525 persists after re-enabling: Cloudflare SSL → **"Full"** (not "Strict") for GitHub Pages

**Do NOT use Cloudflare "Strict" mode with GitHub Pages** — GitHub's Let's Encrypt cert is valid but Cloudflare Strict mode may fail during cert rotation.

## Performance Checklist

Widen content area to reduce side whitespace:

```css
.container { max-width: 1400px; margin: 0 auto; padding: 0 16px; }
```

### Performance Checklist

- [ ] All images compressed (target <100KB per card image)
- [ ] `preconnect` for Google Fonts in `<head>`
- [ ] `fetchpriority="high"` on LCP image
- [ ] `loading="lazy"` on below-fold images
- [ ] Product card images use `object-fit: contain`
- [ ] Container widened to max-width 1400px
- [ ] Test with Lighthouse → Performance score target: 80+