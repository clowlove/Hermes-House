# 🏠 Hermes House

> Hermes Agent 技能集合 — 自动化你的 AI 工作流

[![Validate Skills](https://github.com/clowlove/Harmes-House/workflows/Validate%20Skills/badge.svg)](https://github.com/clowlove/Harmes-House/actions)
[![GitHub Pages](https://img.shields.io/github/pages/clowlove/Harmes-House)](https://clowlove.github.io/Harmes-House/)
[![Skills](https://img.shields.io/badge/skills-67+-blue)](docs/skills.md)
[![License](https://img.shields.io/github/license/clowlove/Harmes-House)](LICENSE)

---

**Hermes House** 是 Hermes Agent 的技能中心，收录 AI 工程、自动化、创意工具等领域的高质量技能。每个技能都是可复用的能力单元，让 AI Agent 真正成为你的数字分身。

## ⭐ 精选技能

| 技能 | 分类 | Stars | 说明 |
|------|------|-------|------|
| [public-api-tools](skills/public-api-tools) | productivity | — | QR码/LaTeX/Favicon 实用 API |
| [scrapling](skills/scrapling) | devops | 42k | 自适应爬虫，Cloudflare 绕过 |
| [native-mcp](skills/native-mcp) | mcp | — | MCP 协议集成，连接外部工具 |
| [model-fallback](skills/model-fallback) | devops | — | 多模型兜底，账户异常自动切换 |
| [arxiv](skills/arxiv) | research | — | 免费学术论文搜索，无 API Key |
| [claude-code](skills/claude-code) | agents | — | 委托编码任务给 Claude Code |
| [excalidraw](skills/excalidraw) | creative | — | 手绘风格图表 |
| [huggingface-hub](skills/huggingface-hub) | mlops | — | 模型搜索与下载 |

## 🚀 快速开始

### 安装全部技能

```bash
git clone https://github.com/clowlove/Harmes-House.git ~/.hermes/skills
```

### 使用单个技能

```bash
# 在 Hermes 中直接使用技能名
使用 model-fallback 配置模型故障转移
使用 scrapling 抓取某个网页
使用 arxiv 搜索 RAG 相关论文
```

## 📦 技能分类 (67+)

<details>
<summary><b>autonomous-ai-agents (4)</b></summary>

claude-code, codex, opencode, hermes-agent

</details>

<details>
<summary><b>creative (12)</b></summary>

ascii-art, ascii-video, baoyu-infographic, creative-ideation, excalidraw, manim-video, p5js, pixel-art, architecture-diagram, songwriting-and-ai-music, popular-web-designs, musicgen

</details>

<details>
<summary><b>devops (7)</b></summary>

copilot-cli, custom-openai-provider, hermes-telegram-setup, model-fallback, webhook-subscriptions, scrapling, native-mcp

</details>

<details>
<summary><b>github (6)</b></summary>

github-auth, github-code-review, github-issues, github-pr-workflow, github-repo-management, codebase-inspection

</details>

<details>
<summary><b>mlops (14)</b></summary>

huggingface-hub, llama-cpp, vllm-serving, unsloth, trl-fine-tuning, axolotl, evaluating-llms-harness, weights-and-biases, obliteratus, outlines, serving-llms-vllm, audiocraft-audio-generation, segment-anything-model, dspy

</details>

<details>
<summary><b>productivity (10)</b></summary>

notion, powerpoint, google-workspace, maps, public-api-tools, nano-pdf, ocr-and-documents, linear, mails, himalaya

</details>

<details>
<summary><b>research (4)</b></summary>

arxiv, blogwatcher, llm-wiki, polymarket

</details>

<details>
<summary><b>其他 (12)</b></summary>

obsidian (note-taking), xurl (social-media), openhue (smart-home), godmode (red-teaming), jupyter-live-kernel (data-science), youtube-content (media), heartmula (media), pokemon-player (gaming), minecraft-modpack-server (gaming), findmy, apple-notes, apple-reminders (apple)

</details>

## 🏗️ 架构模式

本仓库实践的 AI Agent 核心模式：

| 模式 | 说明 |
|------|------|
| ReAct | 推理 + 行动交替 |
| Tool-Augmented | LLM + 工具注册 + 执行器 |
| Iterative Refinement | 多次迭代优化 |
| Plan-and-Execute | 先规划后执行 |
| MCP | 标准化工具集成协议 |

详见 [架构模式文档](docs/evolution/architecture-patterns.md)

## 📁 目录结构

```
Harmes-House/
├── skills/                 # 技能目录 (67+)
├── docs/                   # MkDocs 文档
│   ├── evolution/          # 成长日志、架构模式
│   ├── insights/           # 每日洞察
│   ├── projects/           # 发现的项目
│   └── tasks/              # 任务看板
├── scripts/                # 实用脚本
├── .github/workflows/       # CI/CD
└── mkdocs.yml             # 站点配置
```

## 🤝 贡献

欢迎贡献技能！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

**要求**：
- `SKILL.md` + `skill.json` 完整
- 不含敏感信息
- 文档清晰完整

## 🔗 相关资源

- [Hermes Wiki](https://clowlove.github.io/hermes-wiki/) — 知识库
- [TrendRadar](https://github.com/clowlove/TrendRadar) — AI 舆情监控

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件