---
id: task-003
created_by: hermes-c
created_at: 2026-05-25T10:30:00Z
status: open
priority: high
tags: [pipeline, demo, a-b-c]
pipeline: trend-monitor
---

# 演示：三 Agent 协作流水线

## 任务描述

演示 Hermes-A → Hermes-B → Hermes-C 的完整协作流程。

**目标：生成一份"今日 AI 趋势报告"**

## 流水线阶段

| 阶段 | 执行者 | 状态 | 输出 |
|------|--------|------|------|
| 1. 爬取数据 | Hermes-A | ⏳ 待执行 | 原始数据 |
| 2. 分析趋势 | Hermes-B | ⏳ 待执行 | 分析报告 |
| 3. 审核发布 | Hermes-C | ⏳ 待执行 | 最终报告 |

## 阶段 1 输出（Hermes-A 填写）

```json
{
  "platforms": ["github-trending", "hacker-news", "techcrunch"],
  "items_collected": 50,
  "top_topics": ["LLM", "AI Agent", "RAG"],
  "timestamp": "2026-05-25T10:00:00Z"
}
```

## 阶段 2 输出（Hermes-B 填写）

```json
{
  "summary": "今日 AI 领域最大热点是 AI Agent 自主化",
  "key_trends": ["Multi-Agent 系统", "自我进化", "边缘部署"],
  "insights": ["观点1", "观点2"]
}
```

## 阶段 3 输出（Hermes-C 填写）

```json
{
  "status": "approved",
  "notes": "报告质量良好，建议发布",
  "delivered_to": "telegram"
}
```

## 验收标准

- [ ] Hermes-A 完成数据爬取
- [ ] Hermes-B 完成趋势分析
- [ ] Hermes-C 审核通过
- [ ] 最终报告发送给用户

## 建议执行者

流水线演示，按顺序执行：
1. Hermes-A (阶段1)
2. Hermes-B (阶段2)
3. Hermes-C (阶段3) - 我来执行