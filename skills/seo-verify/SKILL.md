---
name: seo-verify
description: Search engine site verification (Google, Baidu, Bing) + sitemap optimization + domain binding workflow. Covers GitHub Pages, Windows shared hosting with FTP, and Cloudflare DNS setups. Triggers on requests like "verify site on Google", "Baidu site verification", "submit sitemap", "Google SEO", "bind domain to GitHub Pages".
version: 1.0.0
metadata:
  hermes:
    tags: [seo, search-engine, verification]
    related_skills: [github-pages-site, domain]
---

# SEO Site Verification & Sitemap

## Overview

Verify ownership of a website with Google, Baidu, and Bing search engines, then submit sitemaps for indexing. Handles both GitHub Pages and Windows shared hosting (FTP-only, no SSH/RDP) with Cloudflare CDN.

## Prerequisites

- FTP credentials (for Windows shared hosting)
- Cloudflare access (for DNS/domain management)
- Google account (Search Console) / Baidu account (zhanzhang.baidu.com)

---

## Workflow

### 1. Choose Verification Method

| Method | Best For | Limitations |
|--------|----------|-------------|
| **HTML tag** | Any site | Must be able to edit `<head>` |
| **Cloudflare授权** | Cloudflare-proxied sites | Only works for Google |
| **File upload** | FTP-accessible sites | Baidu only accepts .txt/.html |
| **CNAME** | Sites with Cloudflare blocking bots | Most reliable for Baidu |

### 2. Apply Verification Tag

**GitHub Pages** (any HTML site):
```bash
# Find the <head> tag in index.html, insert meta tag right after <title>
# Example: Google verification
sed -i 's|<title>|<meta name="google-site-verification" content="XXXXX" />\n<title>|' index.html
git add index.html && git commit -m "Add search engine verification" && git push
```

**Windows Shared Hosting (FTP)**:
```bash
# Download current index.html, inject meta tag, re-upload via FTP
curl -s --connect-timeout 15 -u "USER:PASS" "ftp://HOST/wwwroot/index.html" -o /tmp/index.html
sed -i 's|<title>|<meta name="google-site-verification" content="XXXXX" />\n<title>|' /tmp/index.html
curl -s --connect-timeout 15 -u "USER:PASS" -T /tmp/index.html "ftp://HOST/wwwroot/index.html"
```

**Baidu file verification (FTP)** — Note: Baidu wants the raw verification CODE as the file content, NOT HTML:
```bash
# Create file with ONLY the verification code string (no HTML wrapper)
echo -n "codeva-XXXXX" > baidu_verify_codeva-XXXXX.html
curl -u "USER:PASS" -T baidu_verify_codeva-XXXXX.html "ftp://HOST/wwwroot/"
```

### 3. Verify Access

```bash
# Confirm tag is live (allow 2-3 min for GitHub Pages rebuild)
curl -s "https://example.com/" | grep "verification_code"

# Check Baidu file
curl -s "https://example.com/baidu_verify_codeva-XXXXX.html"
# Should return: codeva-XXXXX (plain text, no HTML)
```

### 4. Optimize Sitemap

Sitemap checklist:
- [ ] URLs use `https://` (not `http://`)
- [ ] Priority reflects page importance (homepage=1.0, products=0.9, news=0.7, about=0.8)
- [ ] `changefreq` is realistic (homepage=weekly, products=weekly, about=monthly)
- [ ] No dead links (.asp, .doc, verification files, backend files)
- [ ] Includes `xmlns:image` for image sitemap

**Deploy sitemap to Windows shared hosting via FTP:**
```bash
# Create optimized sitemap locally, then:
curl -u "USER:PASS" -T /tmp/sitemap.xml "ftp://HOST/wwwroot/sitemap.xml"
# Verify:
curl -s "https://example.com/sitemap.xml" | head -5
```

### 5. Submit to Search Engines

**Google Search Console** → Sitemaps → Submit:
```
https://example.com/sitemap.xml
```

**Baidu zhanzhang.baidu.com** → 链接提交 → sitemap:
```
https://example.com/sitemap.xml
```

Or use manual URL submission for faster initial crawl.

---

## Troubleshooting

### Baidu "无法连接到您网站的服务器"
**Cause:** Baidu bot blocked by Cloudflare bot protection.

**Fixes (in order):**
1. Set Cloudflare Security to **Low** or **Medium**
2. Disable **Bot Fight Mode** in Cloudflare → Security → Bots
3. Use CNAME verification (bypasses Cloudflare proxy entirely)

### Cloudflare 525 SSL Handshake Error
**Cause:** Server has no SSL cert, Cloudflare can't establish HTTPS connection.

**Fix (no server access):**
Cloudflare → SSL/TLS → Mode: **Flexible** (CF→server uses HTTP)

This is the correct fix for shared Windows hosting with no dedicated SSL.

### Google Site Verification Fails
**Options:** HTML tag (edit head), Cloudflare授权 (fastest if already verified), DNS CNAME (most reliable)

### HTTP 525 / 526 Errors
Means Cloudflare can't reach origin server with SSL. Fix by setting Flexible mode OR installing SSL on origin.

---

## References

- `references/baidu-verify-ftp.md` — Baidu verification on Windows shared hosting (FTP upload, raw text file)
- `references/sitemap-template.xml` — Optimized sitemap template with priorities