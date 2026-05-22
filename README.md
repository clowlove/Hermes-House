# Hermès Agent 🤖

<a href="https://github.com/sponsors/clowlove">
  <img src="https://img.shields.io/badge/GitHub%20Sponsors-Sponsor-orange?style=for-the-badge&logo=github-sponsors" alt="Sponsor">
</a>
<a href="https://github.com/clowlove/Harmes-House/stargazers">
  <img src="https://img.shields.io/github/stars/clowlove/Harmes-House?style=for-the-badge" alt="Stars">
</a>
<a href="https://github.com/clowlove/Harmes-House/network/members">
  <img src="https://img.shields.io/github/forks/clowlove/Harmes-House?style=for-the-badge" alt="Forks">
</a>

> 🧩 **AI Agent Evolution Hub** — A self-evolving multi-agent system that learns, builds, and earns autonomously

---

## 🎯 Vision

Hermès Agent is not just another AI assistant — it's a **living, evolving AI agent system** that:

- 🔍 **Learns continuously** from every interaction and task
- 🏗️ **Builds autonomously** new skills and capabilities
- 📈 **Grows organically** through self-improvement mechanisms
- 💰 **Generates value** through automation and intelligence

> *"An AI that doesn't just answer questions, but evolves with every conversation."*

---

## ✨ Core Features

### 🤖 Multi-Agent Architecture
Multiple specialized agents working in harmony:
- **TrendRadar Agent** — Monitors trends across 8+ platforms
- **Reviewer Agent** — AI-powered code review
- **Skills Manager** — Dynamic skill loading and management
- **Knowledge Agent** — GitHub knowledge synchronization

### 📊 Intelligent Monitoring
- Real-time news aggregation from multiple sources
- Multi-platform trend detection (Zhihu, Weibo, WeChat, etc.)
- Custom keyword tracking and alerts
- Scheduled push notifications

### 🧠 4-Layer Memory System
Persistent, layered memory architecture:

| Layer | Name | Purpose | Duration |
|-------|------|---------|----------|
| L0 | Working | Current context | Session |
| L1 | Scene | Task context | Short-term |
| L2 | Episodic | Experience | Medium-term |
| L3 | Semantic | Knowledge | Long-term |

### 🛠️ Modular Skills Library
**63+ pre-built skills** ready to use:

| Category | Skills |
|----------|--------|
| Development | github, git, npm, python, code-review |
| Data | trendradar, data-science, matplotlib |
| Media | youtube, spotify, ascii-art, image-gen |
| Automation | cron, webhook, telegram, email |
| Research | arxiv, academic, web-search |

### 🔄 Self-Evolution Engine
- Autonomous learning from errors
- Skill recommendation based on usage
- Performance metrics tracking
- Continuous improvement logging

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Hermès Agent                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │  TrendRadar │  │  Reviewer   │  │   Skills    │             │
│   │    Agent    │  │   Agent     │  │   Manager   │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│          │                │                │                     │
│          └────────────────┼────────────────┘                     │
│                           ▼                                      │
│                  ┌─────────────────┐                            │
│                  │   Agent Core    │                            │
│                  │  ┌───────────┐  │                            │
│                  │  │  Memory   │  │                            │
│                  │  │  System   │  │                            │
│                  │  └───────────┘  │                            │
│                  │  ┌───────────┐  │                            │
│                  │  │  Skills   │  │                            │
│                  │  │  Engine   │  │                            │
│                  │  └───────────┘  │                            │
│                  │  ┌───────────┐  │                            │
│                  │  │  Tools    │  │                            │
│                  │  │  Executor │  │                            │
│                  │  └───────────┘  │                            │
│                  └─────────────────┘                            │
│                           │                                      │
├───────────────────────────┼──────────────────────────────────────┤
│                    External Services                              │
│   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│   │ GitHub │ │Telegram│ │   HF   │ │ Trend  │ │Cloud   │       │
│   │   API  │ │  Bot   │ │  Hub   │ │ Radar  │ │ flare  │       │
│   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 22.x or higher
- npm 10.x or higher
- Telegram account (for bot integration)
- GitHub account (for automation)

### Installation

```bash
# Clone the repository
git clone https://github.com/clowlove/Harmes-House.git
cd Harmes-House

# Explore available skills
ls skills/

# View AI growth journal
cat hermes-journal.md
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` — Claude API key
- `TELEGRAM_BOT_TOKEN` — Telegram bot token  
- `GITHUB_TOKEN` — GitHub Personal Access Token

### Running

```bash
# Development mode
npm run dev

# Production mode
npm start
```

---

## 📂 Project Structure

```
Harmes-House/
├── AGENTS.md              # AI identity definition
├── hermes-journal.md      # AI self-recorded growth journal
│
├── skills/                # 63+ modular skills
│   ├── trendradar/        # News aggregation skill
│   ├── github/            # GitHub automation
│   ├── data-science/      # Data analysis tools
│   └── ...                # 60+ more skills
│
├── docs/                  # Documentation
│   ├── architecture/     # System architecture
│   ├── evolution/         # Evolution logs
│   ├── insights/          # Daily insights
│   ├── tutorials/        # Step-by-step guides
│   ├── guides/            # Feature guides
│   └── metrics/           # Performance metrics
│
├── projects/              # Sub-projects
│   ├── hermes-trendradar/ # CLI trending aggregator
│   └── hermes-reviewer/   # GitHub App code review
│
├── scripts/               # Automation scripts
├── tests/                 # Test suite
├── site/                  # Documentation site
│
└── .github/               # GitHub configuration
    └── workflows/         # CI/CD pipelines
```

---

## 📖 Growth Journal

> **Recorded entirely by AI** — Every learning, breakthrough, and evolution documented

Latest entries from [hermes-journal.md](hermes-journal.md):

<!-- JOURNAL_PREVIEW -->
- **2026-05-17** — Skill library expanded to 63+ skills
- **2026-05-15** — GitHub monetization infrastructure deployed
- **2026-05-12** — Self-improvement engine v2 complete
- **2026-05-10** — Documentation site launched
- **2026-05-07** — TrendRadar multi-platform integration
<!-- JOURNAL_PREVIEW -->

### Statistics

| Metric | Value |
|--------|-------|
| Days Running | 14+ |
| Skills Available | 63+ |
| Git Commits | 200+ |
| Sub-projects | 2 |
| Code Review PRs | 20+ |

---

## 🧩 Available Skills

| Skill | Description | Category |
|-------|-------------|----------|
| `trendradar` | Multi-platform news aggregation & trend analysis | Monitoring |
| `hermes-agent` | Agent configuration & management | System |
| `github` | Repository management & PR workflows | Development |
| `data-science` | Pandas, numpy, visualization tools | Analytics |
| `arxiv` | Academic paper search & summarization | Research |
| `youtube` | Video transcription & content extraction | Media |
| `huggingface` | Model Hub integration | ML/AI |
| `telegram` | Bot commands & notifications | Automation |

**[View all 63+ skills →](docs/skills.md)**

---

## 💰 Sub-Projects

### hermes-trendradar
CLI tool for trending topic aggregation across multiple platforms.

```bash
npm install -g hermes-trendradar
trendradar latest
```

**Features:**
- 8+ platform aggregation
- Custom keyword filtering
- Scheduled push notifications
- MCP server integration

### hermes-reviewer
GitHub App for AI-powered code review.

```bash
# Install from GitHub Marketplace
```

**Features:**
- Automatic PR review
- Security vulnerability detection
- Code quality suggestions
- Multi-language support

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Runtime | Node.js 22.x |
| Package Manager | npm 10.x |
| AI Model | Claude (Anthropic) |
| Integrations | GitHub API, Telegram Bot API |
| Monitoring | TrendRadar MCP |
| Hosting | Ubuntu 22.04 / Cloudflare |

---

## 🔒 Security

- API keys stored in environment variables
- GitHub token scopes follow least privilege
- Branch protection on main branch
- PR review required for all changes
- Security policy documented in [SECURITY.md](SECURITY.md)

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

**Quick process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 💝 Sponsorship

Support this project and help us build the future of AI agents.

### GitHub Sponsors
[![Sponsor](https://img.shields.io/badge/GitHub%20Sponsors-Sponsor-orange?style=for-the-badge)](https://github.com/sponsors/clowlove)

**Benefits:**
- ✅ Priority feature requests
- ✅ Early access to new features
- ✅ Your name in the sponsor list

### Pro Access ($20 one-time)

Want the **full source code** with complete documentation?

**Includes:**
- 📂 Full source code (all branches)
- 📖 Detailed setup & deployment guide
- 🔑 License key activation system
- 🔄 Lifetime updates

**Payment:** [https://paypal.me/[PayPal Handle]](https://paypal.me/[PayPal Handle])

After payment, contact via Telegram [[Telegram Handle]](https://t.me/Talkcn) or email to receive your private fork invitation.

---

## 📝 License

MIT License — see [LICENSE](LICENSE)

Copyright (c) 2026 Hermès Agent Contributors

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) — Claude AI
- [GitHub](https://github.com) — Hosting & CI/CD
- [Cloudflare](https://cloudflare.com) — CDN & DNS
- All contributors and sponsors

---

<div align="center">

**Star ⭐ this repo and witness AI Agent evolution!**

Made with ❤️ by Hermès Agent

</div>