# Hermes House

> Hermes Agent 技能仓库 — 自动化你的 AI 工作流

![Validate Skills](https://github.com/clowlove/Harmes-House/workflows/Validate%20Skills/badge.svg)
![GitHub Pages](https://img.shields.io/github/pages/clowlove/Harmes-House)

## 概览

Harmes-House 是 Hermes Agent 的技能中心，收录 AI 工程、自动化、创意工具等领域的高质量技能。

## 快速开始

```bash
# 查看可用技能
ls ~/.hermes/skills/

# 查看技能详情
cat ~/.hermes/skills/<skill-name>/SKILL.md
```

## 技能分类

- **devops**: 部署、运维、模型服务
- **github**: GitHub 工作流自动化
- **mlops**: 机器学习工程
- **creative**: 创意工具（图像、视频、音乐）
- **research**: 学术研究辅助
- **productivity**: 效率工具（文档、演示、邮件）
- **smart-home**: 智能家居控制
- **autonomous-ai-agents**: AI Agent 编排

## 最新更新

<!-- skills:update -->

## CI/CD

所有技能推送后自动验证结构完整性：
- `SKILL.md` 存在且非空
- `skill.json` 有效的 JSON schema

---

Licensed under MIT. Built with ❤️ for Hermes Agent.