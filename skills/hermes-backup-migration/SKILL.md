---
name: hermes-backup-migration
description: Backup, restore, and migrate Hermes Agent data across machines. Covers the local backup scripts, cron scheduling, retention policies, git remote management, shallow-clone migration, and cross-machine parallel deployment.
---

# Hermes Backup & Migration

## When to use this skill

- Daily backup verification or troubleshooting
- Changing the remote backup repository (GitHub org/account switch)
- Migrating Hermes to a new machine while keeping the old one running
- Restoring from a historical backup zip
- Reducing backup disk usage / git history bloat

## Core layout (default installation)

| Path | Purpose |
|---|---|
| `~/.hermes/scripts/backup_hermes.sh` | Daily backup script |
| `~/.hermes/scripts/restore_hermes.sh` | Restore script |
| `~/hermes_backups/` | Local backup repo root |
| `crontab` entry | `0 1 * * * /bin/bash ~/.hermes/scripts/backup_hermes.sh` |

The backup repo is a git repo with zip snapshots committed daily.

## Backup script behavior

- Zips `~/.hermes` core files (config, state, memories, skills, scripts, .env)
- Excludes `audio_cache/`, `cache/`, `*.log`
- Keeps `RETENTION_DAYS` worth of zip files locally (default 7)
- Creates `backup_hermes_latest.zip` symlink
- Commits and pushes to `REMOTE_REPO` on GitHub

## Pitfall: git history bloat

Each daily zip (190–204MB) is committed, so `.git` grows fast. A 9-day history can reach ~8GB in `.git` alone.

**Do not run `git gc --aggressive` on a large backup repo interactively** — it times out on multi-hundred-MB objects and blocks the session.

Instead:
- Set `RETENTION_DAYS` to a smaller value (e.g. 3) to cap future growth.
- For migration, use **shallow clone** so new machines do not download the full history.

## Migration (parallel / dual-machine)

Goal: new machine runs Hermes alongside the old one. Old service stays up.

### Pre-flight: SSH connectivity diagnosis

Before attempting migration, verify the new machine is reachable. For GCP instances, follow this order:

1. **Ping** — confirms host is online
2. **Port scan** — check 22, 2222, 80, 443
3. **SSH attempt** — only after ports are confirmed open

**Critical pitfall:** If `ssh` returns `Permission denied (publickey,password)` despite having correct credentials, the issue is almost always **GCP firewall blocking port 22**, not bad credentials. Do not retry SSH with different keys; fix the firewall rule first.

GCP fix: Console → VPC network → Firewall → Create rule allowing `tcp:22` from your IP.

### Step 1 — Prepare migration package (3KB, no zips)

```bash
mkdir -p /tmp/hermes_migration/scripts
cp ~/.hermes/scripts/backup_hermes.sh  /tmp/hermes_migration/scripts/
cp ~/.hermes/scripts/restore_hermes.sh /tmp/hermes_migration/scripts/
crontab -l | grep -E 'backup|orchestrator' > /tmp/hermes_migration/cron_hermes.txt
# generate a README, then tar it
tar -czf ~/hermes_migration_$(date +%Y%m%d_%H%M%S).tar.gz -C /tmp /basename
```

**Important:** Do not include the zip history in the migration package. It is already in the remote git repo.

### Step 2 — Transfer package

Send the ~3KB tar.gz to the new machine via scp/rsync/GCP Console/etc.

### Step 3 — New machine setup

1. Install Hermes Agent.
2. Transfer `config.yaml` securely (it contains API keys) — do not put it in the public migration package.
3. Extract scripts into `~/.hermes/scripts/`.
4. Pull backup history with shallow clone:

```bash
git clone --depth 3 --branch main git@github.com:clowlove/hermes-backups.git ~/hermes_backups
```

Adjust `--depth` to match desired retention (e.g. 3 for three days).

**Pitfall: SSH key not configured on new machine.** If `git clone` fails with `Permission denied (publickey)`, the new machine lacks SSH keys for GitHub. Fix:

```bash
# Option A: use HTTPS + PAT
git clone https://<TOKEN>@github.com/<ACCOUNT>/hermes-backups.git ~/hermes_backups
# then clear history: history -d $((HISTCMD-1))

# Option B: generate SSH key and add to GitHub account
ssh-keygen -t ed25519 -C "hermes@new-machine"
cat ~/.ssh/id_ed25519.pub  # add this to GitHub account settings
```

**Pitfall: remote repo doesn't exist or PAT has no access.** Before cloning, verify:

```bash
curl -s -H "Authorization: token <PAT>" https://api.github.com/repos/<ACCOUNT>/hermes-backups
```

If `"Not Found"` or `"private": true`, create the repo first:

```bash
curl -s -H "Authorization: token <PAT>" https://api.github.com/user/repos \
  -d '{"name":"hermes-backups","private":false,"description":"Hermes Agent backups"}'
```

### Step 4 — Restore (optional)

```bash
bash ~/.hermes/scripts/restore_hermes.sh [DATE]
```

The restore script:
- Stops Hermes first (prompt with 10s timeout)
- Syncs remote repo
- Unzips chosen backup into temp dir
- Moves current `~/.hermes` to a dated backup
- Moves restored `~/.hermes` into place

### Step 5 — Cron on new machine

Add to crontab:

```
0 1 * * * /bin/bash ~/.hermes/scripts/backup_hermes.sh >> ~/.hermes/scripts/backup.log 2>&1
```

Recommend changing `REMOTE_REPO` in `backup_hermes.sh` to a new repo to avoid push conflicts between machines.

## Reducing disk usage

| Action | Effect |
|---|---|
| `RETENTION_DAYS=3` | Keeps only 3 zip files locally |
| Shallow clone `--depth 3` | New machine downloads ~few MB instead of ~10GB |
| Separate remote repo per machine | Avoids history conflicts |

## Space estimates (observed)

| Item | Size |
|---|---|
| 3-day zip files | ~406MB |
| Full 9-day `.git` history | ~8.3GB |
| Migration package (scripts only) | ~3KB |

## Verification checklist

- [ ] `backup_hermes_latest.zip` symlink points to a real file
- [ ] `zip -T` passes on the latest backup
- [ ] `git remote -v` shows the expected remote
- [ ] New machine `~/hermes_backups` contains the expected zip files
- [ ] New machine Hermes starts and loads sessions/memories after restore
