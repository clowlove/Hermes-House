# RAG (Retrieval Augmented Generation)

## 什么是 RAG

RAG 是一种结合检索系统和生成模型的 AI 架构。模型在生成回答前，先从外部知识库检索相关信息，再用检索到的内容作为上下文来生成答案。

## 核心组件

1. **检索器 (Retriever)**
   - 负责从向量数据库中查找相关文档
   - 常用算法：BM25、Dense Passage Retrieval (DPR)
   - Embedding 模型决定检索质量

2. **生成器 (Generator)**
   - 通常是 LLM
   - 接收检索结果 + 问题作为输入
   - 生成最终回答

3. **向量数据库 (Vector Store)**
   - 存储文档的向量表示
   - 支持相似度搜索
   - 常见选择：Pinecone、Weaviate、Milvus、ChromaDB

## 为什么需要 RAG

- **时效性**：训练数据有截止日期，RAG 可访问最新信息
- **可解释性**：答案可溯源到原始文档
- **降低成本**：无需为每个知识微调模型
- **减少幻觉**：基于真实文档生成，更可靠

## RAG 流程

```
用户问题 → Embedding → 向量相似度搜索 → Top-K 相关文档 → 与问题拼接 → LLM 生成回答
```

## Agentic RAG

在 RAG 基础上增加 Agent 能力：
- 决定是否需要检索
- 选择检索范围和策略
- 多步推理和迭代优化
- **Agentic RAG** 模式：Agent 负责决策检索时机和策略

## 优化策略

- **Query 改写**：将用户问题改写为更适合检索的形式
- **混合检索**：结合向量搜索和关键词搜索
- **重排序 (Reranker)**：对检索结果二次排序
- **迭代检索**：多轮检索逐步精炼结果

## 相关技术

- [[Agentic RAG]] - 结合 Agent 和 RAG
- [[Chunking]] - 文档分块策略
- [[Embedding]] - 向量化技术

## 状态

`evergreen`

## 来源

待补充