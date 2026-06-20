---
name: php-website-development
description: Build and maintain PHP websites with Bootstrap, MySQL, nginx, and Cloudflare — admin panels, product catalogs, inquiry systems, SEO, and performance optimization.
triggers:
  - php website
  - admin panel
  - product catalog
  - bootstrap website
  - mysql website
  - nginx php
  - cloudflare cache
  - inquiry system
  - RFQ form
  - international trade website
  - 外贸网站
  - 后台管理
  - FK constraint
  - foreign key constraint
  - schema mismatch
  - column not found
  - og:image relative
  - canonical url http
---

# PHP Website Development

Build production-ready PHP websites with Bootstrap 5, MySQL, nginx, and Cloudflare CDN.

## Architecture Pattern

```
project/
├── config/database.php      # DB config + dynamic settings loader
├── includes/functions.php    # Shared utilities (auth, sanitize, upload)
├── includes/seo.php          # SEO meta + JSON-LD generator
├── templates/header.php      # Shared header (nav, CSS, meta)
├── templates/footer.php      # Shared footer
├── admin/auth.php            # Admin auth + sidebar layout template
├── admin/index.php           # Dashboard
├── admin/[module].php        # CRUD pages (products, news, etc.)
├── api/[endpoint].php        # JSON API endpoints
├── assets/css/bundle.min.css # Merged + minified CSS
├── assets/js/                # JS files
├── uploads/                  # User uploads (deny PHP execution)
├── logs/                     # Error logs + login attempts
└── scripts/                  # Maintenance scripts
```

## Critical Pitfalls

### CSS Variable Naming Conflicts
**PROBLEM:** Multiple CSS files use different variable names for the same concept:
- `style-v3.css`: `--primary-color`, `--dark-color`, `--success-color`
- `enhance-v3.css` / `product-focus-v4.css` / `visual-v5c.css`: `--primary`, `--accent`, `--gray-100`, `--success`

If only `style-v3.css` defines variables, the other files' references to `--primary`, `--accent`, `--gray-*` resolve to **empty strings**, causing invisible text and broken styles.

**FIX:** Create a unified CSS file (e.g., `color-harmony.css`) that defines ALL variable variants:
```css
:root {
    --primary: #0f2b5b;
    --accent: #c8a23c;
    --gray-50: #f9fafb;  --gray-100: #f3f4f6;  /* ...through... */
    --gray-900: #111827;
    /* Map old names to new */
    --primary-color: var(--primary);
    --dark-color: var(--gray-800);
    --secondary-color: var(--accent);
    --success-color: var(--success);
}
```

### White Text on White Background
**PROBLEM:** Original CSS designed for dark backgrounds (`color: white` on feature-box h4/p), but background was changed to white in a later CSS file. Text becomes invisible.

**FIX:** When changing section backgrounds from dark to light, ALWAYS update text colors in the same change. Use `!important` in override CSS to ensure precedence.

### Scroll Reveal Animation Fallback
**PROBLEM:** `.reveal { opacity: 0 }` elements depend on JS `IntersectionObserver` adding `.revealed` class. If JS fails or doesn't fire (slow connection, browser quirk), **all content stays invisible**.

**FIX:** Add CSS animation fallback:
```css
@keyframes reveal-fallback {
    to { opacity: 1; transform: translateY(0); }
}
.reveal { animation: reveal-fallback 0.01s 2s forwards; }
.reveal.revealed { animation: none; }
```

### Cloudflare Cache Busting
**PROBLEM:** After modifying CSS/JS files, Cloudflare serves stale cached versions. `cf-cache-status: HIT` even after file changes.

**FIX:** Use query string versioning in `header.php`:
```php
<link href="/assets/css/bundle.min.css?v=<?= filemtime(__DIR__ . '/../assets/css/bundle.min.css') ?>" rel="stylesheet">
```
Increment version manually when Cloudflare ignores filemtime: `?v=2`, `?v=3`, etc.

### Cloudflare HTTPS Protocol Detection
**PROBLEM:** Behind Cloudflare Flexible SSL, `$_SERVER['HTTPS']` is not set. `getCurrentUrl()` returns `http://` breaking canonical, og:url, and all absolute URLs.

**FIX:** Check `HTTP_X_FORWARDED_PROTO` in every `getCurrentUrl()` definition:
```php
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') $proto = 'https';
elseif (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') $proto = 'https';
else $proto = 'http';
```

### Foreign Key NULL vs 0
**PROBLEM:** HTML `<select>` sends empty string → PHP `(int)("") = 0` → FK constraint fails silently.

**FIX:** `!empty($_POST['field']) ? (int)$_POST['field'] : null` for all FK columns.

### Schema Mismatch Silent Failures
**PROBLEM:** PHP code references columns that don't exist (e.g., `status` when table has `is_read`/`replied`). INSERT/UPDATE silently fails or throws 500.

**DIAGNOSIS:** Compare `DESCRIBE table_name` with PHP INSERT/UPDATE statements.

### Missing nginx Routes
**PROBLEM:** New PHP pages return 404 because nginx doesn't have clean URL routes.

**FIX:** For each new page, add to nginx config:
```nginx
location = /page-name {
    try_files $uri /page-name.php?$query_string;
}
```
Always run `sudo nginx -t && sudo systemctl reload nginx` after changes.

### Upload Directory PHP Execution
**PROBLEM:** Uploaded files in `/uploads/` could contain malicious PHP.

**FIX:** Add nginx rule to deny PHP execution in uploads:
```nginx
location ~* /uploads/.*\.php$ {
    deny all;
    return 403;
}
```

### Heading Hierarchy for SEO
**PROBLEM:** Product cards use `<h5>` under `<h2>` section titles, skipping H3/H4. Search engines flag this as poor structure. Visual size is controlled by CSS, not heading level.

**FIX:** Use correct semantic level with visual class override:
```html
<!-- Section title -->
<h2 class="section-title">Featured Tractors</h2>
<!-- Product card: H3 (correct level) with h5 visual size -->
<h3 class="h5"><?= escape($product['name']) ?></h3>
```
Pattern: `<h{level} class="h{visual-size}">` — semantic level for SEO, visual class for display.

### Perl Regex Breaking PHP Ternary Expressions
**PROBLEM:** Using `perl -pi -e` to replace hardcoded English text with `t('...')` calls fails when the text is inside PHP ternary expressions:
```php
// BEFORE perl:
<?= $action === 'add' ? 'Add Product' : 'Edit Product' ?>
// AFTER perl (BROKEN — nested PHP tags):
<?= $action === 'add' ? '<?= t('Add Product') ?>' : '<?= t('Edit Product') ?>' ?>
```

**FIX:** For ternary expressions, use direct file edit (patch tool or manual) instead of perl regex:
```php
<?= $action === 'add' ? t('Add Product') : t('Edit Product') ?>
```
Safe to use perl for simple HTML text outside PHP blocks: `>Text<` → `><?= t('Text') ?><`

### Wrong Include Path in New Pages
**PROBLEM:** New pages created by subagents sometimes use `__DIR__ . '/includes/header.php'` instead of `__DIR__ . '/templates/header.php'`, causing 500 errors.

**FIX:** Always verify include paths in new PHP files:
```bash
grep -n 'include\|require' /path/to/new-page.php
```
Should show `/templates/header.php` and `/templates/footer.php`, not `/includes/`.

## Admin Panel Architecture

### Shared Auth Template (`admin/auth.php`)
Every admin page includes this single file which provides:
- Login check via `requireLogin()`
- Database connection (`$db`)
- CSRF token (`$csrfToken`)
- Flash messages (`$flashMsg`, `$flashType`)
- Complete sidebar navigation with active state
- Header with user info
- Opens `<div class="content-area">`

Each page sets `$pageTitle` and `$currentPage` before including auth.php:
```php
<?php
$pageTitle = 'Products';
$currentPage = 'products';
require_once __DIR__ . '/auth.php';
// ... page content ...
echo '</div></div><script src="bootstrap.bundle.min.js"></script></body></html>';
```

### Admin i18n (Language Switching)
Add Chinese/English switching to the admin panel:

**Files:**
- `admin/lang/zh.php` — Chinese translations (200+ terms)
- `admin/lang/en.php` — English (identity map)
- `admin/lang_helper.php` — `t($key)` function + session-based language toggle

**Implementation:**
```php
// admin/lang_helper.php
function t($key) {
    static $lang = null;
    if ($lang === null) {
        $langCode = $_SESSION['admin_lang'] ?? 'zh';
        $langFile = __DIR__ . '/lang/' . $langCode . '.php';
        $lang = file_exists($langFile) ? require($langFile) : [];
    }
    return $lang[$key] ?? $key;
}
```

**In auth.php sidebar footer:** Add language toggle buttons:
```html
<a href="?lang=zh" class="btn btn-sm <?= ($langCode==='zh')?'btn-primary':'btn-outline-secondary' ?>">中文</a>
<a href="?lang=en" class="btn btn-sm <?= ($langCode==='en')?'btn-primary':'btn-outline-secondary' ?>">EN</a>
```

**Coverage:** Translate sidebar nav, page titles, table headers, form labels, button text, flash messages, empty-state messages, status badges. Use `t()` calls in all admin pages.

### Database-Driven Settings
Load site settings from DB into PHP constants at startup:

```php
// config/database.php
function loadSiteSettings() {
    $db = getDBConnection();
    $settings = $db->query("SELECT setting_key, setting_value FROM settings")->fetchAll(PDO::FETCH_KEY_PAIR);
    if (!defined('SITE_URL')) define('SITE_URL', $settings['site_url'] ?? 'https://default.com');
    // ... more constants ...
}
```

Call `loadSiteSettings()` in `functions.php` after `require_once database.php`.

## Inquiry/RFQ System Pattern

1. **Database table:** `inquiries` with status enum (new/replied/quoted/closed)
2. **API endpoint:** `api/inquiry.php` — POST JSON, validate, insert, return JSON response
3. **Product page form:** Embedded RFQ form with country dropdown, pre-filled message
4. **Admin page:** List with status filters, detail view, status update, admin notes
5. **JavaScript:** `fetch()` to API, show success/error alerts, WhatsApp quick link on success

**Full pattern:** See `foreign-trade-operations` skill → `references/rfq-inquiry-system-pattern.md`

## Business Pages Pattern

For international trade sites, create these additional pages:

### Export/Trade Process (`export.php`)
- 6-step export process (Inquiry → Quotation → Confirmation → Production → QC → Shipping)
- Trade terms cards (FOB/CIF/EXW with descriptions)
- Payment terms (T/T 30%+70%, L/C, Western Union)
- Shipping info (container sizes, packaging, port, delivery by region)
- FAQ accordion (Bootstrap collapse)

### Why Choose Us (`why-us.php`)
- Company strengths (years, factory, capacity, countries)
- Quality assurance process (4 steps)
- Certifications (dark gradient bg with glassmorphism cards)
- Global services (training, parts, support, installation)
- Customer testimonials

### Navigation Additions
- Add "Why Us" and "Export" links to navbar
- Add "Get Quote" button (gold accent) linking to /contact
- Add WhatsApp button (green) linking to wa.me/{number}

### Navigation Active State
Each page sets `$currentPage` before including header.php. The header uses it to highlight the current nav item:
```php
// In templates/header.php nav links:
<a class="nav-link<?= ($currentPage ?? '') === 'about' ? ' active' : '' ?>" href="/about">About Us</a>
```
CSS underline effect on active/hover (in bundle):
```css
.nav-link::after { content:''; position:absolute; bottom:0; left:50%; width:0; height:2px;
    background: linear-gradient(90deg, var(--primary), var(--accent)); transition: all 0.3s ease;
    transform: translateX(-50%); border-radius: 1px; }
.nav-link:hover::after, .nav-link.active::after { width: 60%; }
```

### Contact Info Consistency
**PROBLEM:** Header top bar has hardcoded phone/email, footer uses PHP constants, contact page has different values. Social links use `#` (dead links).

**FIX:** Use PHP constants from `config/database.php` everywhere:
```php
// In header.php top bar:
<span><i class="fas fa-phone"></i> <?= CONTACT_PHONE ?></span>
<span><i class="fas fa-envelope"></i> <?= CONTACT_EMAIL ?></span>
<a href="<?= SOCIAL_FACEBOOK ?>" target="_blank" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
```
Never hardcode phone numbers, emails, or social URLs — always use the constants.

### Footer Additions
- Trade terms row (FOB/CIF/EXW)
- Payment methods (T/T, L/C, Western Union)
- Certification badges (pill style)

### nginx Routes
```nginx
location = /export { try_files $uri /export.php?$query_string; }
location = /why-us { try_files $uri /why-us.php?$query_string; }
```

## CSS Build Pipeline

Create `scripts/build-css.sh` that runs a PHP minifier:
1. Concatenate CSS files in order: base → enhance → product-focus → visual → responsive → color-harmony
2. Remove comments, collapse whitespace
3. Output to `assets/css/bundle.min.css`
4. Use `filemtime()` for cache-busting version

### CSS Bundle Deduplication
**PROBLEM:** Over multiple iterations, similar CSS files accumulate (`style-v2.css`, `style-v3.css`, `style-responsive.css`) with identical `:root` variables and base styles. Concatenating them creates a bundle with the same rules repeated 2-3 times (58KB+ of bloat).

**DIAGNOSIS:** Check for duplicates before rebuilding:
```bash
cd assets/css && md5sum style-*.css visual-*.css
# Also check: wc -l *.css (similar line counts = likely duplicates)
```

**FIX:** Rebuild bundle with only unique source files:
```bash
cat style-responsive.css enhance-v3.css product-focus-v4.css visual-v5c.css > bundle.min.css
# Minify: remove comments + collapse whitespace
perl -0777 -pe 's|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/||gs' bundle.min.css | \
  perl -pe 's/\s+/ /g' | perl -pe 's/^\s+//; s/\s+$//' > bundle.min.tmp && mv bundle.min.tmp bundle.min.css
```
Archive duplicates: `mv style-v2.css style-v2.css.bak` (don't delete until verified).

### color-harmony.css Must Be Explicitly Loaded
**PROBLEM:** `color-harmony.css` defines brand colors (`--primary: #0f2b5b`, `--accent: #c8a23c`) but is NOT included in the bundle. The bundle's `:root` has generic blue `--primary-color: #2563eb`. Result: site renders with wrong brand colors.

**FIX:** Add AFTER bundle.min.css in `templates/header.php` (later file wins in CSS cascade):
```php
<link href="/assets/css/bundle.min.css?v=<?= filemtime(__DIR__ . '/../assets/css/bundle.min.css') ?>" rel="stylesheet">
<link href="/assets/css/color-harmony.css?v="<?= filemtime(__DIR__ . '/../assets/css/color-harmony.css') ?>" rel="stylesheet">
```
Verify with browser console: `getComputedStyle(document.documentElement).getPropertyValue('--primary').trim()` should return `#0f2b5b`.

## Security Checklist

- [ ] Login rate limiting (5 attempts / 15 min per IP+username)
- [ ] CSRF tokens on all forms (`generateCSRFToken()` / `verifyCSRFToken()`)
- [ ] `sanitize()` all user inputs
- [ ] `escape()` all output
- [ ] PDO prepared statements (no string interpolation in SQL)
- [ ] Upload validation (file type, size, rename with `uniqid()`)
- [ ] nginx security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy)
- [ ] Deny PHP execution in upload directories
- [ ] Remove test/debug files from production (test.php, db-test.php)
- [ ] Whitelist allowed setting keys in settings handler

## Performance Optimization

- CSS bundle (5 unique files → 1, ~38KB after deduplication)
- nginx gzip compression
- Browser caching: images 30d, CSS/JS 7d, fonts 30d
- Image lazy loading (`loading="lazy"`)
- `aspect-ratio` for responsive images instead of fixed heights
- Preconnect for external CDNs (Google Fonts, Bootstrap, Font Awesome)
