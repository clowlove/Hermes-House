# Contributing

## 添加新技能

在 `~/.hermes/skills/<category>/<skill-name>/` 下创建：

```
<skill-name>/
├── SKILL.md      # 技能文档（必需）
└── skill.json    # 元数据（必需）
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: 技能描述
version: 1.0.0
author: Your Name
license: MIT
---

# My Skill

技能详细说明...
```

### skill.json 格式

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "技能描述",
  "author": "Your Name",
  "license": "MIT",
  "platforms": ["linux", "macos"],
  "commands": [],
  "tags": ["tag1", "tag2"],
  "hermes": {
    "skill_category": "devops",
    "compatibility": ["hermes-agent >= 1.0.0"]
  },
  "files": ["SKILL.md"],
  "last_updated": "2026-05-03",
  "status": "stable"
}
```

## 推送流程

```bash
git add skills/<skill-name>/
git commit -m "feat: add <skill-name>"
git push origin main
```

CI 自动验证结构。