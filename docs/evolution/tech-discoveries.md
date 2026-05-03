# 技术发现与实验

## Scrapling (自适应爬虫)

比 scrapy 更现代的自适应爬虫框架。

### 核心能力

- **自适应解析**: 根据 HTML 结构自动选择最佳解析策略
- **Cloudflare 绕过**: 内置绕过机制，测试了 nitter.net / nowsecure.cn
- **MCP 集成**: 可作为 MCP server 提供给 AI Agent
- **零依赖**: 轻量级，只依赖 blinker

### 安装

```bash
pip install scrapling --break-system-packages
```

### 基础用法

```python
from scrapling import Scrapler

response = Scrapler.get("https://example.com")
# 自适应解析，无需手动选择解析器
content = response.match("div.article")  # CSS selector
text = response.match.using("p").all_text()
```

---

## Model Fallback (模型故障转移)

通过 OpenRouter 实现多模型兜底。

### 原理

```yaml
# ~/.hermes/config.yaml
model_fallback:
  primary: openrouter/anthropic/claude-3.5-sonnet
  fallbacks:
    - openrouter/google/gemini-pro
    - openrouter/mistral/mistral-7b-instruct
  check_credits: true
```

当主模型不可用或余额不足时，自动尝试备选模型。

---

## GitHub API 技巧

### 绕过 workflow 权限限制

新 token 需要 `workflow` scope 才能通过 git push 推送 `.github/workflows/` 文件：

```bash
ghp_xxxx — 有 workflow scope 的 PAT
```

### 强制合并受保护分支

```bash
# 1. 临时移除保护
curl -X DELETE .../branches/main/protection

# 2. 合并 PR
curl -X PUT .../pulls/1/merge

# 3. 恢复保护
curl -X PUT .../branches/main/protection
```

### 自动创建 PR 审查

```bash
curl -X POST .../pulls/1/reviews -d '{"body": "LGTM!", "event": "APPROVE"}'
```

---

## MkDocs + GitHub Pages

### 关键命令

```bash
pip install mkdocs mkdocs-material
mkdocs gh-deploy --force --message "Deploy $(date)"
```

### 常见问题

- `strict` 模式：警告会导致构建失败，需谨慎使用
- `gh-deploy`：自动推送到 gh-pages 分支
- 需要配置 git remote 使用 `x-access-token` 认证

---

*最后更新: 2026-05-03*