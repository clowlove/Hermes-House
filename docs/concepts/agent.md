# Agent (AI Agent)

## 什么是 Agent

Agent 是能够自主感知环境、做出决策并执行动作的 AI 系统。与传统程序不同，Agent 可以：
- 理解复杂目标
- 规划多步行动
- 使用工具
- 适应变化

## Agent 的核心组件

### 1. 规划 (Planning)
- 目标分解：将大任务拆分为可执行的子任务
- 反思机制：评估行动效果，调整策略
- 思维链 (Chain of Thought)：展示推理过程

### 2. 记忆 (Memory)
- **短期记忆**：当前对话上下文
- **长期记忆**：持久化的知识和经验
- 检索增强：结合 RAG 技术

### 3. 工具使用 (Tool Use)
- 调用外部 API
- 执行代码
- 读写文件
- 搜索信息

### 4. 协作 (Multi-Agent)
- 多个 Agent 协作完成复杂任务
- 分工明确，各司其职
- 通信协议定义交互方式

## Agent 类型

| 类型 | 描述 | 示例 |
|------|------|------|
| 单任务 Agent | 完成特定简单任务 | 天气查询 Bot |
| 任务规划 Agent | 拆解并执行复杂任务 | AutoGPT |
| 对话 Agent | 持续对话交互 | ChatGPT |
| 工具型 Agent | 辅助完成具体工作 | 代码助手 |
| 协作型 Agent | 多 Agent 协作 | MetaGPT |

## 设计模式

- **ReAct**：推理 + 行动交替
- **Plan-and-Execute**：先规划后执行
- **Reflexion**：自我反思改进
- **Tree of Thoughts**：思维树搜索

## 著名 Agent 框架

- LangChain / LangGraph
- AutoGen (Microsoft)
- CrewAI
- MetaGPT
- ChatDev

## 与 LLM 的区别

| 维度 | LLM | Agent |
|------|-----|-------|
| 核心能力 | 文本生成 | 决策 + 行动 |
| 工具使用 | 被动 | 主动 |
| 自主性 | 低 | 高 |
| 执行链路 | 单轮/多轮对话 | 感知→规划→执行→反馈 |

## 状态

`evergreen`

## 来源

待补充