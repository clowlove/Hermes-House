# Hermès Reviewer

> 🤖 AI-powered automated code review for GitHub pull requests

[![GitHub App](https://img.shields.io/badge/GitHub%20App-Herm%C3%A8s%20Reviewer-orange?style=for-the-badge)](https://github.com/apps/hermes-reviewer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## Support This Project

If hermes-reviewer saves you time, consider buying me a coffee! ☕

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee)](https://www.[REDACTED])
[![GitHub Sponsor](https://img.shields.io/badge/GitHub%20Sponsor-fafbfc?style=for-the-badge&logo=github-sponsors)](https://github.com/sponsors/[REDACTED])

---

## Overview

Hermès Reviewer is a GitHub App that automatically reviews pull requests using AI. It analyzes code changes and posts helpful feedback directly on PRs.

## Features

- ✅ **Automated Code Review** - Gets AI-powered analysis on every PR
- ✅ **Multiple Review Categories** - Issues, suggestions, and security concerns
- ✅ **Easy Integration** - One-click GitHub App installation
- ✅ **Privacy First** - Your code is only used for review, never stored

## How It Works

1. Install the GitHub App on your repository
2. Create or update a pull request
3. Hermès Reviewer automatically analyzes the changes
4. Within seconds, a detailed review comment appears on your PR

## Installation

### GitHub Marketplace

1. Visit [Hermès Reviewer on GitHub Marketplace](https://github.com/marketplace/hermes-reviewer)
2. Select your plan (Free tier available!)
3. Install on your account or organization
4. Grant access to the repositories you want to review

### Manual Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/apps)
2. Create a new GitHub App
3. Set the webhook URL to your server
4. Generate and save the private key
5. Install the app on your repositories

## Configuration

Set these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_APP_ID` | GitHub App ID | Yes |
| `GH_APP_PRIVATE_KEY` | Private key (replace \\n with newlines) | Yes |
| `WEBHOOK_SECRET` | Webhook secret for verification | Yes |
| `MODEL_BASE_URL` | AI model API endpoint | Yes |
| `MODEL_API_KEY` | API key for AI model | Yes |
| `INSTALLATION_ID` | GitHub App installation ID | Yes |

## Development

```bash
# Install dependencies
npm install

# Run locally
npm start

# Run tests
npm test
```

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Free | $0/mo | 10 reviews/month, 1 repo |
| Pro | $9/mo | Unlimited reviews, unlimited repos |
| Team | $29/mo | Everything + priority support |

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## Sponsorship

If this project saves you time and you want to support ongoing development:

☕ **[Buy Me a Coffee](https://www.[REDACTED])** — 一杯咖啡就是最大的鼓励

❤️ **[GitHub Sponsors](https://github.com/sponsors/[REDACTED])** — 长期支持开源

---

## License

MIT © Hermès Agent