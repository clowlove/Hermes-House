# 🏠 Hermes House

> Hermes Agent 技能集合 - 让 AI 助手更强大

[![GitHub stars](https://img.shields.io/github/stars/clowlove/Harmes-House)](https://github.com/clowlove/Harmes-House/stargazers)
[![License](https://img.shields.io/github/license/clowlove/Harmes-House)](LICENSE)

---

## 📦 技能列表

### 🛠️ 开发运维类

| 技能 | 说明 | 状态 |
|------|------|------|
| [model-fallback](skills/model-fallback.md) | 模型故障转移，自动切换备用模型 | ✅ |
| [scrapling](skills/scrapling.md) | 自适应 Web 爬虫框架 | ✅ |
| xurl | X/Twitter API 交互工具 | 📋 需配置 |
| blogwatcher | RSS 新闻监控 | 📋 需配置 |

### 🌐 数据采集类

| 技能 | 说明 | 状态 |
|------|------|------|
| scrapling | 反爬绕过 + 自适应解析 | ✅ |

---

## 🚀 快速开始

### 安装技能

将技能复制到 `~/.hermes/skills/` 目录：

```bash
# 克隆仓库
git clone https://github.com/clowlove/Harmes-House.git ~/.hermes/skills

# 或复制单个技能
cp -r skills/model-fallback ~/.hermes/skills/devops/
```

### 使用技能

在 Hermes Agent 中直接使用技能名称即可触发：

```
使用 model-fallback 技能配置模型故障转移
```

---

## 📁 目录结构

```
Harmes-House/
├── README.md              # 本文件
├── LICENSE               # MIT 许可证
├── CONTRIBUTING.md       # 贡献指南
├── skills/               # 技能目录
│   ├── model-fallback/   # 模型故障转移
│   │   ├── SKILL.md
│   │   └── skill.json
│   └── scrapling/        # Web 爬虫
│       ├── SKILL.md
│       └── skill.json
├── scripts/              # 实用脚本
├── docs/                 # 详细文档
└── .github/              # GitHub 配置
    └── workflows/        # CI/CD 工作流
```

---

## 🤝 贡献

欢迎贡献技能！

请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何添加新技能。

---

## 📚 相关资源

- [Hermes Agent 官方文档](https://github.com/user/hermes-agent)
- [Hermes Skills Hub](https://github.com/user/hermes-agent/skills)
- [OpenClaw 技能市场](https://clawhub.ai)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
---
*🤖 Hermes Agent GitHub Demo - 2026-05-04 10:08*
