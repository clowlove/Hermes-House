---
name: inference
description: Model serving, quantization (GGUF/GPTQ), structured output, inference optimization, and model surgery tools for deploying and running LLMs.
version: 1.0.0
metadata:
  hermes:
    tags: [mlops, inference]
    related_skills: ['llama-cpp', 'serving-llms-vllm', 'outlines']
---

# Inference

Model serving, quantization, and inference optimization tools for deploying and running LLMs.

## Sub-skills

- **llama-cpp**: llama.cpp local GGUF inference + HF Hub model discovery
- **serving-llms-vllm**: vLLM: high-throughput LLM serving, OpenAI API
- **outlines**: Structured JSON/regex/Pydantic LLM generation
- **obliteratus**: OBLITERATUS: abliterate LLM refusals

## Colab Notebook Deployment

Google Colab provides free GPU/TPU for inference and fine-tuning. The workflow: write notebook JSON → push to GitHub → open in Colab.

### Colab Notebook Structure (JSON)
```json
{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": { "name": "notebook_name.ipynb" },
    "kernelspec": { "name": "python3", "display_name": "Python 3" }
  },
  "cells": [
    { "cell_type": "markdown", "source": ["# Title"] },
    { "cell_type": "code", "source": ["!pip install ...\n", "import torch\n", "..."] }
  ]
}
```

### GitHub Push Workflow
```bash
gh repo clone clowlove/clowlove /tmp/repo
mkdir -p /tmp/repo/notebooks
# write notebook JSON to /tmp/repo/notebooks/
cd /tmp/repo && git add . && git commit -m "Add notebooks" && git push
```

### Key Colab Patterns
- Use `@param` decorator for UI sliders/dropdowns in code cells
- Cell decorations: `# @title My Title`, `# @markdown`
- GPU check: `torch.cuda.is_available()`
- Mount Drive: `from google.colab import drive; drive.mount('/content/drive')`

### Useful Colab Snippets
```python
# GPU check
import torch
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Install in Colab
!pip install transformers torch accelerate -q

# Model loading with GPU
model = AutoModelForCausalLM.from_pretrained(
    "model/id",
    torch_dtype=torch.float16,
    device_map="auto"
)
```