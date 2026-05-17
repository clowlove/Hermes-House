# MOC (Map of Content)

## 什么是 MOC

MOC 是主题地图/内容地图，用于组织和关联多个相关笔记的导航页面。不是普通目录，而是**理解路线图**。

## 目录 vs MOC

| 维度 | 目录 | MOC |
|------|------|-----|
| 目的 | 分类存储 | 展示关系 |
| 组织方式 | 层级结构 | 网状结构 |
| 内容 | 文件列表 | 主题概览 + 链接 |
| 更新频率 | 静态 | 动态演进 |

## MOC 的价值

1. **鸟瞰全局**：一眼看到某领域所有相关主题
2. **理解关系**：知道各主题如何关联
3. **导航入口**：作为该领域的着陆页
4. **知识进度**：标记哪些已深入，哪些待学习

## 创建原则

- 一个领域一个 MOC
- 包含核心概念列表
- 展示概念间关系
- 定期更新演进
- 使用 `[[wikilink]]` 链接到具体页面

## 示例结构

```markdown
# [[LLM Wiki 地图]]

## 核心概念
- [[LLM]] - 大语言模型基础
- [[RAG]] - 检索增强生成
- [[Agent]] - AI Agent
- [[Prompt Engineering]] - 提示词工程

## 进阶主题
- [[Agentic RAG]] - 结合 Agent 和 RAG
- [[Multi-Agent]] - 多 Agent 协作

## 工具生态
- [[Obsidian]] - 笔记工具
- [[LangChain]] - Agent 开发框架

## 学习路径
1. [[LLM]] → [[Prompt Engineering]]
2. → [[RAG]]
3. → [[Agent]]
4. → [[Agentic RAG]]
```

## 状态

`evergreen`

## 来源

LLM Wiki + Obsidian 教程 - 知野 (@knoYee_)