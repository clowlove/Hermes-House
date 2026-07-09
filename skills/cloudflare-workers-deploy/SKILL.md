---
name: cloudflare-workers-deploy
description: Deploy and manage Cloudflare Workers with D1, R2, KV, and Workers KV store
triggers:
  - deploy to cloudflare workers
  - cf_b2b type projects
  - wrangler.toml based deployment
---

# Cloudflare Workers Deployment

## Workflow

### Phase 1: Scout & Plan
1. Clone/fetch the repo, read `wrangler.toml` and `package.json`
2. Identify required Cloudflare resources (D1, R2, KV) and their bindings
3. If resources don't exist yet, create them via REST API

### Phase 2: Create Cloudflare Resources
```bash
# D1 Database
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/d1/database" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "database_name"}'

# R2 Bucket
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/r2/buckets" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "bucket-name"}'

# KV Namespace
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "namespace-name"}'
```

### Phase 3: Configure wrangler.toml
Update `wrangler.toml` with resource IDs:
```toml
[[d1_databases]]
binding = "DB"
database_name = "database_name"
database_id = "<uuid>"

[[kv_namespaces]]
binding = "STATIC_ASSETS"
id = "<uuid>"
```

### Phase 4: Initialize Database
```bash
# Run SQL migrations (use --remote for production D1)
npx wrangler d1 execute database_name --file=schema/schema.sql --remote
```

### Phase 5: Deploy
```bash
npx wrangler deploy
```

## KV Settings Pattern (website_settings)
Many CF Workers projects store site config in KV as JSON. This pattern recurs in B2B/ecommerce templates.

**Correct way to write JSON to KV:**
```bash
# Must use --path <file>, NOT stdin/heredoc — wrangler reads value from file
echo '{"site_name":"...","email":"..."}' > /tmp/settings.json
npx wrangler kv key put "website_settings" --path /tmp/settings.json --namespace-id <uuid> --remote
```

## Pitfalls

- **wrangler kv key put**: Use `--path <file>` to read value from file. Stdin/heredoc does NOT work. Must add `--remote` for production targeting.
- **wrangler d1 execute**: Always add `--remote` flag to target production D1, not local dev DB.
- **No build step**: Pure JS projects deploy directly without `npm run build`. Check `package.json` scripts first.
- **Admin role**: Default admin accounts may be `admin` role, not `super_admin`. Upgrade via D1: `UPDATE admins SET role='super_admin' WHERE username='admin'`
- **POST vs PUT for updates**: POST often creates duplicates — verify whether update uses POST or PUT
- **D1 SQL via API**: When `wrangler` CLI fails, fall back to Cloudflare REST API for D1 operations
- **KV settings NOT auto-propagated to pages**: Pages with hardcoded HTML template strings do NOT update when KV changes. Fix: read settings server-side in page handler (`await env.STATIC_ASSETS.get()`), inject into HTML template string, redeploy. Check home.js, about.js, contact.js when updating site content. Pages using JS `fetch('/api/settings')` client-side may fail silently — always prefer server-side injection for static content pages.
- **CSS variable naming mismatch causes 500 errors**: `layout.css` defines `--primary`, `--dark`, `--gray-*`, `--radius`, `--shadow-*`. Many page templates incorrectly use `--primary-color`, `--text-light`, `--text-dark`, `--bg-light` which do NOT exist in layout.css and cause Worker exceptions. **Always verify all CSS variables match layout.css definitions before deploying.** Replace: `var(--primary-color)→var(--primary)`, `var(--text-light)→var(--gray-500)`, `var(--text-dark)→var(--dark)`, `var(--bg-light)→var(--gray-100)`.
- **Template literal `class` keyword causes "Expected ; but found class" build error**: In Cloudflare Workers (V8 engine), template literals containing `class=` attributes fail to parse, producing cryptic build errors at the `class` keyword. **Workaround**: Use string concatenation (`'<div class="card">' + ... + '</div>'`) for HTML with class attributes. Do NOT use backtick template literals for HTML card markup in page handlers.
- **Product detail pages 500 — check CSS vars first**: When a product-detail page throws 500, CSS variable mismatches are almost always the culprit, not the DB query. Use a minimal stub page to isolate, then progressively add complexity.
- **Server-side rendering preferred for product listing**: Pages fetching `/api/products` client-side via `API.get()` are fragile. Render products server-side with `env.DB.prepare().all()` and inject HTML during SSR. Client-side JS fetch is fine for dynamic content (filters, modals) but not primary content.

## Verification
```bash
curl -sLo /dev/null -w "%{http_code}" "https://worker.workers.dev/"
curl -s "https://worker.workers.dev/api/settings"
```

## References
- `references/cloudflare-rest-api.md` — Cloudflare API endpoints for D1/R2/KV/Workers management
- `references/cf-b2b-project-notes.md` — Session-specific notes from deploying geeeeeeek/cf_b2b
- `references/d1-database-operations.md` — D1 INSERT/UPDATE patterns, image URL batch update, validation scripts, and browser-console product extraction technique