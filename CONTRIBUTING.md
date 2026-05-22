# Contributing Guide

Welcome! We're excited you're interested in contributing to Hermès Agent.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/clowlove/Harmes-House.git
cd Harmes-House

# 2. Install dependencies
npm install

# 3. Create feature branch
git checkout -b feat/your-feature-name
```

## Branch Strategy

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production code | PR + 1 approval |
| `develop` | Integration | PR required |
| `feature/*` | New features | Open |
| `fix/*` | Bug fixes | Open |

## Commit Format

```
type: description

Types: feat | fix | docs | style | refactor | test | chore
```

Examples:
```
feat: add new trend analysis skill
fix: resolve memory leak in cron jobs
docs: update contributing guide
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to your fork
5. **Open** a Pull Request
6. **Wait** for review
7. **Merge** after approval

## Code Standards

- Follow existing code style
- Add comments for complex logic
- Include SKILL.md for new skills
- Update docs if needed

## Testing

```bash
# Run tests
npm test

# Check linting
npm run lint
```

## Questions?

- GitHub Issues: Bug reports & feature requests
- Telegram: [Telegram Handle]

---

*Last Updated: 2026-05-17*