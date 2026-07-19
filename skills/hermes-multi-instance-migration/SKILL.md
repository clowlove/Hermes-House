---
name: hermes-multi-instance-migration
description: "Migrate Hermes Agent to a new server while keeping both instances running in parallel. Covers backup, SSH troubleshooting, skill/memory sync, and GitHub remote setup."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, migration, multi-instance, backup, sync, gcp, fail2ban]
    related_skills: [hermes-agent]
---

# Hermes Multi-Instance Migration

Migrate a Hermes Agent installation to a new server with zero downtime on the old instance. Both machines run independently after migration.

## When to Use This Skill

- Setting up Hermes on a new server (AWS, GCP, VPS, etc.)
- Cloning an existing instance to a colleague
- Splitting one instance into two for redundancy
- The user says "迁移到新机器", "双机并行", "clone 实例", or "同步配置到新服务器"

## Pre-Migration Checklist

1. **Old machine backup works**
   ```bash
   bash ~/.hermes/scripts/backup_hermes.sh
   ls -lh ~/hermes_backups/
   ```

2. **New machine reachable**
   - GCP/AWS: ensure firewall allows port 22 from your IP
   - Test: `ssh root@NEW_IP` or browser-based console SSH

3. **GitHub remote repo exists**
   - Verify repo under correct account: `curl -H "Authorization: token <PAT>" https://api.github.com/repos/<OWNER>/<REPO>`
   - If missing: `curl -H "Authorization: token <PAT>" https://api.github.com/user/repos -d '{"name":"hermes-backups","private":false}'`

## Migration Steps

### Step 1: Fix new machine SSH access

**GCP-specific:** VPC firewall defaults deny inbound. Create an ingress rule for `tcp:22`.

**Fail2Ban issue:** If old IP is banned:
```bash
# On new machine
fail2ban-client set sshd unbanip <OLD_IP>
systemctl stop fail2ban && systemctl disable fail2ban
```

### Step 2: Prepare new machine

```bash
# Install tools
apt-get update && apt-get install -y git zip unzip

# Create directories
mkdir -p ~/.hermes/scripts ~/hermes_backups
```

### Step 3: Clone backup repository

Use shallow clone to avoid downloading full git history:
```bash
git clone --depth 3 --branch main https://<TOKEN>@github.com/<OWNER>/hermes-backups.git ~/hermes_backups
```

### Step 4: Sync configuration and skills

**Exclude large/volatile directories:**
```bash
tar -czf /tmp/hermes_config_sync.tar.gz \
  -C ~/.hermes \
  --exclude='skills/.curator_backups' \
  --exclude='cache/*' \
  --exclude='logs/*' \
  --exclude='audio_cache/*' \
  --exclude='image_cache/*' \
  skills memories config.yaml .env cron hooks scripts docs profile providers shared state pairing
```

**Transfer to new machine (paramiko chunked upload for reliability):**
```python
import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
with sftp.open('/tmp/hermes_config_sync.tar.gz', 'wb') as remote_file:
    with open('/tmp/hermes_config_sync.tar.gz', 'rb') as local_file:
        uploaded = 0
        while True:
            chunk = local_file.read(512 * 1024)  # 512KB chunks
            if not chunk:
                break
            remote_file.write(chunk)
            uploaded += len(chunk)
sftp.close()

# Extract on new machine
ssh.exec_command('cd ~/.hermes && tar -xzf /tmp/hermes_config_sync.tar.gz && rm /tmp/hermes_config_sync.tar.gz')
```

### Step 5: Verify counts match

```bash
# On new machine
echo "Skills: $(ls ~/.hermes/skills/ | wc -l)"
echo "Memories: $(ls ~/.hermes/memories/*.md 2>/dev/null | wc -l)"
echo "Scripts: $(ls ~/.hermes/scripts/ | wc -l)"
```

### Step 6: Configure automatic backups

```bash
# On new machine - set daily backup cron
(crontab -l 2>/dev/null || echo "") | grep -v 'backup_hermes.sh'
echo "0 1 * * * /bin/bash ~/.hermes/scripts/backup_hermes.sh >> ~/.hermes/scripts/backup.log 2>&1" | crontab -
```

## Critical Rules

1. **Never sync `.env` via git or shared storage** — API keys must be configured separately on each instance
2. **Both machines are independent** — they push to the same GitHub repo but do NOT rsync live
3. **Keep original product structure** — only touch CSS/JS/meta for SEO/visual work, never replace HTML tables/cards
4. **Always verify before declaring success** — check file counts, not just "script ran"

## Common Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Fail2Ban blocks old IP | Old machine can't SSH to new | `fail2ban-client set sshd unbanip <OLD_IP>` |
| GCP firewall blocks 22 | Connection refused | Create VPC ingress rule for tcp:22 |
| GitHub repo mismatch | "Repository not found" | Verify repo exists under correct owner account |
| Memory files missing | New instance has no user context | Explicitly copy `memories/*.md` |
| Large transfers timeout | tar.gz >4MB hangs | Stream in 512KB chunks with progress |
| GCP firewall rule mismatch | Port open in rule but still blocked from outside | Rule target must be "所有实例" or match instance network tags |
| HTTPS git push fails | `could not read Password` after clone | Switch remote to SSH: `git remote set-url origin git@github.com:OWNER/REPO.git` and add SSH key to GitHub |
| Subscription port blocked | busybox httpd works locally but external timeout | Open `tcp:<PORT>` in GCP cloud firewall; internal firewall is separate |
| Instance has restrictive tags | New firewall rules don't apply | Check instance tags in GCP Console; rule target must include them |
| Swap not configured | Memory-constrained GCP micro instances | Create 3GB swapfile with `swappiness=10`, `vfs_cache_pressure=50` |
| GCP firewall rule mismatch | Port open in rule but still blocked from outside | Rule target must be "所有实例" or match instance network tags |
| HTTPS git push fails | `could not read Password` after clone | Switch remote to SSH: `git remote set-url origin git@github.com:OWNER/REPO.git` and add SSH key to GitHub |
| Subscription port blocked | busybox httpd works locally but external timeout | Open `tcp:<PORT>` in GCP cloud firewall; internal firewall is separate |
| Instance has restrictive tags | New firewall rules don't apply | Check instance tags in GCP Console; rule target must include them |
| Swap not configured | Memory-constrained GCP micro instances | Create 3GB swapfile with `swappiness=10`, `vfs_cache_pressure=50` |

## After Migration

Both instances run in parallel. Schedule depends on user preference:
- **Independent backups**: each pushes to same GitHub repo (historical backup merges)
- **Separate repos**: modify `REMOTE_REPO` in `backup_hermes.sh` to avoid conflicts

## SSH Key Auth for GitHub

For new instances, prefer SSH over HTTPS to avoid credential prompts:
```bash
ssh-keygen -t ed25519 -C "hermes@HOST" -f ~/.ssh/id_ed25519 -N ""
# Show public key to user for GitHub web UI
git remote set-url origin git@github.com:OWNER/REPO.git
```

## GCP Networking Gotchas

- **Firewall target mismatch**: Rule with target "指定网络标签" won't apply unless instance tags match exactly
- **Instance tags**: Check via GCP Console or `curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/tags`
- **Internal vs external firewall**: `iptables/ufw/fail2ban` inside the VM does NOT block external port scans; GCP cloud firewall does
- **Subscription/httpd ports**: busybox httpd may bind to `*:PORT` but external timeout means cloud firewall is still blocking

## Memory-Constrained Instances

For GCP micro instances with <1GB RAM:
```bash
fallocate -l 3G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=3072
chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile
echo "/swapfile none swap sw 0 0" >> /etc/fstab
sysctl vm.swappiness=10
sysctl vm.vfs_cache_pressure=50
```

## tar Extraction Gotcha

When tar is created with `-C /home/ubuntu/.hermes` and contains paths like `skills/`, extract into `~/.hermes/`, not `~/`:
```bash
cd ~/.hermes && tar -xzf /tmp/hermes_config_sync.tar.gz
```
