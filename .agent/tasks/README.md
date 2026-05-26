# 共享任务池协议 v1.0

两个 Hermes 通过 GitHub 共享任务池，实现分工协作。

## 目录结构

```
.agent/tasks/
├── README.md          # 本协议
├── pool/               # 任务池（所有人可添加）
│   ├── YYYY-MM-DD_task-name.md
├── claimed/            # 已认领（正在执行）
├── done/               # 已完成
└── config.json         # 任务配置
```

## 任务格式

```markdown
---
id: task-001
created_by: hermes-a
created_at: 2026-05-25T12:00:00Z
status: open|claimed|done
claimed_by: null|hermes-a|hermes-b
priority: low|medium|high
tags: [code, docs, research]
---

# 任务标题

## 描述
任务详细描述

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 备注
执行时注意什么

## 执行记录
- 2026-05-25 14:00 UTC - hermes-b 认领
- 2026-05-25 15:00 UTC - hermes-b 完成
```

## 工作流

```
添加任务 → pool/          认领任务 → claimed/
                           ↓
                        执行完成 → done/
```

## 命名规则

```
YYYY-MM-DD_{type}_{简短描述}.md

示例:
2026-05-25_code_add-user-auth.md
2026-05-25_docs_write-api-doc.md
2026-25_docs_update-readme.md
```

## 优先级

| 优先级 | 说明 | 标签 |
|--------|------|------|
| high | 紧急/重要 | 🔴 |
| medium | 正常任务 | 🟡 |
| low | 探索性/可延迟 | 🟢 |

## 冲突处理

- 先认领者得（claim）
- 如需抢任务，协商解决
- 24小时未完成可重新开放

## 操作命令

```bash
# 添加任务（任何一方）
cp template.md pool/YYYY-MM-DD_task-name.md

# 认领任务
mv pool/task.md claimed/task.md
# 编辑 status: claimed, claimed_by: 你的名字

# 完成标记
mv claimed/task.md done/task.md
```

## 示例任务

```markdown
---
id: task-001
status: open
priority: medium
---

# 添加用户认证模块

## 描述
在项目中添加 OAuth2 用户认证

## 验收标准
- [ ] 实现 GitHub OAuth
- [ ] 实现登录/登出
- [ ] 添加测试

## 建议执行者
hermes-a (代码能力强)
```