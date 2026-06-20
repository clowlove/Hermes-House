# LLM Wiki

## 概念

LLM Wiki 是一种结合 LLM (大语言模型) 和 Wiki 工具的知识管理方法。LLM 负责读取、拆解、建页、加双链，Wiki 工具（如 [[Obsidian]]）负责查看、审阅和图谱展示。

## 核心价值

- **知识结构化**：LLM 将原始资料拆解为可复用的知识节点
- **双链网络**：概念页之间形成网状关联
- **MOC 导航**：主题地图提供理解路线图
- **可追溯**：Source-first 原则，结论可溯源

## 工作流程

```
放入一篇文章 → Hermes 读取 raw 原始资料
→ Hermes 自动拆成概念页、实体页、MOC、双链
→ Obsidian 中形成可视化知识网络
```

## 核心组成

| 目录 | 说明 |
|------|------|
| raw/ | 原始资料区，只能追加和读取 |
| concepts/ | 概念页 |
| entities/ | 实体页 |
| moc/ | 主题地图 |
| queries/ | 问答沉淀 |
| comparisons/ | 比较页 |
| drafts/ | 草稿 |

## 核心原则

- [[Zettelkasten]] - 原子化卡片
- [[双链交叉引用]] - 知识互联
- [[MOC]] - 主题地图导航
- [[Source-first]] - 关键结论标注来源
- 重要内容使用 `[[wikilink]]`

## 相关工具

- [[Obsidian]] - 主要查看工具
- [[Logseq]] - 替代选择
- [[Hermes]] - LLM Agent（用于拆解）

## 状态

`evergreen`

## 来源

LLM Wiki + Obsidian 教程 - 知野 (@knoYee_)