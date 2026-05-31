# HF CLI Skill for Hermès Agent
# 自动同步到 HF，版本 2.0

## Trigger Conditions
- 用户提到 Hugging Face、HF、huggingface
- 需要上传/下载模型、数据集、Space
- 需要查找或搜索 HF 资源
- 需要部署 Space 应用

## Commands

### 基础认证
```bash
hf auth login --token [TOKEN]
hf whoami  # 验证登录状态
```

### 模型操作
```bash
hf models ls                          # 列出我的模型
hf models search "gpt2"               # 搜索模型
hf models download username/modelname # 下载模型
hf upload username/modelname ./model/ # 上传模型
```

### 数据集操作
```bash
hf datasets ls                        # 列出我的数据集
hf datasets search "wikipedia"        # 搜索数据集
hf datasets download username/dataset # 下载数据集
hf upload username/dataset ./data/    # 上传数据集
```

### Space 操作
```bash
hf spaces ls                          # 列出我的 Spaces
hf spaces create username/space --type space --public --space-sdk gradio  # 创建 Space
hf upload username/space . --repo-type space  # 上传 Space
```

### Collection 操作
```bash
hf collections ls                      # 列出我的 Collections
hf collections create username/collection  # 创建 Collection
hf collections add-item username/collection username/resource type  # 添加资源
```

### 推理 API (免费)
```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="meta-llama/Llama-3.2-1B-Instruct",
    token="hf_xxx"
)

# 文本生成
result = client.text_generation(
    prompt="Hello, how are you?",
    max_new_tokens=100,
    temperature=0.7
)
```

## Hermès 资源列表 (cntalk)

| 资源名 | 类型 | URL |
|--------|------|-----|
| hello-hermes | Space | hf.co/spaces/cntalk/hello-hermes |
| hermes-toolkit | Space | hf.co/spaces/cntalk/hermes-toolkit |
| hermes-examples | Dataset | hf.co/datasets/cntalk/hermes-examples |
| agent-prompts | Dataset | hf.co/datasets/cntalk/agent-prompts |
| hermes-skills | Dataset | hf.co/datasets/cntalk/hermes-skills |
| hermes-integration | Dataset | hf.co/datasets/cntalk/hermes-integration |

Collection: [hermes-agent-resources](https://huggingface.co/collections/cntalk/hermes-agent-resources-69f9c5b62fb70b0bbb6ae0b1)

## 同步脚本
```bash
python ~/.hermes/scripts/hf_sync.py  # 同步 Hermès 资源到 HF
```

## 注意事项
- 免费账户可创建公开模型/数据集/Spaces
- Space CPU Basic 免费，T4 GPU 按小时计费
- Inference API 有速率限制 (不指定模型时)
- 上传前确保 `.gitattributes` 设置正确 (LFS 如果需要)

## 免费 Inference API 模型 (常用)
- text-generation: meta-llama/Llama-3.2-1B-Instruct, mistralai/Mistral-7B-Instruct-v0.2
- summarization: facebook/bart-large-cnn
- translation: Helsinki-NLP/opus-mt-zh-en
- sentiment-analysis: distilbert-base-uncased-finetuned-sst-2-english
- question-answering: deepset/roberta-base-squad2
- image-classification: google/vit-base-patch16-224