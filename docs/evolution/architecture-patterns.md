# AI Agent 架构模式

> 从社区优秀项目和 Harmes-House 实践中提取的可复用模式

## 核心架构

### 1. ReAct (Reasoning + Acting)

```
LLM → Thought → Action → Observation → Thought → ...
```

经典范式：模型输出思维链，然后选择动作，从环境中获取观察，再继续推理。

**适用场景**：需要工具调用的复杂任务、Multi-step 推理

### 2. Tool-Augmented Agent

```
Agent = LLM + ToolRegistry + Executor + Memory
```

工具注册 → 意图识别 → 工具选择 → 执行 → 结果聚合

**适用场景**：需要调用多种外部工具的场景

### 3. Iterative Refinement

```
Initial Response → Critique → Revision → Final Response
```

多次迭代优化，比单次生成质量高。

**适用场景**：代码生成、写作、内容创作

### 4. Plan-and-Execute

```
Planner (LLM) → Task Graph → Executor → Resolver
```

先规划所有步骤，再按依赖顺序执行，最后汇总。

**适用场景**：复杂多步骤任务

### 5. Multi-Agent Collaboration

```
Agent A (专家) ←→ Agent B (专家) ←→ Agent C (协调者)
```

多个专业 Agent 协作，各司其职，通过协议通信。

**适用框架**：MetaGPT, CrewAI, AutoGen

## MCP (Model Context Protocol)

MCP 是 Anthropic 提出的标准化协议，用于连接 AI Agent 与外部工具。

### 架构

```
Host (Claude/Cline) ←→ MCP Client ←→ MCP Server (工具)
                            ↓
                     本地 / 远程
```

### MCP Server 类型

| 类型 | 示例 | 用途 |
|------|------|------|
| 本地工具 | filesystem, terminal | 读写文件、执行命令 |
| 远程服务 | GitHub, Slack, Google | API 集成 |
| 数据源 | PostgreSQL, Redis | 数据库查询 |
| 浏览器 | mcp-chrome | 网页自动化 |

### Harmes-House 中的 MCP 实践

- [native-mcp](skills/native-mcp) — 内置 MCP Client
- [scrapling](skills/scrapling) — 可作为 MCP server 提供爬虫能力

### 知名 MCP 项目

| 项目 | Stars | 说明 |
|------|-------|------|
| fastapi-mcp | 11.8k | FastAPI → MCP Server |
| mcp-chrome | 11.4k | Chrome → MCP Server |
| mcp-for-beginners | 16k | Microsoft MCP 教程 |

## 关键组件

### Memory System

| 类型 | 用途 | 实现 |
|------|------|------|
| Short-term | 当前会话上下文 | BufferMemory |
| Long-term | 持久知识存储 | VectorDB / Redis |
| Procedural | 技能/工作流 | Skill Registry |
| Episodic | 历史经验 | Conversation logs |
| Semantic | 文档/知识 | RAG Retrieval |

### Planning

- **Chain**: 按顺序执行步骤
- **Tree**: 分支探索，选择最优路径 (ToT)
- **Graph**: 依赖感知的任务图 (LangGraph)

### Tool Integration

```python
# 标准工具接口
class Tool:
    name: str
    description: str
    input_schema: dict
    def execute(**kwargs) → str
```

## Multi-Agent 协作模式

### 1. 层级模式

```
Manager Agent
    ├── Research Agent
    ├── Coding Agent
    └── Review Agent
```

### 2. 同级协作模式

```
Agent A ←→ Message Bus ←→ Agent B
                    ↓
              Shared Memory
```

### 3. 流水线模式

```
Input → Preprocess → Agent A → Agent B → Agent C → Output
```

## 学习来源

| 项目 | Stars | 贡献 |
|------|-------|------|
| MetaGPT | 44k | Multi-Agent 软件开发 |
| CrewAI | 22k | 角色驱动 Agent 编排 |
| AutoGen | 32k | Microsoft 多 Agent 框架 |
| mcp-for-beginners | 16k | MCP 协议入门教程 |
| dzhng/deep-research | 18k | 迭代式搜索 + 主题深化 |

## Harmes-House 技能映射

| 模式 | 相关技能 |
|------|---------|
| Tool-Augmented | [native-mcp](skills/native-mcp), [scrapling](skills/scrapling) |
| Iterative Refinement | [systematic-debugging](skills/systematic-debugging) |
| Multi-Agent | [claude-code](skills/claude-code), [hermes-agent](skills/hermes-agent) |
| Planning | [plan](skills/plan) |
| Memory/RAG | [llm-wiki](skills/llm-wiki), [obsidian](skills/obsidian) |

---

*最后更新: 2026-05-05*