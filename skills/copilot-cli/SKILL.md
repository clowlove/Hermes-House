---
name: copilot-cli
description: GitHub Copilot CLI — 安装、认证、三种模式、工具权限、上下文管理、GitHub 集成、Custom Agents、MCP、Hooks
version: 1.1.0
tags: [copilot, github, cli, agent, mcp]
---

# GitHub Copilot CLI v1.0.40+

## 安装

**推荐（Linux/macOS）：**
```bash
curl -fsSL https://gh.io/copilot-install | bash
```

**Homebrew：**
```bash
brew install copilot-cli
```

**pip（任意平台）：**
```bash
pip install github-copilot-cli
```

**验证：**
```bash
copilot --version
```

> ⚠️ 注意：`gh copilot` 扩展已于 2025 年 9 月废弃，所有功能已迁移到独立的 `copilot` CLI。

---

## 认证

**关键：需要 Fine-Grained PAT（`ghp_` 开头的不行）**

Fine-Grained PAT 创建：https://github.com/settings/tokens
需要勾选 **Copilot** scope。

**三种认证方式：**

```bash
# 方式1：Web 登录（需浏览器）
copilot login

# 方式2：环境变量（推荐自动化）
export COPILOT_GITHUB_TOKEN=$(gh auth token)

# 方式3：直接指定 PAT
export COPILOT_GITHUB_TOKEN=ghp_xxxxxxxxxxxx
copilot
```

---

## 三种运行模式

用 `Shift+Tab` 循环切换模式。

### 交互模式（默认）

```bash
copilot
```

- 每条指令需要确认后才执行
- 按需提问澄清
- 文件修改和命令执行前会弹出权限确认

### Plan 模式（推荐复杂任务）

```bash
# 在交互模式内按 Shift+Tab 切换，或启动时：
copilot --mode plan
```

- 不直接写代码，先生成结构化实施计划
- 可在执行前修改、调整单个步骤
- 适合多步骤重构、复杂功能设计

### 自动驾驶模式（Autopilot）

```bash
copilot --mode autopilot -p "实现 xxx 功能"
```

- 自动执行，不需要手动确认
- 适合已充分理解的任务

---

## 工具权限控制

### 权限标志说明

| 标志 | 说明 |
|------|------|
| `--allow-tool 'shell(COMMAND)'` | 允许特定 shell 命令（可重复使用） |
| `--allow-tool 'write'` | 允许所有文件修改 |
| `--allow-tool 'shell'` | 允许所有 shell 命令 |
| `--allow-all-tools` / `--yolo` | 全部允许（谨慎使用） |
| `--deny-tool 'shell(rm)'` | 拒绝特定命令（优先级最高） |
| `--allow-tool 'postgres'` | 允许 MCP server 的工具 |

### 权限示例

```bash
# 允许运行 pytest 和写文件（无需每次确认）
copilot -p "运行测试并报告结果" --allow-tool 'shell(pytest)' --allow-tool 'write'

# 允许所有但拒绝危险操作
copilot --allow-all-tools --deny-tool 'shell(rm)' --deny-tool 'shell(git push)'

# 允许 MCP server（需先配置 MCP）
copilot --allow-tool 'postgres' --allow-tool 'postgres(query)'
```

### 交互模式内权限

```
1. Yes                          — 允许本次
2. Yes, and approve for session  — 本次会话内不再询问
3. No + 说明                     — 拒绝并告诉 Copilot 怎么处理
```

---

## 模型选择

### `/model` 命令

交互模式内输入：
```
/model
```

可选 **Auto**（自动选最优模型）或指定模型。

**常见模型（2026年2月）：**

| 模型 | 倍率 | 备注 |
|------|------|------|
| Claude Sonnet 4.6 | 1× | 默认，代码能力强 |
| Claude Opus 4.6 | varies | 复杂规划任务 |
| GPT-5.3-Codex | varies | Agentic 任务更快 |
| Auto | — | 自动选择最优模型 |

### 启动时指定

```bash
copilot --model claude-sonnet-4.6
```

> Auto 模式比手动选择便宜 10%（Pro+ 及以上）。Auto 不会选有 premium multiplier > 1× 的模型。

---

## 上下文管理

### `/context` — 查看 token 使用

```
/context
```

显示：系统提示词 / 对话历史 / 剩余可用 token。

### `/compact` — 压缩上下文

```
/compact
```

压缩对话历史，保留关键信息。需要时按 `Escape` 取消。

> 自动压缩在会话达到 **95% token 限制**时自动触发，可实现几乎无限的会话长度。

---

## GitHub.com 集成（内置 MCP）

Copilot CLI 内置 GitHub MCP server，无需额外配置即可使用：

```bash
copilot
```

### 常用指令

```
List my open PRs
List all open issues assigned to me in owner/repo
Check the changes made in PR https://github.com/owner/repo/pull/123
Use the GitHub MCP server to find good first issues for owner/repo
```

### 在 Issue 上工作

```
I've been assigned this issue: https://github.com/<owner>/<repo>/issues/<number>. Start working on this in a suitably named branch.
```

Copilot 会：读取 Issue → 创建分支 → 实现 → 运行测试 → 汇报。

### 创建 PR

```
In the root of this repo, add health_check.py. Create a pull request against main.
```

---

## 远程 Agent Task（`gh agent-task`）

在云端 Codespace 运行，不占用本地资源，适合长任务。

```bash
# 关联 Issue 创建远程任务
gh agent-task create --repo <owner>/<repo> --issue <number> \
  --body "Add docstrings to the new code"

# 列出所有任务
gh agent-task list --repo <owner>/<repo>

# 查看任务状态
gh agent-task view <task-id> --repo <owner>/<repo>

# 查看完成后的 PR
gh pr view <pr-number> --web
```

> Agent Task 需要 Copilot Pro 或更高版本。

---

## Custom Agents（自定义代理）

### 创建 Agent

在项目 `.github/agents/` 目录下创建：

```markdown
---
name: fastapi-expert
description: FastAPI 专家代理
---

## Role
你是 Python 后端工程师，专精 FastAPI 和异步 Python。

## Conventions
- 使用 async/await 处理所有 I/O 操作
- 使用 Pydantic 定义所有请求/响应模型
- 使用依赖注入管理共享资源
- 遵循 RESTful 命名规范
- 使用正确的 HTTP 状态码
```

### 使用 Agent

```
@fastapi-expert Add rate limiting middleware
```

Agent 名称前加 `@` 调用。

---

## Custom Instructions（自定义指令）

在 `.github/` 目录创建 `copilot-instructions.md`：

```markdown
# Project Guidelines

## Technology Stack
- Framework: FastAPI
- Testing: pytest with pytest-mock
- Validation: Pydantic v2

### Coding Style
- 遵循 PEP 8
- 使用类型提示
- 使用 f-strings
- 公共函数添加 Google-style docstrings

### Testing Guidance
- 使用 pytest
- 使用 pytest-mock mock 外部依赖
- 测试命名：`test_<function>_<scenario>`

### Architecture
- 路由、模型、工具函数分离
- 使用 Pydantic 定义 schema
```

### 作用域指令

在 `.github/instructions/` 下按目录应用：

```markdown
---
applyTo: "webapp/**/*.py"
---

## API Conventions
- PascalCase 类名
- 使用 type hints
- 为 endpoint 函数添加详细 docstrings
```

---

## MCP Servers（扩展工具）

### 配置文件

**用户级**（所有项目）：`~/.copilot/mcp-config.json`
**项目级**：`.github/mcp.json`

### 示例：PostgreSQL MCP

```json
{
  "servers": {
    "postgres": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "DATABASE_URL", "mcp/postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/mydb"
      }
    }
  }
}
```

### 使用 MCP 工具

交互模式内查看已配置的 MCP servers：

```
/mcp
```

然后用自然语言调用：

```
Use the postgres MCP server to show me the schema of the users table.
```

### 预批准 MCP 工具

```bash
# 允许整个 server
copilot --allow-tool 'postgres'

# 只允许特定工具
copilot --allow-tool 'postgres(query)' --deny-tool 'postgres(execute)'
```

---

## Copilot Memory（跨会话记忆）

```bash
# 查看当前记忆
/memory
```

Copilot 会记住项目规范、偏好设置，下次启动无需重复说明。

---

## Hooks（写文件后自动执行）

### 创建 Hook

`.github/hooks/post-write.sh`：

```bash
#!/bin/bash
if [[ "$COPILOT_HOOK_FILE" == *.py ]]; then
  ruff check --fix "$COPILOT_HOOK_FILE"
  ruff format "$COPILOT_HOOK_FILE"
fi
```

### 注册 Hook

`.github/hooks/config.json`：

```json
{
  "hooks": [
    { "event": "post-write", "command": ".github/hooks/post-write.sh" }
  ]
}
```

---

## Community Extensions（Awesome Copilot）

```bash
# 添加插件市场
copilot plugin marketplace add github/awesome-copilot

# 安装 awesome-copilot 插件
copilot plugin install awesome-copilot@awesome-copilot
```

然后在交互模式内：

```
/awesome-copilot:suggest-awesome-github-copilot-skills
/awesome-copilot:suggest-awesome-github-copilot-instructions
/awesome-copilot:suggest-awesome-github-copilot-agents
```

---

## 实际工作流模板

### 完整 Python 功能开发流程

```
Stage 1 → 探索（默认模式）
  copilot
  "Show me all files involved in the /token endpoint"

Stage 2 → 设计（Plan 模式）
  [Shift+Tab] → Plan 模式
  "Add pagination to /token endpoint..."

Stage 3 → 构建测试
  Copilot 实现代码 → 运行 pytest → 自我修正
  /context  → 检查 token 使用
  /compact   → 压缩上下文

Stage 4 → 提交 PR
  "Commit with conventional commit and create PR"

Stage 5 → 异步完善（远程 Agent）
  gh agent-task create --repo owner/repo --issue <num> \
    --body "Add docstrings"
```

### 表格式总结

| 阶段 | 模式 | 工具 | 动作 |
|------|------|------|------|
| 探索 | 默认 | Copilot CLI | 自然语言映射文件 |
| 设计 | Plan | Copilot CLI | 构建实施计划 |
| 构建 | 默认/Plan | Copilot CLI | 实现 + pytest + 自我修正 |
| 上下文 | — | /context + /compact | 管理 token 使用 |
| 交付 | — | GitHub MCP | 提交 + PR |
| 完善 | — | gh agent-task | 异步文档生成 |

---

## 参考资源

- 官方文档：https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli
- 安装指南：https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli
- Copilot CLI 参考：https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli
- 官方课程（微软）：https://github.com/microsoft/Mastering-GitHub-Copilot-for-Paired-Programming
- Awesome Copilot：https://github.com/github/awesome-copilot