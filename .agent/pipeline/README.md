# 自动化流水线协议 v1.0

Hermes-A → 数据采集 → Hermes-B → 分析 → 用户

## 流水线架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Hermes-A   │     │  Hermes-B   │     │    用户     │
│  (采集者)   │     │  (分析者)   │     │   (亨利)    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   │
┌─────────────┐     ┌─────────────┐           │
│  数据采集   │ ──▶ │  数据分析   │ ────────▶ │
│  (outbox)   │     │  (inbox)    │           │
└─────────────┘     └─────────────┘           │
                           │                   │
                           ▼                   │
                    ┌─────────────┐           │
                    │  报告推送   │ ←─────────┘
                    │  (Telegram) │
                    └─────────────┘
```

## 数据交换格式

```yaml
# pipeline/{pipeline-name}/{timestamp}_{stage}.json
{
  "pipeline": "trend-report",
  "stage": "raw|processed|analyzed|report",
  "produced_by": "hermes-a",
  "timestamp": "2026-05-25T12:00:00Z",
  "data": {
    "source": "trendradar",
    "items": [...],
    "stats": {...}
  },
  "meta": {
    "next_stage": "hermes-b",
    "expected_stages": ["raw", "analyzed", "report"]
  }
}
```

## 流水线类型

### 1. 趋势监控流水线

```
Hermes-A 采集 → Hermes-B 分析 → Telegram 推送
```

| 阶段 | 文件 | 执行者 |
|------|------|--------|
| raw | `pipeline/trend/raw_YYYYMMDD.json` | A |
| analyzed | `pipeline/trend/analyzed_YYYYMMDD.json` | B |
| report | `pipeline/trend/report_YYYYMMDD.md` | B |

### 2. 代码质量流水线

```
Hermes-A 扫描 → Hermes-B 审查 → PR 创建
```

| 阶段 | 文件 | 执行者 |
|------|------|--------|
| scan | `pipeline/code/scan_YYYYMMDD.json` | A |
| review | `pipeline/code/review_YYYYMMDD.md` | B |

### 3. 学习报告流水线

```
Hermes-A 记录 → Hermes-B 整理 → 用户阅读
```

| 阶段 | 文件 | 执行者 |
|------|------|--------|
| raw | `pipeline/learn/raw_YYYYMMDD.json` | A |
| summary | `pipeline/learn/summary_YYYYMMDD.md` | B |

## 目录结构

```
.agent/
├── tasks/
├── knowledge/
└── pipeline/              # 流水线数据
    ├── trend/
    ├── code/
    ├── learn/
    └── config.yaml        # 流水线配置
```

## 流水线配置

```yaml
pipelines:
  trend-report:
    stages: [raw, analyzed, report]
    producers: [hermes-a]
    consumers: [hermes-b]
    schedule: "0 8,17 * * *"  # 每天两次
    deliver_to: telegram
    
  code-scan:
    stages: [scan, review]
    producers: [hermes-a]
    consumers: [hermes-b]
    trigger: on-pr-open
    deliver_to: pr-comment
    
  daily-learn:
    stages: [raw, summary]
    producers: [hermes-a]
    consumers: [hermes-b]
    schedule: "0 22 * * *"
    deliver_to: telegram
```

## 交接协议

### A → B 交接
1. A 完成当前阶段
2. 在 outbox 创建数据文件
3. 创建 PR 并通知 B
4. B 读取并处理

### B 完成通知
1. B 生成报告
2. 推送结果
3. 通过 Telegram 通知用户
4. 标记流水线完成

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| A 阶段失败 | 重试 3 次，失败则通知 |
| B 无响应 | 24 小时超时，跳过或通知用户 |
| 数据格式错误 | A 重新生成，B 提供格式说明 |

## 执行脚本

```python
# pipeline_runner.py - 流水线执行器
import json
import subprocess
from pathlib import Path

def run_pipeline(name: str, stage: str):
    data_dir = Path(f".agent/pipeline/{name}")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查前置阶段
    # 执行当前阶段
    # 写入输出
    # 通知下一阶段
```