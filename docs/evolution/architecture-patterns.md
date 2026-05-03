# AI Agent 架构模式

> 从社区优秀项目提取的可复用模式

## 核心架构

### 1. ReAct (Reasoning + Acting)

```
LLM → Thought → Action → Observation → Thought → ...
```

经典范式：模型输出思维链，然后选择动作，从环境中获取观察，再继续推理。

### 2. Tool-Augmented Agent

```
Agent = LLM + ToolRegistry + Executor + Memory
```

工具注册 → 意图识别 → 工具选择 → 执行 → 结果聚合

### 3. Iterative Refinement

```
Initial Response → Critique → Revision → Final Response
```

多次迭代优化，比单次生成质量高。

## 关键组件

### Memory System

| 类型 | 用途 | 实现 |
|------|------|------|
| Short-term | 当前会话上下文 | BufferMemory |
| Long-term | 持久知识存储 | VectorDB / Redis |
| Procedural | 技能/工作流 | Skill Registry |
| Episodic | 历史经验 | Conversation logs |

### Planning

- **Chain**: 按顺序执行步骤
- **Tree**: 分支探索，选择最优路径
- **Graph**: 依赖感知的任务图

### Tool Integration

```python
# 标准工具接口
class Tool:
    name: str
    description: str
    input_schema: dict
    def execute(**kwargs) → str
```

## 学习来源

| 项目 | 贡献 |
|------|------|
| dzhng/deep-research | 迭代式搜索 + 主题深化 |
| airecon | 本地 LLM (Ollama) + Docker 安全沙箱 |
| comfyui-workflow-skill | 自然语言驱动复杂工具 |
| WebRover | Web 导航自动化 |

---

*最后更新: 2026-05-03*