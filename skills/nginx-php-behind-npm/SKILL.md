---
name: nginx-php-behind-npm
description: >
  Bind a PHP website served by the host nginx behind Nginx Proxy Manager
  when the NPM container already occupies port 80/. Covers the exact
  conflict pattern: default site → nginx can't start → proxy never reaches
  PHP-FPM, and the known good resolution order.
---

# Nginx + PHP behind Nginx Proxy Manager

Use this when the host nginx and the NPM container both want port 80/443
and your PHP site must be reached through a domain managed by NPM.

## Trigger

- NPM proxy exists but upstream returns 502 Bad Gateway
- `nginx -t` ok, but `ss` shows only docker-proxy on 80
- `nginx` fails to start with `bind() to 0.0.0.0:80 failed`

## Required belief before proceeding

Nginx on the host and NPM **cannot both bind 80**. The host nginx
must use a non-overlapping port (e.g. 8087+). After this, NPM forwards
traffic to the host nginx, which talks to php-fpm.

## Fixed order

1. Delete the default site when it collides with NPM:
```bash
rm -f /etc/nginx/sites-enabled/default
nginx -t && nginx -c /etc/nginx/nginx.conf -g "daemon on;" || true
ss -tlnp | grep ':8086\|:8087\|:80\|nginx'
```

2. Ubuntu 22.04 php-fpm8.1 socket path is `/run/php/php8.1-fpm.sock`.
   Do not guess the path.

3. Server block for the site listens on a free high port:
```nginx
server {
    listen 8087 default_server;
    server_name _;
    root /path/to/site;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_index index.php;
    }
    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

4. Restart host nginx. Then `curl -I http://127.0.0.1:8087` must return `200 OK`.

5. Update the NPM proxy host to `forward_scheme=http`, `forward_host=154.41.135.101`,
   `forward_port=<chosen port>`, `ssl_forced=false`, `http2_support=false`.

6. Verify from outside: `curl -I http://<domain>` and expect `200 OK`.

## Pitfalls

- Do not use `nginx -s reload` when `nginx -t` passed but `ssl` sites are present.
  Restart is the calmer choice.
- If `nginx` fails to start, `ss -tlnp` and `/var/log/nginx/error.log`
  is the unlock pattern.
- If PHP returns 502, check `ls /run/php/*.sock` first.
- Site directory under `/root/` is invisible to `www-data` by default:
  run `chmod o+rx /root` and `chmod -R o+rx /path/to/site` before testing.
- PHP-FPM socket path varies by distro/version:
  discover with `find /run /var/run -name 'php*-fpm*.sock'` instead of hardcoding.
- NPM API is schema-strict: PUT payload must match the **exact** `GET /api/nginx/proxy-hosts/<id>` keys.
  Extra/missing fields yield `400 {code:400, message:'data must NOT have additional properties'}`.
- NPM proxy `ssl_forced=true` with an existing `certificate_id` is valid even when the upstream is HTTP.
  Accept the current certificate state instead of forcing `ssl_forced=false`.
- If `nginx -s stop` or `reload` complains about `/run/nginx.pid` missing, use:
  `nginx -c /etc/nginx/nginx.conf -g "daemon on;"` to restart cleanly instead of `reload`.

## Pretty URL rewrites after binding

Once the site is live, internal pretty URLs like `/product/<slug>` and `/news/<slug>` still 404 if Nginx doesn't rewrite them to the PHP router. Add these blocks before the generic `location ~ \.php$` block:

```nginx
location ~ ^/product/(.+)$ {
    rewrite ^/product/(.+)$ /product.php?slug=$1 last;
}
location ~ ^/news/(.+)\.html$ {
    rewrite ^/news/(.+)\.html$ /news_detail.php?slug=$1 last;
}
location ~ ^/news/(.+)$ {
    rewrite ^/news/(.+)$ /news_detail.php?slug=$1 last;
}
```

`product.php` already strips a leading `/product/`, and `news_detail.php` strips `/news/` and `.html`, so the router itself usually does not need code changes — the rewrite alone is enough.

## Link verification expectations

- `fonts.googleapis.com` and `fonts.gstatic.com` commonly 404/block from mainland hosts; this is environmental, not a site bug — rely on the local `filesystem`-served `bundle-*.css` fallbacks instead.
- `mailto:` and `tel:` links fail HTTP probes with "No connection adapters"; they are fine in a real browser.
- JS template tokens like `/product/${product.slug}` appear as literal strings in raw HTML crawls but render correctly client-side after JS interpolation.
