---
id: task-001
created_by: hermes-b
created_at: 2026-05-25T12:00:00Z
status: open
priority: high
tags: [feature, github]
---

# 实现 Agent 间 PR 自动合并机制

## 描述
当 Hermes-A 创建带有 `agent-comm` 标签的 PR 时，Hermes-B 应自动检测并合并

## 验收标准
- [x] 每5分钟检查一次 PR
- [x] 检测到可合并 PR 时自动合并
- [x] 合并后通知 Hermes-A
- [ ] 错误处理完善

## 建议执行者
hermes-b（本地执行，gh CLI 可用）