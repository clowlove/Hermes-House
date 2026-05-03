# 技能模板

这是一个用于创建新技能的模板文件。

## 快速开始

1. 复制 `skill-template.md` 为 `SKILL.md`
2. 复制 `skill-template.json` 为 `skill.json`
3. 修改内容为你的技能信息

---

## 示例：创建 "hello-world" 技能

### 目录结构

```
skills/
└── hello-world/
    ├── SKILL.md      # 复制自 skill-template.md
    └── skill.json    # 复制自 skill-template.json
```

### SKILL.md 内容

```markdown
---
name: hello-world
description: 一个简单的示例技能
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: []
  api_keys: []
metadata:
  hermes:
    tags: [example, template]
    homepage: https://github.com/your/repo
---

# Hello World

这是技能的详细说明。

## 安装

...

## 使用

...
```

### skill.json 内容

```json
{
  "name": "hello-world",
  "version": "1.0.0",
  "description": "一个简单的示例技能",
  "author": "Your Name",
  "license": "MIT",
  "platforms": ["linux", "macos", "windows"],
  "commands": [],
  "api_keys_needed": [],
  "tags": ["example", "template"],
  "hermes": {
    "skill_category": "devops",
    "compatibility": ["hermes-agent >= 1.0.0"]
  },
  "files": ["SKILL.md"],
  "last_updated": "2024-01-01",
  "status": "stable"
}
```

---

更多信息请查看 [CONTRIBUTING.md](../CONTRIBUTING.md)