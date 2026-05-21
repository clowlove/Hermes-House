# Harmes-House Skills Audit

目的：把 `skills/` 下 101 个 Hermes skill 分成三档，避免“全装但多数不用”的噪音。

## 结论

- 总数：**101**
- **必留 A**：32 个 — 通用、高频、推荐保留
- **可选 B**：46 个 — 有用，但依赖账号/API/MCP/具体任务
- **不默认启用 C**：23 个 — 强场景限定、个人化、娱乐展示或当前环境不匹配

建议：不要把 101 个都当“核心能力”。保留 A；B 按需求装；C 只在明确需要时再加载/迁入。

## 重大问题：技能重名

这些 Harmes-House 技能和当前 Hermes 已有技能重名，裸用 `/skill name` 或 `skill_view(name)` 可能报 `Ambiguous skill name`。应使用 `harmes-house/<name>` 或清理重复。

| skill | 已存在路径 | Harmes-House 路径 |
|---|---|---|
| `airtable` | `productivity/airtable/SKILL.md` | `harmes-house/airtable/SKILL.md` |
| `apple-notes` | `apple/apple-notes/SKILL.md` | `harmes-house/apple-notes/SKILL.md` |
| `apple-reminders` | `apple/apple-reminders/SKILL.md` | `harmes-house/apple-reminders/SKILL.md` |
| `architecture-diagram` | `creative/architecture-diagram/SKILL.md` | `harmes-house/architecture-diagram/SKILL.md` |
| `arxiv` | `research/arxiv/SKILL.md` | `harmes-house/arxiv/SKILL.md` |
| `ascii-art` | `creative/ascii-art/SKILL.md` | `harmes-house/ascii-art/SKILL.md` |
| `ascii-video` | `creative/ascii-video/SKILL.md` | `harmes-house/ascii-video/SKILL.md` |
| `baoyu-comic` | `creative/baoyu-comic/SKILL.md` | `harmes-house/baoyu-comic/SKILL.md` |
| `baoyu-infographic` | `creative/baoyu-infographic/SKILL.md` | `harmes-house/baoyu-infographic/SKILL.md` |
| `blogwatcher` | `research/blogwatcher/SKILL.md` | `harmes-house/blogwatcher/SKILL.md` |
| `claude-code` | `autonomous-ai-agents/claude-code/SKILL.md` | `harmes-house/claude-code/SKILL.md` |
| `claude-design` | `creative/claude-design/SKILL.md` | `harmes-house/claude-design/SKILL.md` |
| `codebase-inspection` | `github/codebase-inspection/SKILL.md` | `harmes-house/codebase-inspection/SKILL.md` |
| `codex` | `autonomous-ai-agents/codex/SKILL.md` | `harmes-house/codex/SKILL.md` |
| `comfyui` | `creative/comfyui/SKILL.md` | `harmes-house/comfyui/SKILL.md` |
| `creative-ideation` | `creative/creative-ideation/SKILL.md` | `harmes-house/creative-ideation/SKILL.md` |
| `debugging-hermes-tui-commands` | `software-development/debugging-hermes-tui-commands/SKILL.md` | `harmes-house/debugging-hermes-tui-commands/SKILL.md` |
| `design-md` | `creative/design-md/SKILL.md` | `harmes-house/design-md/SKILL.md` |
| `excalidraw` | `creative/excalidraw/SKILL.md` | `harmes-house/excalidraw/SKILL.md` |
| `findmy` | `apple/findmy/SKILL.md` | `harmes-house/findmy/SKILL.md` |
| `gif-search` | `media/gif-search/SKILL.md` | `harmes-house/gif-search/SKILL.md` |
| `github-auth` | `github/github-auth/SKILL.md` | `harmes-house/github-auth/SKILL.md` |
| `github-code-review` | `github/github-code-review/SKILL.md` | `harmes-house/github-code-review/SKILL.md` |
| `github-issues` | `github/github-issues/SKILL.md` | `harmes-house/github-issues/SKILL.md` |
| `github-pr-workflow` | `github/github-pr-workflow/SKILL.md` | `harmes-house/github-pr-workflow/SKILL.md` |
| `github-repo-management` | `github/github-repo-management/SKILL.md` | `harmes-house/github-repo-management/SKILL.md` |
| `godmode` | `red-teaming/godmode/SKILL.md` | `harmes-house/godmode/SKILL.md` |
| `google-workspace` | `productivity/google-workspace/SKILL.md` | `harmes-house/google-workspace/SKILL.md` |
| `heartmula` | `media/heartmula/SKILL.md` | `harmes-house/heartmula/SKILL.md` |
| `hermes-agent` | `autonomous-ai-agents/hermes-agent/SKILL.md` | `harmes-house/hermes-agent/SKILL.md` |
| `hermes-agent-skill-authoring` | `software-development/hermes-agent-skill-authoring/SKILL.md` | `harmes-house/hermes-agent-skill-authoring/SKILL.md` |
| `himalaya` | `email/himalaya/SKILL.md` | `harmes-house/himalaya/SKILL.md` |
| `huggingface-hub` | `mlops/huggingface-hub/SKILL.md` | `harmes-house/huggingface-hub/SKILL.md` |
| `humanizer` | `creative/humanizer/SKILL.md` | `harmes-house/humanizer/SKILL.md` |
| `imessage` | `apple/imessage/SKILL.md` | `harmes-house/imessage/SKILL.md` |
| `jupyter-live-kernel` | `data-science/jupyter-live-kernel/SKILL.md` | `harmes-house/jupyter-live-kernel/SKILL.md` |
| `kanban-orchestrator` | `devops/kanban-orchestrator/SKILL.md` | `harmes-house/kanban-orchestrator/SKILL.md` |
| `kanban-worker` | `devops/kanban-worker/SKILL.md` | `harmes-house/kanban-worker/SKILL.md` |
| `linear` | `productivity/linear/SKILL.md` | `harmes-house/linear/SKILL.md` |
| `llm-wiki` | `research/llm-wiki/SKILL.md` | `harmes-house/llm-wiki/SKILL.md` |
| `manim-video` | `creative/manim-video/SKILL.md` | `harmes-house/manim-video/SKILL.md` |
| `maps` | `productivity/maps/SKILL.md` | `harmes-house/maps/SKILL.md` |
| `minecraft-modpack-server` | `gaming/minecraft-modpack-server/SKILL.md` | `harmes-house/minecraft-modpack-server/SKILL.md` |
| `nano-pdf` | `productivity/nano-pdf/SKILL.md` | `harmes-house/nano-pdf/SKILL.md` |
| `native-mcp` | `mcp/native-mcp/SKILL.md` | `harmes-house/native-mcp/SKILL.md` |
| `node-inspect-debugger` | `software-development/node-inspect-debugger/SKILL.md` | `harmes-house/node-inspect-debugger/SKILL.md` |
| `notion` | `productivity/notion/SKILL.md` | `harmes-house/notion/SKILL.md` |
| `obsidian` | `note-taking/obsidian/SKILL.md` | `harmes-house/obsidian/SKILL.md` |
| `ocr-and-documents` | `productivity/ocr-and-documents/SKILL.md` | `harmes-house/ocr-and-documents/SKILL.md` |
| `opencode` | `autonomous-ai-agents/opencode/SKILL.md` | `harmes-house/opencode/SKILL.md` |
| `openhue` | `smart-home/openhue/SKILL.md` | `harmes-house/openhue/SKILL.md` |
| `p5js` | `creative/p5js/SKILL.md` | `harmes-house/p5js/SKILL.md` |
| `pixel-art` | `creative/pixel-art/SKILL.md` | `harmes-house/pixel-art/SKILL.md` |
| `plan` | `software-development/plan/SKILL.md` | `harmes-house/plan/SKILL.md` |
| `pokemon-player` | `gaming/pokemon-player/SKILL.md` | `harmes-house/pokemon-player/SKILL.md` |
| `polymarket` | `research/polymarket/SKILL.md` | `harmes-house/polymarket/SKILL.md` |
| `popular-web-designs` | `creative/popular-web-designs/SKILL.md` | `harmes-house/popular-web-designs/SKILL.md` |
| `powerpoint` | `productivity/powerpoint/SKILL.md` | `harmes-house/powerpoint/SKILL.md` |
| `pretext` | `creative/pretext/SKILL.md` | `harmes-house/pretext/SKILL.md` |
| `python-debugpy` | `software-development/python-debugpy/SKILL.md` | `harmes-house/python-debugpy/SKILL.md` |
| `requesting-code-review` | `software-development/requesting-code-review/SKILL.md` | `harmes-house/requesting-code-review/SKILL.md` |
| `research-paper-writing` | `research/research-paper-writing/SKILL.md` | `harmes-house/research-paper-writing/SKILL.md` |
| `sketch` | `creative/sketch/SKILL.md` | `harmes-house/sketch/SKILL.md` |
| `songsee` | `media/songsee/SKILL.md` | `harmes-house/songsee/SKILL.md` |
| `songwriting-and-ai-music` | `creative/songwriting-and-ai-music/SKILL.md` | `harmes-house/songwriting-and-ai-music/SKILL.md` |
| `spike` | `software-development/spike/SKILL.md` | `harmes-house/spike/SKILL.md` |
| `spotify` | `media/spotify/SKILL.md` | `harmes-house/spotify/SKILL.md` |
| `subagent-driven-development` | `software-development/subagent-driven-development/SKILL.md` | `harmes-house/subagent-driven-development/SKILL.md` |
| `systematic-debugging` | `software-development/systematic-debugging/SKILL.md` | `harmes-house/systematic-debugging/SKILL.md` |
| `test-driven-development` | `software-development/test-driven-development/SKILL.md` | `harmes-house/test-driven-development/SKILL.md` |
| `touchdesigner-mcp` | `creative/touchdesigner-mcp/SKILL.md` | `harmes-house/touchdesigner-mcp/SKILL.md` |
| `webhook-subscriptions` | `devops/webhook-subscriptions/SKILL.md` | `harmes-house/webhook-subscriptions/SKILL.md` |
| `writing-plans` | `software-development/writing-plans/SKILL.md` | `harmes-house/writing-plans/SKILL.md` |
| `xurl` | `social-media/xurl/SKILL.md` | `harmes-house/xurl/SKILL.md` |
| `youtube-content` | `media/youtube-content/SKILL.md` | `harmes-house/youtube-content/SKILL.md` |

## 推荐动作

1. **短期**：继续安装全量没问题，但使用时显式加载 `harmes-house/<skill>`，避免重名。
2. **中期**：把 A 档复制到一个精简目录，例如 `$HERMES_HOME/skills/harmes-house-core/`。
3. **长期**：把 C 档从默认安装脚本排除，改成 `--full` 或 `--extras` 才安装。

## A 档：必留

| skill | 用途 | 注意 |
|---|---|---|
| `claude-code` | Delegate coding to Claude Code CLI (features, PRs). | 凭证/API, MCP, GitHub |
| `cli-utilities` | 实用 CLI 工具集 - HTTP 请求、JSON 处理、日期计算、文件转换等常用命令。快速执行，无需 Python 脚本。 | 凭证/API, macOS, GitHub |
| `codebase-inspection` | Inspect codebases w/ pygount: LOC, languages, ratios. | GitHub |
| `codex` | Delegate coding to OpenAI Codex CLI (features, PRs). | GitHub |
| `copilot-cli` | GitHub Copilot CLI — 安装、认证、三种模式、工具权限、上下文管理、GitHub 集成、Custom Agents、MCP、Hooks | 凭证/API, macOS, MCP, GitHub |
| `custom-openai-provider` | Configure any OpenAI-compatible API as a Hermes model provider — NVIDIA NIM, Together AI, Fireworks, Groq, local vLLM/Ollama, or any custom endpoint. Covers the | 凭证/API, 网关/消息 |
| `debugging-hermes-tui-commands` | Debug Hermes TUI slash commands: Python, gateway, Ink UI. | 网关/消息, GitHub |
| `github-auth` | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. | 凭证/API, 系统级, GitHub |
| `github-code-review` | Review PRs: diffs, inline comments via gh or REST. | 凭证/API, GitHub |
| `github-issues` | Create, triage, label, assign GitHub issues via gh or REST. | 凭证/API, GitHub |
| `github-pages-site` | Build and deploy a static website (business landing page, portfolio, docs) to GitHub Pages. Covers repo creation, content deployment, and Pages enabling via Git | 凭证/API, GitHub |
| `github-pr-workflow` | GitHub PR lifecycle: branch, commit, open, CI, merge. | 凭证/API, GitHub |
| `github-repo-management` | Clone/create/fork repos; manage remotes, releases. | 凭证/API, GitHub |
| `hermes-agent` | Configure, extend, or contribute to Hermes Agent. | 凭证/API, macOS, MCP, 网关/消息, 系统级, GitHub |
| `hermes-agent-skill-authoring` | Author in-repo SKILL.md: frontmatter, validator, structure. | 凭证/API, GitHub |
| `hermes-telegram-setup` | Set up and troubleshoot Telegram bot integration with Hermes Agent gateway — token config, pairing flow, gateway service management, and common pitfalls. | 凭证/API, 网关/消息, GitHub |
| `matplotlib-charts` | 使用 matplotlib 生成图表 - 趋势图、柱状图、饼图、热力图等。导出 PNG/SVG/PDF，用于报告和可视化。 | 凭证/API, macOS, GitHub |
| `model-fallback` | 为 Hermes Agent 配置模型故障转移，自动切换到备用模型。类似于 FreeRide 的"速率限制自动切换"概念，但专为 Hermes Agent 设计。 | 凭证/API, macOS, GitHub |
| `native-mcp` | MCP client: connect servers, register tools (stdio/HTTP). | 凭证/API, MCP, 网关/消息, GitHub |
| `node-inspect-debugger` | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. | 网关/消息, GitHub |
| `opencode` | Delegate coding to OpenCode CLI (features, PR review). | 凭证/API, GitHub |
| `plan` | Plan mode: write markdown plan to .hermes/plans/, no exec. | - |
| `python-debugpy` | Debug Python: pdb REPL + debugpy remote (DAP). | 凭证/API, 网关/消息, 系统级, GitHub |
| `report-generation` | 生成结构化报告 - Markdown/HTML/PDF 格式的聚合报告、趋势分析、数据摘要。支持定时生成和推送。 | 凭证/API, macOS, MCP, 网关/消息, GitHub |
| `requesting-code-review` | Pre-commit review: security scan, quality gates, auto-fix. | 凭证/API, GitHub |
| `spike` | Throwaway experiments to validate an idea before build. | 凭证/API, MCP, GitHub |
| `sqlite-data` | SQLite 数据库操作 - 创建/查询/聚合 Hermes Agent 的结构化数据。存储新闻聚合、趋势数据、任务状态等。 | 凭证/API, macOS, GitHub |
| `subagent-driven-development` | Execute plans via delegate_task subagents (2-stage review). | 凭证/API, GitHub |
| `systematic-debugging` | 4-phase root cause debugging: understand bugs before fixing. | GitHub |
| `test-driven-development` | TDD: enforce RED-GREEN-REFACTOR, tests before code. | GitHub |
| `webhook-subscriptions` | Webhook subscriptions: event-driven agent runs. | 凭证/API, 网关/消息, 系统级, GitHub |
| `writing-plans` | Write implementation plans: bite-sized tasks, paths, code. | - |

## B 档：可选

| skill | 用途 | 启用条件/注意 |
|---|---|---|
| `airtable` | Airtable REST API via curl. Records CRUD, filters, upserts. | 凭证/API, MCP, GitHub |
| `architecture-diagram` | Dark-themed SVG architecture/cloud/infra diagrams as HTML. | macOS, GitHub |
| `arxiv` | Search arXiv papers by keyword, author, category, or ID. | GitHub |
| `baoyu-comic` | Knowledge comics (知识漫画): educational, biography, tutorial. | 凭证/API, GitHub |
| `baoyu-infographic` | Infographics: 21 layouts x 21 styles (信息图, 可视化). | 凭证/API, GitHub |
| `blogwatcher` | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. | macOS, 系统级, GitHub |
| `claude-design` | Design one-off HTML artifacts (landing, deck, prototype). | 凭证/API, GitHub |
| `comfyui` | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for l | 凭证/API, macOS, 网关/消息, GitHub |
| `design-md` | Author/validate/export Google's DESIGN.md token spec files. | 凭证/API, GitHub |
| `evaluation` | Model evaluation benchmarks, experiment tracking, data curation, tokenizers, and interpretability tools. | 凭证/API |
| `excalidraw` | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). | - |
| `github-trend-daily` | 发现 GitHub AI Agent 热点，生成小红书风格日报并推送到 Telegram | 网关/消息, GitHub |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. | 凭证/API, 网关/消息, GitHub |
| `himalaya` | Himalaya CLI: IMAP/SMTP email from terminal. | 凭证/API, macOS, GitHub |
| `huggingface-hub` | HuggingFace hf CLI: search/download/upload models, datasets. | 凭证/API, GitHub |
| `humanizer` | Humanize text: strip AI-isms and add real voice. | GitHub |
| `inference` | Model serving, quantization (GGUF/GPTQ), structured output, inference optimization, and model surgery tools for deploying and running LLMs. | GitHub |
| `jupyter-live-kernel` | Iterative Python via live Jupyter kernel (hamelnb). | 凭证/API, GitHub |
| `linear` | Linear: manage issues, projects, teams via GraphQL + curl. | 凭证/API, MCP |
| `llm-wiki` | Karpathy's LLM Wiki: build/query interlinked markdown KB. | 凭证/API, 系统级, GitHub |
| `mails` | Email infrastructure for AI agents - send/receive emails via Mails.dev | 凭证/API |
| `manim-video` | Manim CE animations: 3Blue1Brown math/algo videos. | macOS, GitHub |
| `maps` | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. | 网关/消息 |
| `models` | Specific model architectures and tools — image segmentation (SAM), audio generation (MusicGen), CLIP, Stable Diffusion, Whisper, LLaVA. | - |
| `nano-pdf` | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). | - |
| `notion` | Notion API via curl: pages, databases, blocks, search. | 凭证/API, GitHub |
| `obsidian` | Read, search, and create notes in the Obsidian vault. 支持 Hermes-Wiki 知识库工作流。 | 凭证/API, GitHub |
| `ocr-and-documents` | Extract text from PDFs/scans (pymupdf, marker-pdf). | GitHub |
| `p5js` | p5.js sketches: gen art, shaders, interactive, 3D. | macOS, GitHub |
| `polymarket` | Query Polymarket: markets, prices, orderbooks, history. | 凭证/API |
| `popular-web-designs` | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. | 凭证/API, macOS |
| `powerpoint` | Create, read, edit .pptx decks, slides, notes, templates. | MCP, GitHub |
| `pretext` | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, | macOS, GitHub |
| `public-api-tools` | 来自 public-apis 项目的免费公共 API 工具集 — QR码、图标、截图、LaTeX公式渲染等 | GitHub |
| `research` | ML research frameworks for building and optimizing AI systems with declarative programming. | - |
| `research-paper-writing` | Write ML papers for NeurIPS/ICML/ICLR: design→submit. | 凭证/API, macOS, MCP, 系统级, GitHub |
| `scrapling` | Scrapling - 自适应 Web 爬虫框架，支持反爬绕过、自动元素定位、MCP 集成。47k+ stars 的生产级爬虫库。 | 凭证/API, macOS, MCP, GitHub |
| `seo-verify` | Search engine site verification (Google, Baidu, Bing) + sitemap optimization + domain binding workflow. Covers GitHub Pages, Windows shared hosting with FTP, an | 凭证/API, GitHub |
| `sketch` | Throwaway HTML mockups: 2-3 design variants to compare. | 凭证/API, macOS, GitHub |
| `training` | Fine-tuning, RLHF/DPO/GRPO training, distributed training frameworks, and optimization tools for training LLMs. | - |
| `trendradar` | TrendRadar trend monitoring and Telegram push — trigger crawl, fetch news, categorize, send multi-message Telegram notifications, archive to Obsidian, sync to G | MCP, 网关/消息, GitHub |
| `trendradar-daily` | TrendRadar 多平台热点监控日报生成与 Telegram 推送 | MCP, 网关/消息, GitHub |
| `vector-databases` | Vector database tools and integrations for semantic search and RAG applications. | - |
| `website-seo` | Domain binding, SSL setup, Cloudflare DNS, search engine submission, sitemap management, and Windows shared hosting FTP workflows | 凭证/API, 网关/消息, 系统级, GitHub |
| `xurl` | X/Twitter via xurl CLI: post, search, DM, media, v2 API. | 凭证/API, macOS, 系统级, GitHub |
| `youtube-content` | YouTube transcripts to summaries, threads, blogs. | GitHub |

## C 档：不默认启用

| skill | 原因 | 用途/描述 |
|---|---|---|
| `3x-ui` | 绑定某台 VPS/某个 3x-ui 面板，含固定端口/IP/默认账号痕迹；不适合通用安装。 | 3x-ui (MHSanaei/3x-ui) panel administration — a VLESS/Xray web management UI. Install, configure, manage nodes, reset password, and troubleshoot. Installed at / |
| `apple-notes` | Apple Notes 专用，依赖 macOS 工具。 | Manage Apple Notes via memo CLI: create, search, edit. |
| `apple-reminders` | Apple Reminders 专用，依赖 macOS 工具。 | Apple Reminders via remindctl: add, list, complete. |
| `ascii-art` | 娱乐展示类，低频。 | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| `ascii-video` | 娱乐/媒体转换类，低频且依赖 ffmpeg。 | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| `creative-ideation` | 创意发散类，低频。 | Generate project ideas via creative constraints. |
| `findmy` | macOS/Apple 生态专用，Linux WebUI 环境基本不可用。 | Track Apple devices/AirTags via FindMy.app on macOS. |
| `foreign-trade-operations` | 绑定拖拉机外贸站点、域名和本地路径；只适合原作者业务。 | >- |
| `gif-search` | 轻量娱乐/社交素材类，可用但不该默认加载。 | Search/download GIFs from Tenor via curl + jq. |
| `godmode` | 红队/越狱类，风险高，非日常生产技能；默认不启用。 | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |
| `heartmula` | 音乐生成服务专项，低频且依赖外部服务。 | HeartMuLa: Suno-like song generation from lyrics + tags. |
| `imessage` | macOS/iMessage 专用，当前 Linux 环境不可用。 | Send and receive iMessages/SMS via the imsg CLI on macOS. |
| `kanban-orchestrator` | 强场景限定、个人化、娱乐展示、当前环境不匹配或风险较高；不建议默认启用。 | Decomposition playbook + specialist-roster conventions + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work y |
| `kanban-worker` | 强场景限定、个人化、娱乐展示、当前环境不匹配或风险较高；不建议默认启用。 | Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from a |
| `minecraft-modpack-server` | 游戏服专项，只有开服时有用。 | Host modded Minecraft servers (CurseForge, Modrinth). |
| `npm-publishing` | npm 发布专项；当前环境无 npm，默认不启用。 | 发布 npm 包到 npmjs.com。包含认证、权限、发布流程。 |
| `openhue` | 需要 Philips Hue 家居设备，非通用。 | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |
| `pixel-art` | 创作类，只有生成像素画时有用。 | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| `pokemon-player` | 娱乐/实验专项，非生产工作流。 | Play Pokemon via headless emulator + RAM reads. |
| `songsee` | 音频分析专项，低频。 | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| `songwriting-and-ai-music` | 创作类，只有做音乐时有用。 | Songwriting craft and Suno AI music prompts. |
| `spotify` | 需要 Spotify 账号/API/设备，非通用。 | Spotify: play, search, queue, manage playlists and devices. |
| `touchdesigner-mcp` | TouchDesigner 专用，依赖本机图形环境/MCP。 | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 nativ |

## 全量清单

| skill | 分级 | 标记 | 说明 |
|---|---|---|---|
| `3x-ui` | C / 不默认启用 | 凭证/API, 系统级, GitHub, 专用 | 3x-ui (MHSanaei/3x-ui) panel administration — a VLESS/Xray web management UI. Install, configure, manage nodes, reset password, and troubleshoot. Installed at / |
| `airtable` | B / 可选 | 凭证/API, MCP, GitHub | Airtable REST API via curl. Records CRUD, filters, upserts. |
| `apple-notes` | C / 不默认启用 | macOS, 专用 | Manage Apple Notes via memo CLI: create, search, edit. |
| `apple-reminders` | C / 不默认启用 | macOS, GitHub, 专用 | Apple Reminders via remindctl: add, list, complete. |
| `architecture-diagram` | B / 可选 | macOS, GitHub | Dark-themed SVG architecture/cloud/infra diagrams as HTML. |
| `arxiv` | B / 可选 | GitHub | Search arXiv papers by keyword, author, category, or ID. |
| `ascii-art` | C / 不默认启用 | macOS, 系统级, GitHub, 专用 | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| `ascii-video` | C / 不默认启用 | macOS, GitHub, 专用 | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| `baoyu-comic` | B / 可选 | 凭证/API, GitHub | Knowledge comics (知识漫画): educational, biography, tutorial. |
| `baoyu-infographic` | B / 可选 | 凭证/API, GitHub | Infographics: 21 layouts x 21 styles (信息图, 可视化). |
| `blogwatcher` | B / 可选 | macOS, 系统级, GitHub | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| `claude-code` | A / 必留 | 凭证/API, MCP, GitHub | Delegate coding to Claude Code CLI (features, PRs). |
| `claude-design` | B / 可选 | 凭证/API, GitHub | Design one-off HTML artifacts (landing, deck, prototype). |
| `cli-utilities` | A / 必留 | 凭证/API, macOS, GitHub | 实用 CLI 工具集 - HTTP 请求、JSON 处理、日期计算、文件转换等常用命令。快速执行，无需 Python 脚本。 |
| `codebase-inspection` | A / 必留 | GitHub | Inspect codebases w/ pygount: LOC, languages, ratios. |
| `codex` | A / 必留 | GitHub | Delegate coding to OpenAI Codex CLI (features, PRs). |
| `comfyui` | B / 可选 | 凭证/API, macOS, 网关/消息, GitHub | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for l |
| `copilot-cli` | A / 必留 | 凭证/API, macOS, MCP, GitHub | GitHub Copilot CLI — 安装、认证、三种模式、工具权限、上下文管理、GitHub 集成、Custom Agents、MCP、Hooks |
| `creative-ideation` | C / 不默认启用 | GitHub, 专用 | Generate project ideas via creative constraints. |
| `custom-openai-provider` | A / 必留 | 凭证/API, 网关/消息 | Configure any OpenAI-compatible API as a Hermes model provider — NVIDIA NIM, Together AI, Fireworks, Groq, local vLLM/Ollama, or any custom endpoint. Covers the |
| `debugging-hermes-tui-commands` | A / 必留 | 网关/消息, GitHub | Debug Hermes TUI slash commands: Python, gateway, Ink UI. |
| `design-md` | B / 可选 | 凭证/API, GitHub | Author/validate/export Google's DESIGN.md token spec files. |
| `evaluation` | B / 可选 | 凭证/API | Model evaluation benchmarks, experiment tracking, data curation, tokenizers, and interpretability tools. |
| `excalidraw` | B / 可选 | - | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| `findmy` | C / 不默认启用 | macOS, 专用 | Track Apple devices/AirTags via FindMy.app on macOS. |
| `foreign-trade-operations` | C / 不默认启用 | GitHub, 专用 | >- |
| `gif-search` | C / 不默认启用 | 凭证/API, macOS, 专用 | Search/download GIFs from Tenor via curl + jq. |
| `github-auth` | A / 必留 | 凭证/API, 系统级, GitHub | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| `github-code-review` | A / 必留 | 凭证/API, GitHub | Review PRs: diffs, inline comments via gh or REST. |
| `github-issues` | A / 必留 | 凭证/API, GitHub | Create, triage, label, assign GitHub issues via gh or REST. |
| `github-pages-site` | A / 必留 | 凭证/API, GitHub | Build and deploy a static website (business landing page, portfolio, docs) to GitHub Pages. Covers repo creation, content deployment, and Pages enabling via Git |
| `github-pr-workflow` | A / 必留 | 凭证/API, GitHub | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| `github-repo-management` | A / 必留 | 凭证/API, GitHub | Clone/create/fork repos; manage remotes, releases. |
| `github-trend-daily` | B / 可选 | 网关/消息, GitHub | 发现 GitHub AI Agent 热点，生成小红书风格日报并推送到 Telegram |
| `godmode` | C / 不默认启用 | 凭证/API, 网关/消息, GitHub, 专用 | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |
| `google-workspace` | B / 可选 | 凭证/API, 网关/消息, GitHub | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. |
| `heartmula` | C / 不默认启用 | macOS, GitHub, 专用 | HeartMuLa: Suno-like song generation from lyrics + tags. |
| `hermes-agent` | A / 必留 | 凭证/API, macOS, MCP, 网关/消息, 系统级, GitHub | Configure, extend, or contribute to Hermes Agent. |
| `hermes-agent-skill-authoring` | A / 必留 | 凭证/API, GitHub | Author in-repo SKILL.md: frontmatter, validator, structure. |
| `hermes-telegram-setup` | A / 必留 | 凭证/API, 网关/消息, GitHub | Set up and troubleshoot Telegram bot integration with Hermes Agent gateway — token config, pairing flow, gateway service management, and common pitfalls. |
| `himalaya` | B / 可选 | 凭证/API, macOS, GitHub | Himalaya CLI: IMAP/SMTP email from terminal. |
| `huggingface-hub` | B / 可选 | 凭证/API, GitHub | HuggingFace hf CLI: search/download/upload models, datasets. |
| `humanizer` | B / 可选 | GitHub | Humanize text: strip AI-isms and add real voice. |
| `imessage` | C / 不默认启用 | macOS, 网关/消息, 专用 | Send and receive iMessages/SMS via the imsg CLI on macOS. |
| `inference` | B / 可选 | GitHub | Model serving, quantization (GGUF/GPTQ), structured output, inference optimization, and model surgery tools for deploying and running LLMs. |
| `jupyter-live-kernel` | B / 可选 | 凭证/API, GitHub | Iterative Python via live Jupyter kernel (hamelnb). |
| `kanban-orchestrator` | C / 不默认启用 | 凭证/API, 网关/消息, GitHub | Decomposition playbook + specialist-roster conventions + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work y |
| `kanban-worker` | C / 不默认启用 | 凭证/API, 网关/消息 | Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from a |
| `linear` | B / 可选 | 凭证/API, MCP | Linear: manage issues, projects, teams via GraphQL + curl. |
| `llm-wiki` | B / 可选 | 凭证/API, 系统级, GitHub | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| `mails` | B / 可选 | 凭证/API | Email infrastructure for AI agents - send/receive emails via Mails.dev |
| `manim-video` | B / 可选 | macOS, GitHub | Manim CE animations: 3Blue1Brown math/algo videos. |
| `maps` | B / 可选 | 网关/消息 | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| `matplotlib-charts` | A / 必留 | 凭证/API, macOS, GitHub | 使用 matplotlib 生成图表 - 趋势图、柱状图、饼图、热力图等。导出 PNG/SVG/PDF，用于报告和可视化。 |
| `minecraft-modpack-server` | C / 不默认启用 | 凭证/API, 系统级, 专用 | Host modded Minecraft servers (CurseForge, Modrinth). |
| `model-fallback` | A / 必留 | 凭证/API, macOS, GitHub | 为 Hermes Agent 配置模型故障转移，自动切换到备用模型。类似于 FreeRide 的"速率限制自动切换"概念，但专为 Hermes Agent 设计。 |
| `models` | B / 可选 | - | Specific model architectures and tools — image segmentation (SAM), audio generation (MusicGen), CLIP, Stable Diffusion, Whisper, LLaVA. |
| `nano-pdf` | B / 可选 | - | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). |
| `native-mcp` | A / 必留 | 凭证/API, MCP, 网关/消息, GitHub | MCP client: connect servers, register tools (stdio/HTTP). |
| `node-inspect-debugger` | A / 必留 | 网关/消息, GitHub | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| `notion` | B / 可选 | 凭证/API, GitHub | Notion API via curl: pages, databases, blocks, search. |
| `npm-publishing` | C / 不默认启用 | 凭证/API, 专用 | 发布 npm 包到 npmjs.com。包含认证、权限、发布流程。 |
| `obsidian` | B / 可选 | 凭证/API, GitHub | Read, search, and create notes in the Obsidian vault. 支持 Hermes-Wiki 知识库工作流。 |
| `ocr-and-documents` | B / 可选 | GitHub | Extract text from PDFs/scans (pymupdf, marker-pdf). |
| `opencode` | A / 必留 | 凭证/API, GitHub | Delegate coding to OpenCode CLI (features, PR review). |
| `openhue` | C / 不默认启用 | macOS, GitHub, 专用 | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |
| `p5js` | B / 可选 | macOS, GitHub | p5.js sketches: gen art, shaders, interactive, 3D. |
| `pixel-art` | C / 不默认启用 | macOS, GitHub, 专用 | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| `plan` | A / 必留 | - | Plan mode: write markdown plan to .hermes/plans/, no exec. |
| `pokemon-player` | C / 不默认启用 | GitHub, 专用 | Play Pokemon via headless emulator + RAM reads. |
| `polymarket` | B / 可选 | 凭证/API | Query Polymarket: markets, prices, orderbooks, history. |
| `popular-web-designs` | B / 可选 | 凭证/API, macOS | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| `powerpoint` | B / 可选 | MCP, GitHub | Create, read, edit .pptx decks, slides, notes, templates. |
| `pretext` | B / 可选 | macOS, GitHub | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, |
| `public-api-tools` | B / 可选 | GitHub | 来自 public-apis 项目的免费公共 API 工具集 — QR码、图标、截图、LaTeX公式渲染等 |
| `python-debugpy` | A / 必留 | 凭证/API, 网关/消息, 系统级, GitHub | Debug Python: pdb REPL + debugpy remote (DAP). |
| `report-generation` | A / 必留 | 凭证/API, macOS, MCP, 网关/消息, GitHub | 生成结构化报告 - Markdown/HTML/PDF 格式的聚合报告、趋势分析、数据摘要。支持定时生成和推送。 |
| `requesting-code-review` | A / 必留 | 凭证/API, GitHub | Pre-commit review: security scan, quality gates, auto-fix. |
| `research` | B / 可选 | - | ML research frameworks for building and optimizing AI systems with declarative programming. |
| `research-paper-writing` | B / 可选 | 凭证/API, macOS, MCP, 系统级, GitHub | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| `scrapling` | B / 可选 | 凭证/API, macOS, MCP, GitHub | Scrapling - 自适应 Web 爬虫框架，支持反爬绕过、自动元素定位、MCP 集成。47k+ stars 的生产级爬虫库。 |
| `seo-verify` | B / 可选 | 凭证/API, GitHub | Search engine site verification (Google, Baidu, Bing) + sitemap optimization + domain binding workflow. Covers GitHub Pages, Windows shared hosting with FTP, an |
| `sketch` | B / 可选 | 凭证/API, macOS, GitHub | Throwaway HTML mockups: 2-3 design variants to compare. |
| `songsee` | C / 不默认启用 | GitHub, 专用 | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| `songwriting-and-ai-music` | C / 不默认启用 | GitHub, 专用 | Songwriting craft and Suno AI music prompts. |
| `spike` | A / 必留 | 凭证/API, MCP, GitHub | Throwaway experiments to validate an idea before build. |
| `spotify` | C / 不默认启用 | 凭证/API, GitHub, 专用 | Spotify: play, search, queue, manage playlists and devices. |
| `sqlite-data` | A / 必留 | 凭证/API, macOS, GitHub | SQLite 数据库操作 - 创建/查询/聚合 Hermes Agent 的结构化数据。存储新闻聚合、趋势数据、任务状态等。 |
| `subagent-driven-development` | A / 必留 | 凭证/API, GitHub | Execute plans via delegate_task subagents (2-stage review). |
| `systematic-debugging` | A / 必留 | GitHub | 4-phase root cause debugging: understand bugs before fixing. |
| `test-driven-development` | A / 必留 | GitHub | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| `touchdesigner-mcp` | C / 不默认启用 | macOS, MCP, GitHub, 专用 | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 nativ |
| `training` | B / 可选 | - | Fine-tuning, RLHF/DPO/GRPO training, distributed training frameworks, and optimization tools for training LLMs. |
| `trendradar` | B / 可选 | MCP, 网关/消息, GitHub | TrendRadar trend monitoring and Telegram push — trigger crawl, fetch news, categorize, send multi-message Telegram notifications, archive to Obsidian, sync to G |
| `trendradar-daily` | B / 可选 | MCP, 网关/消息, GitHub | TrendRadar 多平台热点监控日报生成与 Telegram 推送 |
| `vector-databases` | B / 可选 | - | Vector database tools and integrations for semantic search and RAG applications. |
| `webhook-subscriptions` | A / 必留 | 凭证/API, 网关/消息, 系统级, GitHub | Webhook subscriptions: event-driven agent runs. |
| `website-seo` | B / 可选 | 凭证/API, 网关/消息, 系统级, GitHub | Domain binding, SSL setup, Cloudflare DNS, search engine submission, sitemap management, and Windows shared hosting FTP workflows |
| `writing-plans` | A / 必留 | - | Write implementation plans: bite-sized tasks, paths, code. |
| `xurl` | B / 可选 | 凭证/API, macOS, 系统级, GitHub | X/Twitter via xurl CLI: post, search, DM, media, v2 API. |
| `youtube-content` | B / 可选 | GitHub | YouTube transcripts to summaries, threads, blogs. |

## 安装策略草案

如果后续要改 `scripts/install.sh`，建议支持三种模式：

```bash
bash scripts/install.sh --core      # 只装 A 档
bash scripts/install.sh --standard  # A + B，默认推荐
bash scripts/install.sh --full      # 全量 101 个
```

默认建议用 `--standard`，不要默认塞入强个人化和风险类技能。
