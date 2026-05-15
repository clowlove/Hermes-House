---
name: website-seo
description: Domain binding, SSL setup, Cloudflare DNS, search engine submission, sitemap management, and Windows shared hosting FTP workflows
triggers:
  - bind domain to github pages
  - cloudflare ssl 525 error
  - submit sitemap to google
  - baidu verification
  - yandex verification
---

# Website SEO & Administration

## Domain Binding (GitHub Pages → Custom Domain)

### GitHub Settings
1. Repository → Settings → Pages → Custom domain: `www.example.com`
2. Do NOT check "Enforce HTTPS" until after DNS verification completes

### Cloudflare DNS
| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | www | `githubtalk.github.io` | DNS only (gray) during verification |

**Critical**: Keep DNS-only (gray cloud) while GitHub validates domain ownership. After GitHub issues HTTPS cert, re-enable proxy (orange cloud).

### Why Enforce HTTPS Is Optional with Cloudflare
Cloudflare Flexible/Full SSL already handles HTTP→HTTPS redirect at CDN level. GitHub's "Enforce HTTPS" does the same. If `https://www.example.com` works in browser, the checkbox is cosmetic.

---

## Cloudflare SSL 525 Error

**Symptom**: `HTTP 525 - SSL handshake failed`

**Root cause**: Origin server has no valid SSL certificate for the domain

**Quick fix**:
- Cloudflare → SSL/TLS → Mode: **Flexible**
- Visitor → Cloudflare: HTTPS ✅
- Cloudflare → Origin: HTTP (no cert needed) ✅

**Permanent fix**: Install Let's Encrypt on origin server (requires RDP/SSH access)

---

## Sitemap After Domain Change

**Problem**: Switched custom domain but sitemap.xml still has old URLs like `githubtalk.github.io/shengtuo-tractor/`

**Fix**:
1. Update `sitemap.xml` in the GitHub repository with new domain URLs
2. GitHub Pages automatically redirects `/sitemap.xml` from parked URL to custom domain
3. Search Console "Couldn't fetch" = CDN cache delay, refreshes in 2-5 min

---

## Baidu Verification

- Baidu web interface rejects `.html` file upload via browser (UI bug: "Unsupported document type")
- **Solution**: Upload verification file via FTP client to web root, then trigger file verification in Baidu console
- FTP upload to Windows shared hosting works where browser UI fails

---

## Yandex Verification

**File method**:
- Filename must be: `yandex_<code>.html` (underscore in middle, not underscore at start)
- Content must be full HTML wrapper, not plain text

**Example**:
```html
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body>Verification: 3fdba79f71c66d1b</body>
</html>
```

Upload via FTP, then trigger verification in Yandex Webmaster.

---

## Search Engine Submission Priority

| Engine | Priority | Tools |
|--------|----------|-------|
| Google | Must-do | search.google.com/search-console |
| Bing | High (Yahoo shared) | bing.com/webmasters |
| Yandex | Medium (Russia) | webmaster.yandex.com |
| Baidu | If China market | zhanzhang.baidu.com |

### Submission Checklist
1. Verify ownership (HTML tag / file / CNAME)
2. Submit sitemap URL: `https://www.example.com/sitemap.xml`
3. Ensure HTTPS works and canonical URLs are correct
4. Check coverage/index status after 1-3 days

---

## References
- `references/cloudflare-ssl-modes.md`
- `references/seo-submission-checklist.md`