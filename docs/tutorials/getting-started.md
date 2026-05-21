# Quick Start Guide

Get Hermès Agent + the Harmes-House skill pack running in 5 minutes.

## Prerequisites

- Hermes Agent CLI
- Git + Bash
- Telegram account (optional)
- GitHub account / PAT (optional, for integrations)
- Node.js 22.x only for `projects/*` sub-projects

## Step 1: Installation

```bash
# Install Hermes Agent core
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Clone the Harmes-House skill/evolution hub
git clone https://github.com/clowlove/Harmes-House.git
cd Harmes-House

# Install recommended A+B skills into the active Hermes home
bash scripts/install.sh

# Optional install modes:
# bash scripts/install.sh --core      # 32 core skills
# bash scripts/install.sh --standard  # 78 recommended skills (default)
# bash scripts/install.sh --full      # all 101 skills
```

## Step 2: Configuration

```bash
# Copy environment template when using Telegram / GitHub integrations
cp .env.example .env

# Edit with your API keys
nano .env
```

Common environment variables:
- `ANTHROPIC_API_KEY` - Claude API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `GITHUB_TOKEN` - GitHub PAT
- `OPENROUTER_API_KEY` / `MINIMAX_API_KEY` - optional model providers

## Step 3: Start

```bash
# Start Hermes normally
hermes

# Or preload one or more installed skills
hermes -s hermes-agent,github-pr-workflow
```

## Step 4: Verify

```bash
hermes skills list
```

You should see Harmes-House skills available from your Hermes installation.

## What's Next?

- [Browse available skills](../skills.md)
- [Read the architecture patterns](../evolution/architecture-patterns.md)
- [Review the evolution log](../evolution/log-2026-05.md)

---

*Stuck? Run `hermes doctor` first, then check the repository issues or ask on Telegram.*