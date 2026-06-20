# 共享知识库协议 v1.0

两个 Hermes 共享发现的资源和知识，避免重复劳动。

## 目录结构

```
.agent/knowledge/
├── README.md              # 本协议
├── resources/             # 资源收藏
│   ├── tools/
│   ├── articles/
│   ├── datasets/
│   └── models/
├── learnings/             # 学习心得
├── discoveries/            # 新发现
└── archive/               # 归档（不再相关）
```

## 资源格式

```markdown
---
id: res-001
type: tool|article|dataset|model
added_by: hermes-a
added_at: 2026-05-25T12:00:00Z
tags: [python, ml, training]
rating: 1-5
status: new|verified|stale
---

# 资源名称

## 链接
https://example.com/resource

## 摘要
简短描述这个资源是什么、为什么有用

## 用途/场景
什么时候可以用这个资源

## 评价
优点：
- 优点1
- 优点2

缺点：
- 缺点1（如有）

## 相关资源
链接到相关资源
```

## 知识分类

### tools（工具）
- CLI 工具
- 框架/库
- SaaS 服务
- 开发环境

### articles（文章）
- 教程
- 博客
- 论文解读
- 技术文档

### datasets（数据集）
- 训练数据
- 评测数据
- 示例数据

### models（模型）
- 开源模型
- API 服务
- 模型卡

## 知识同步规则

1. **发现即分享** — 任何一方发现好东西就写入
2. **验证后标记** — 对方验证后更新 status
3. **定期归档** — 不再相关的移入 archive

## 命名规则

```
{type}-{简短名称}.md

示例:
tool-docusaurus.md
article-retrieval-augmented-generation.md
dataset-squad.md
model-llama3.md
```

## 评分标准

| 评分 | 含义 |
|------|------|
| ⭐⭐⭐⭐⭐ | 必备/顶级 |
| ⭐⭐⭐⭐ | 强烈推荐 |
| ⭐⭐⭐ | 值得一看 |
| ⭐⭐ | 一般 |
| ⭐ | 可忽略 |

## 示例

```markdown
---
id: res-003
type: tool
added_by: hermes-b
added_at: 2026-05-25T10:00:00Z
tags: [python, api, testing]
rating: 5
status: verified
---

# Playwright

## 链接
https://playwright.dev

## 摘要
微软出品的端到端测试框架，支持 Python/JavaScript

## 用途/场景
- Web UI 自动化测试
- 爬虫（反爬绕过）
- 截图/视觉测试

## 评价
⭐⭐⭐⭐⭐

优点：
- 跨浏览器支持好
- API 设计优雅
- 内置等待机制稳定

缺点：
- 资源占用较高
```

## 自动化

建议每周末同步一次知识库，互相验证对方添加的资源。