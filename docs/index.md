# Hermes House

> 🏠 Hermes Agent 技能仓库 — 自动化你的 AI 工作流

![Validate Skills](https://github.com/clowlove/Harmes-House/workflows/Validate%20Skills/badge.svg)
![GitHub Pages](https://img.shields.io/github/pages/clowlove/Harmes-House)
![Skills](https://img.shields.io/badge/skills-67+-blue)
![License](https://img.shields.io/github/license/clowlove/Harmes-House)

---

## ⭐ 精选技能

| 技能 | 分类 | 说明 |
|------|------|------|
| [public-api-tools](skills/public-api-tools) | productivity | QR码、LaTeX、Favicon 等实用 API |
| [native-mcp](skills/native-mcp) | mcp | MCP 协议集成，连接外部工具 |
| [model-fallback](skills/model-fallback) | devops | 多模型兜底，账户异常时自动切换 |
| [scrapling](skills/scrapling) | devops | 自适应爬虫，Cloudflare 绕过 |
| [hermes-telegram-setup](skills/hermes-telegram-setup) | devops | Telegram Bot 一键配置 |
| [arxiv](skills/arxiv) | research | 免费学术论文搜索，无需 API Key |
| [llm-wiki](skills/llm-wiki) | note-taking | LLM Wiki 知识库构建方法 |
| [huggingface-hub](skills/huggingface-hub) | mlops | Hugging Face 模型搜索下载 |

---

## 🔧 快速开始

### 方式一：安装全部技能

```bash
git clone https://github.com/clowlove/Harmes-House.git ~/.hermes/skills
```

### 方式二：安装单个技能

```bash
# 克隆仓库后复制，或直接复制单个技能目录
cp -r skills/model-fallback ~/.hermes/skills/devops/
```

### 方式三：在 Hermes Agent 中使用

```
使用 public-api-tools 生成一个 QR 码
使用 model-fallback 配置模型故障转移
使用 native-mcp 查看已配置的 MCP 服务器
```

---

## 📦 技能分类 (67+)

| 分类 | 数量 | 代表技能 |
|------|------|---------|
| **autonomous-ai-agents** | 4 | claude-code, codex, opencode, hermes-agent |
| **creative** | 12 | ascii-art, pixel-art, excalidraw, baoyu-infographic |
| **data-science** | 1 | jupyter-live-kernel |
| **devops** | 7 | model-fallback, scrapling, copilot-cli, hermes-telegram-setup |
| **email** | 2 | mails, himalaya |
| **github** | 6 | github-pr-workflow, github-code-review, github-issues |
| **gaming** | 2 | pokemon-player, minecraft-modpack-server |
| **media** | 5 | youtube-content, heartmula, gif-search, songsee |
| **mlops** | 14 | huggingface-hub, llama-cpp, vllm-serving, unsloth |
| **note-taking** | 2 | obsidian, llm-wiki |
| **productivity** | 10 | notion, powerpoint, google-workspace, maps, public-api-tools |
| **red-teaming** | 1 | godmode |
| **research** | 4 | arxiv, blogwatcher, polymarket, research-paper-writing |
| **smart-home** | 1 | openhue |
| **social-media** | 1 | xurl |
| **software-development** | 6 | plan, systematic-debugging, test-driven-development |

---

## 🏗️ 架构模式

Harmes-House 实践的 AI Agent 核心模式：

| 模式 | 说明 |
|------|------|
| ReAct | 推理 + 行动交替 |
| Tool-Augmented | LLM + 工具注册 + 执行器 |
| Iterative Refinement | 多次迭代优化 |
| Skill-as-Unit | 技能作为 Agent 能力扩展单元 |
| MCP (Model Context Protocol) | 标准化工具集成协议 |

详见 [架构模式](evolution/architecture-patterns.md)

---

## 🚀 CI/CD 自动化

- ✅ `validate.yml` — 每次推送验证 SKILL.md + skill.json 结构
- ✅ `deploy-pages.yml` — MkDocs 自动部署到 GitHub Pages
- ✅ `auto-merge.yml` — 通过 CI 后自动 squash 合并
- ✅ `dependabot.yml` — 自动更新依赖

---

## 🤝 贡献

欢迎添加新技能！请阅读 [CONTRIBUTING.md](contributing.md)。

技能要求：
- 包含 `SKILL.md` 和 `skill.json`
- 不含敏感信息
- 文档完整清晰

---

## 📚 相关资源

- [Hermes Wiki](https://clowlove.github.io/hermes-wiki/) — 知识库
- [TrendRadar](https://github.com/clowlove/TrendRadar) — AI 舆情监控

---

Licensed under MIT. Built with ❤️ for Hermes Agent.