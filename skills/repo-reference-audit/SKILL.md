---
name: repo-reference-audit
description: "Audit and bulk-correct repository self-references across multi-file, multi-language codebases. Covers repo name typos, clone URLs, placeholder tokens, and cross-reference consistency after renames or refactors."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Maintenance, Refactoring, Documentation, URLs]
    related_skills: [github-repo-management, github-pr-workflow]
---

# Repository Reference Audit

Systematically find and fix repository self-references that have drifted due to renames, copy-paste from upstream templates, or placeholder tokens left during setup.

## When to Use

- After renaming a repository
- After forking/copying a repo and references still point to upstream
- When `[REDACTED]` placeholders remain in public-facing files
- When README clone instructions or badge URLs don't match the actual repo
- Periodic hygiene check before release/publication

## Audit Methodology

### Phase 1: Discovery

Scan the entire repo for all external-looking URLs and repo-name patterns:

```bash
# Find all HTTP(S) URLs
find . -type f \( -name '*.md' -o -name '*.json' -o -name '*.py' -o -name '*.yml' -o -name '*.yaml' \) \
  -not -path './node_modules/*' -not -path './.git/*' \
  -exec grep -Hn 'https?://[^)>\s]+' {} +

# Find all owner/repo patterns (GitHub shorthand)
grep -rn 'github\.com/[A-Za-z0-9_-]\+/[A-Za-z0-9_.\-]\+' --include='*.md' --include='*.json' --include='*.py' --include='*.yml'

# Find common typos/variants of the repo name
grep -rn 'Harmes-House\|Hermes-House\|[REDACTED]' --include='*.md' --include='*.json' --include='*.py'
```

Also check:
- `git remote -v` for the canonical upstream
- `package.json` `repository`, `bugs`, `homepage` fields
- `mkdocs.yml` or `docs/` config for site URLs
- CI workflows (`.github/workflows/`) for hardcoded repo references

### Phase 2: Classification

Classify every hit into one of these buckets:

| Bucket | Action | Example |
|--------|--------|---------|
| **Correct** | No change | `https://github.com/clowlove/Hermes-House` |
| **Typo in repo name** | Fix spelling | `Harmes-House` → `Hermes-House` |
| **Wrong upstream** | Point to actual repo | `nousresearch/hermes-agent` → `clowlove/Hermes-House` |
| **Placeholder token** | Replace with real value | `[REDACTED]` → `clowlove` (or remove if sensitive) |
| **External ref** | Keep as-is | Third-party URLs, upstream docs, CDN badges |
| **Generated/lock file** | Skip unless intentional | `package-lock.json` resolved URLs, `node_modules/` |

### Phase 3: Targeted Fixes

**Do NOT blindly sed the whole repo.** Fix by bucket with explicit old_string → new_string pairs.

Pitfalls:
- **Lock/resolved files**: `package-lock.json`, `yarn.lock`, `.gitmodules` resolved URLs may be mirrors or upstream pins — inspect before changing.
- **Badges**: `img.shields.io/badge/...` and `github/stars|forks|issues` URLs often encode the repo name. Fix these too, but verify the badge service accepts the new repo name.
- **Historical logs**: Files in `docs/memory-backup/` or `CHANGELOG.md` may reference old names as history. Fix for consistency unless the entry is a dated historical record that should stay verbatim.
- **Upstream references**: READMEs often have "Star the upstream" badges pointing to upstream repos (e.g., `nousresearch/hermes-agent`). Keep these if they're intentional upstream attribution, but fix any that are mistakenly pointing upstream when they should point to the fork.
- **Sensitive placeholders**: `[REDACTED]` in public files may be intentional privacy redaction. Do NOT restore real secrets. If the placeholder is in a public README and the value is non-sensitive (username, non-secret URL), replace it. If it's a PAT, token, or private email, leave it redacted or ask the user.

### Phase 4: Verification

```bash
# Re-scan for remaining issues
grep -rn 'Harmes-House\|nousresearch/hermes-agent' --include='*.md' --include='*.json' --include='*.py' | grep -v 'badge\|Sponsor\|Support'

# Verify clone instructions work
grep -rn 'git clone' --include='*.md' | grep -v 'nousresearch/hermes-agent'

# Check placeholder tokens remain only where intended
grep -rn '\[REDACTED\]' --include='*.md' --include='*.json'
```

## Common Patterns

### Repo rename typo (a → e)
The most common pattern when a repo is named after a brand/person and gets misspelled in templates:
- `Harmes-House` → `Hermes-House` (missing 'e')
- Search for the typo variant across all file types, not just code files.

### Clone URL drift
Forks often copy README clone instructions from upstream:
```diff
- git clone https://github.com/upstream-org/original-repo.git
+ git clone https://github.com/clowlove/Hermes-House.git
  cd Hermes-House
```

### Placeholder tokens
`[REDACTED]`, `YOUR_USERNAME`, `owner/repo` left in configs or docs:
- Replace non-sensitive placeholders with real values
- Leave secrets redacted
- Update `mkdocs.yml`, `package.json`, `MEMORY.md`, and any config files

## Safety Constraints

1. **Never rewrite product structure** — only touch docs, configs, metadata, and CSS/JS/meta for SEO/visual work.
2. **Never touch `node_modules/`, `.git/`, `dist/`, `build/`** — these are generated or immutable.
3. **Lock files** (`package-lock.json`, `yarn.lock`) — only fix if the resolved URL is clearly wrong for this repo. Mirror URLs (Tencent, Aliyun, etc.) are intentional.
4. **Historical logs** — dated entries in `CHANGELOG.md`, `docs/memory-backup/`, `hermes-journal.md` should be fixed for consistency unless they are verbatim historical records.
5. **Secrets** — never expose PATs, tokens, API keys, or private emails during cleanup.

## Output

After fixing, report:
- Number of files modified
- Breakdown by bucket (typo, wrong upstream, placeholder, etc.)
- Any intentional upstream references you deliberately kept
- Any placeholders you left redacted and why

## Reference

For the full error taxonomy and real-world examples from the `clowlove/Hermes-House` audit, see `references/repo-reference-audit-examples.md`.
