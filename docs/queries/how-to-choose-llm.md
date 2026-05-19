# 如何选择 LLM

## 选择维度

### 1. 任务类型
- **通用对话**：GPT-4o、Claude 3.5
- **代码生成**：GPT-4o、Claude 3.5
- **长文档处理**：Gemini 1.5、Claude 3.5
- **中文场景**：Qwen、DeepSeek、Minim

### 2. 隐私需求
- **敏感数据**：本地部署 ([[llama.cpp]], [[Ollama]])
- **一般数据**：云端 API

### 3. 成本考量
- **低频使用**：云端按量付费
- **高频使用**：本地部署或订阅

### 4. 质量要求
- **最高质量**：GPT-4o、Claude 3.5
- **性价比**：DeepSeek、Qwen

## 模型推荐

| 场景 | 推荐 | 理由 |
|------|------|------|
| 通用助手 | GPT-4o / Claude 3.5 | 全能型 |
| 代码助手 | GPT-4o / Claude 3.5 | 上下文理解强 |
| 隐私优先 | Llama 3 / Qwen | 本地部署 |
| 中文场景 | Qwen 2.5 / DeepSeek | 中文优化 |
| 长上下文 | Gemini 1.5 / Claude 3.5 | 100K+ token |

## 状态

`growing`

## 来源

待补充