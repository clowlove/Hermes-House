---
name: copilot-cli
description: GitHub Copilot CLI 使用指南 — v1.0.40 安装、认证、能力
---

# GitHub Copilot CLI

## 安装
```bash
curl -fsSL https://github.com/github/copilot-cli/releases/download/v1.0.40/copilot-linux-x64.tar.gz -o /tmp/copilot.tar.gz
tar -xzf /tmp/copilot.tar.gz -C /tmp
sudo mv /tmp/copilot /usr/local/bin/copilot
chmod +x /usr/local/bin/copilot
copilot --version  # GitHub Copilot CLI 1.0.40
```

## 认证要求
**重要**: Copilot CLI 需要 Fine-Grained PAT（`github_pat_` 开头），不支持 Classic PAT（`ghp_` 开头）。

认证方式（3选1）：
1. `copilot login --web` (需浏览器)
2. 设置环境变量: `export COPILOT_GITHUB_TOKEN=$(gh auth token)` — 但 gh 需用 Fine-Grained PAT 登录
3. `export COPILOT_GITHUB_TOKEN=<fine-grained-pat>`

创建 Fine-Grained PAT: https://github.com/settings/tokens

Fine-Grained PAT 需要勾选 **Copilot** scope。

## 核心能力
- **交互模式**: `copilot` (无参数)
- **非交互模式**: `copilot -p "prompt" --allow-all-tools`
- **Agent 模式**: `--mode plan` / `--mode autopilot`
- **会话恢复**: `copilot --continue`, `copilot --resume=<session-id>`
- **MCP 集成**: `--add-github-mcp-tool`, `--add-github-mcp-toolset`, `--disable-builtin-mcps`
- **自定义模型**: `--model <model-name>` (支持 BYOK provider)
- **插件系统**: `--plugin-dir <directory>`

## 权限标志
- `--allow-all` = `--allow-all-tools --allow-all-paths --allow-all-urls`
- `--yolo` = 同 `--allow-all`
- `--allow-tool='write'` 允许写文件
- `--allow-tool='shell(git:*)'` 允许 git 操作
- `--add-dir <path>` 允许访问特定目录

## 使用示例
```bash
# 解释代码（非交互）
copilot -p "Explain this function" --allow-tool='shell(cat)' -s

# 修复 bug（交互）
copilot -p "Fix the bug in main.py" --allow-all -i

# 计划模式（不执行，只分析）
copilot -p "Migrate this project to TypeScript" --mode plan

# 自动驾驶模式
copilot -p "Refactor the auth module" --mode autopilot

# 使用特定模型
copilot -p "Review this PR" --model gpt-4
```

## 当前状态
⚠️ 待认证：需要 Fine-Grained PAT（classic PAT 不支持）