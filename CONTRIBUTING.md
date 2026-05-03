# 🤝 贡献指南

感谢你的贡献！本文档帮助你创建和提交新技能。

---

## 技能结构

每个技能至少包含两个文件：

```
skills/
└── <skill-name>/
    ├── SKILL.md      # 技能文档（必需）
    └── skill.json    # 技能元数据（必需）
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 技能简短描述
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [command1, command2]
  api_keys: [KEY_NAME]
metadata:
  hermes:
    tags: [tag1, tag2]
    homepage: https://github.com/...
---

# 技能名称

技能详细说明...

## 安装

...

## 使用

...
```

### skill.json 格式

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "技能描述",
  "author": "Your Name",
  "license": "MIT",
  "platforms": ["linux", "macos"],
  "commands": [],
  "api_keys_needed": [],
  "tags": ["tag1", "tag2"],
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

## 技能分类

| 分类 | 说明 | 示例 |
|------|------|------|
| devops | 开发运维工具 | model-fallback, docker |
| data-science | 数据科学 | jupyter, pandas |
| mlops | 机器学习运维 | training, inference |
| social-media | 社交媒体 | xurl, blogwatcher |
| creative | 创意工具 | ascii-art, image-gen |
| productivity | 效率工具 | notion, linear |
| research | 研究工具 | arxiv, blogwatcher |

---

## 提交流程

1. **Fork** 本仓库
2. 创建新分支：`git checkout -b skills/<skill-name>`
3. 添加你的技能文件
4. 测试技能可正常使用
5. 提交 PR 并描述功能

---

## 技能审核标准

✅ **通过条件：**
- SKILL.md 和 skill.json 格式正确
- 文档清晰，包含安装和使用说明
- 不包含敏感信息（API keys 等）
- 遵循 MIT 许可证

❌ **拒绝条件：**
- 包含恶意代码
- 侵犯他人版权
- 文档不完整或缺失
- 包含硬编码的凭据

---

## 问题反馈

如果你发现问题或有建议，请提交 [Issue](https://github.com/clowlove/Harmes-House/issues)。

---

感谢你的贡献！ 🎉