---
name: custom-openai-provider
description: Configure any OpenAI-compatible API as a Hermes model provider — NVIDIA NIM, Together AI, Fireworks, Groq, local vLLM/Ollama, or any custom endpoint. Covers the critical provider-clearing pitfall.
version: 1.0.0
metadata:
  hermes:
    tags: [models, providers, nvidia-nim, custom-endpoint, openai-compatible]
---

# Custom OpenAI-Compatible Provider Setup

Configure Hermes to use any OpenAI-compatible API endpoint as its model provider.

## When to Use

- NVIDIA NIM (https://integrate.api.nvidia.com/v1)
- Together AI, Fireworks AI, Groq
- Local vLLM, Ollama, LM Studio
- Any self-hosted OpenAI-compatible server

## Key Steps

### 1. Add API Key

Use `hermes config env-path` to find the .env location. Add your key there (use terminal + sed for the protected file).

### 2. Configure Model Settings

```bash
hermes config set model.default "provider/model-name"
hermes config set model.base_url "https://api.example.com/v1"
hermes config set model.api_key "env:YOUR_ENV_VAR_NAME"
```

### 3. CRITICAL: Clear Provider

**PITFALL**: If `model.provider` is set to a previous provider (e.g., "xiaomi", "openrouter"), Hermes routes requests incorrectly. MUST clear it:

```bash
hermes config set model.provider ""
```

This is the #1 mistake when switching from a named provider to a custom endpoint.

### 4. Restart

Exit CLI and restart hermes. For gateway: `hermes gateway restart`.

## NVIDIA NIM

- Base URL: `https://integrate.api.nvidia.com/v1`
- Get key: https://build.nvidia.com
- Models: `deepseek-ai/deepseek-v4-pro`, `meta/llama-3.1-405b-instruct`, etc.

### List Available Models
```bash
curl -s https://integrate.api.nvidia.com/v1/models \
  -H "Authorization: Bearer nvapi-YOUR_KEY" | jq -r '.data[].id'
```

### Test Model Availability
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer nvapi-YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "MODEL_NAME", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}'
```

### Diagnose 403 Errors
If `/v1/models` works (returns model list) but `/v1/chat/completions` returns 403:
1. **Check account credits** - https://build.nvidia.com → Billing/Credits
2. **Free tier exhausted** - New accounts have limited free credits
3. **Key permissions** - May need to regenerate key with inference permissions
4. **Model not enabled** - Some models require manual activation in console

### Test Multiple Models
When unsure which models are available/working, batch test:
```bash
for model in model1 model2 model3; do
  echo -n "$model: "
  curl -s "https://integrate.api.nvidia.com/v1/chat/completions" \
    -H "Authorization: Bearer nvapi-YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$model\", \"messages\": [{\"role\": \"user\", \"content\": \"Hi\"}], \"max_tokens\": 10}" \
    | grep -q '"choices"' && echo "✅" || echo "❌"
done
```

### Reasoning Models
Some models (e.g., `minimaxai/minimax-m2.7`) return `reasoning_content` field instead of `content` when `max_tokens` is too low. Use `max_tokens: 100+` to get actual responses.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Requests go to wrong provider | `hermes config set model.provider ""` |
| 401 Unauthorized | Verify key with curl test |
| 403 Forbidden (can list models) | Account has no credits or free tier exhausted |
| 403 Forbidden (cannot list models) | Invalid key or key format wrong |
| Model not found | List models via /v1/models endpoint |
| Changes not生效 | Restart CLI session |
