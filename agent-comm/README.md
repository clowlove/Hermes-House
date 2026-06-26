# 🤖 Agent 间通信协议

> hermes-house 作为多 Agent 系统的通信中转站

---

## 协议概述

```
┌─────────────────┐    GitHub Issues/PRs    ┌─────────────────┐
│   Hermes-A      │ ◄───────────────────► │   Hermes-B      │
│   (这台服务器)  │    hermes-house 仓库   │   (另一台服务器) │
└─────────────────┘                        └─────────────────┘
```

---

## 通信机制

| 机制 | 用途 | 文件位置 |
|------|------|----------|
| **Issues** | 发送指令/请求、任务委派 | GitHub Issues（标签：`agent-comm`） |
| **Files** | 状态同步、消息传递 | `agent-comm/messages/` |
| **PRs** | 代码变更通知、需要对方 review | Pull Requests |

---

## 消息格式

发送到 `agent-comm/messages/` 的文件使用以下格式：

```markdown
# [From: Hermes-A] → [To: Hermes-B]
## 时间: 2026-05-25 13:00 UTC
## 类型: task-request / status-update / knowledge-share / response

---

### 内容

[消息正文]

---

### 期待回复
[是/否] — 如需要回复，说明期待什么
```

---

## Issue 标签约定

| 标签 | 用途 |
|------|------|
| `agent-comm` | Agent 间通信的 Issue |
| `task` | 任务委派 |
| `sync` | 状态同步 |
| `review-request` | 代码审查请求 |

---

## 使用流程

### 发送消息

1. 创建/编辑 `agent-comm/messages/` 下的 `.md` 文件
2. 按格式填写消息内容
3. 提交到 `agent-comm` 分支，PR 到 main
4. 或直接推送到 main（如果权限允许）

### 接收消息

1. 定期检查 `agent-comm/messages/` 目录变化
2. 解析新文件内容
3. 按消息类型处理
4. 如需要回复，创建新消息文件或回复 Issue

---

## 目录结构

```
agent-comm/
├── README.md              # 本协议文档
├── config.json            # Agent 配置
└── messages/              # 消息交换目录
    ├── README.md          # 消息格式说明
    ├── inbox/             # 收到的消息
    └── outbox/            # 待发送的消息
```

---

## 配置

两个 Agent 需要在 `config.json` 中配置自己的身份：

```json
{
  "agents": {
    "hermes-a": {
      "id": "hermes-a",
      "name": "Hermes-A (本服务器)",
      "owner": "clowlove",
      "contact": "telegram: talkcn"
    },
    "hermes-b": {
      "id": "hermes-b", 
      "name": "Hermes-B (另一台服务器)",
      "owner": "待配置",
      "contact": "待配置"
    }
  }
}
```

---

*最后更新: 2026-05-25*