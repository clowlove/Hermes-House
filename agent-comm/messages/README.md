# 消息目录

## 目录说明

- `inbox/` — 收到的消息
- `outbox/` — 待发送的消息

## 消息文件名规范

```
{type}-{from}-{to}-{timestamp}.md
```

### 示例

```
task-hermes-a-hermes-b-20260525-130000.md    # Hermes-A 发给 Hermes-B 的任务
status-hermes-b-hermes-a-20260525-131500.md  # Hermes-B 发给 Hermes-A 的状态
```

## 消息类型

| 类型 | 说明 |
|------|------|
| `task` | 任务委派 |
| `status` | 状态更新 |
| `knowledge` | 知识共享 |
| `review` | 代码审查请求 |
| `response` | 回复 |
| `ping` | 心跳/连接测试 |