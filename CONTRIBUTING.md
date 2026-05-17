# Contributing to Hermès House

🎉 Thank you for your interest in contributing! We're excited to have you.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

---

## 🚀 Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Harmes-House.git
cd Harmes-House

# 2. Add upstream remote
git remote add upstream https://github.com/clowlove/Harmes-House.git

# 3. Create your branch
git checkout -b feat/your-feature-name

# 4. Make your changes
# ... implement your changes ...

# 5. Test locally
npm test

# 6. Push and create PR
git push origin feat/your-feature-name
```

---

## 🛠️ Development Setup

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 22.x |
| npm | 10.x |
| Git | Latest |

### Installation

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### Verify Setup

```bash
# Run tests
npm test

# Start development server
npm run dev
```

---

## ✏️ Making Changes

### Branch Naming

| Type | Example |
|------|---------|
| Feature | `feat/add-new-skill` |
| Bug Fix | `fix/memory-leak` |
| Documentation | `docs/update-readme` |
| Refactor | `refactor/skill-loader` |
| Chore | `chore/update-deps` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new trendradar skill
fix: resolve memory leak in cron jobs  
docs: update contributing guide
style: format code with prettier
refactor: improve skill loading performance
test: add tests for github integration
chore: update dependencies
```

### Commit Format

```
type(scope): description

[optional body]

[optional footer]
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Sync with upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**
   ```bash
   npm test
   npm run lint
   ```

3. **Update documentation** if needed

4. **Squash commits** if you have many small commits

### PR Description

Include:
- **Summary** — What does this PR do?
- **Motivation** — Why this change?
- **Changes** — List the specific changes
- **Screenshots** — If UI changes
- **Testing** — How was this tested?

### Review Process

1. Maintainer reviews your PR
2. Address any feedback
3. Once approved, squash and merge

---

## 📏 Coding Standards

### JavaScript/TypeScript

- Use 2 spaces for indentation
- Use semicolons
- Maximum line length: 100 characters
- Use `const` and `let`, avoid `var`

### Python

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black)

### Documentation

- Use Markdown for all docs
- Keep lines under 100 characters
- Include code examples when relevant

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch

# Specific test file
npm test -- tests/skills/trendradar.test.js
```

### Test Structure

```javascript
describe('Skill: trendradar', () => {
  it('should fetch latest news', async () => {
    const result = await skill.execute({ action: 'latest' });
    expect(result).toHaveProperty('news');
  });
  
  it('should handle errors gracefully', async () => {
    const result = await skill.execute({ invalid: true });
    expect(result).toHaveProperty('error');
  });
});
```

---

## 📖 Documentation

### When to Update Docs

- Adding new features
- Changing existing behavior
- Adding new skills
- Updating configuration

### Doc Structure

```
docs/
├── index.md              # Documentation home
├── getting-started.md     # Quick start guide
├── skills/               # Skill documentation
│   └── SKILL.md         # Each skill has SKILL.md
├── tutorials/            # Step-by-step guides
└── api/                  # API references
```

---

## 💬 Community

### Where to Get Help

- **GitHub Discussions** — For questions and ideas
- **GitHub Issues** — For bugs and features
- **Telegram** — @Talkcn

### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<p align="center">

**Thank you for making Hermès House better!** 💖

</p>