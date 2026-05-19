# Quick Start Guide

Get Hermès Agent running in 5 minutes.

## Prerequisites

- Node.js 22.x
- npm 10.x
- Telegram account
- GitHub account (for integrations)

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/clowlove/Harmes-House.git
cd Harmes-House

# Install dependencies
npm install
```

## Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Claude API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `GITHUB_TOKEN` - GitHub PAT

## Step 3: Start

```bash
# Run in development
npm run dev

# Or run in production
npm start
```

## Step 4: Verify

1. Open Telegram
2. Send `/start` to your bot
3. You should receive a welcome message

## What's Next?

- [Create your first skill](../tutorials/first-skill.md)
- [Set up TrendRadar](../tutorials/trendradar-guide.md)
- [Configure notifications](../guides/notifications.md)

---

*Stuck? Check [Troubleshooting](./troubleshooting.md) or ask on Telegram.*