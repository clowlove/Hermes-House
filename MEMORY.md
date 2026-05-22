# Hermès 长期记忆

> 每次对话开始时读取此文件，恢复对用户和项目的长期记忆。

---

## 用户信息

- **用户**: 亨利 (Henry)，GitHub: [REDACTED]
- **语言**: 中文
- **沟通风格**: 简洁直接，不废话
- **Telegram**: [Telegram Handle]（已连接）
- **时区**: 中国（晚间休息）

---

## 项目背景

- **母仓库**: [[REDACTED]/Harmes-House](https://github.com/[REDACTED]/Harmes-House)
- **定位**: AI Agent 进化基地，参考 NousResearch/hermes-agent 架构
- **备份仓库**: [REDACTED]/hermes-backups（私有，每日 01:00 自动备份）
- **TrendRadar MCP**: 运行在 port 3333，9 个话题，255 条新闻

---

## 技术栈

- **模型**: minimaxai/minimax-m2.6（默认）、NVIDIA NIM（备用）
- **GitHub PAT**: [REDACTED]
- **GitHub CLI**: v2.63.2，已认证
- **HF CLI**: 已配置，账户 cntalk
- **Claude Code**: 可用
- **备份**: hermes-backups 私有仓库，7 天轮转

---

## 用户偏好

- ✅ 偏好简洁直接的回复
- ✅ 中文交流
- ✅ PR workflow（不直接推 main）
- ✅ Telegram 推送（TrendRadar）
- ✅ 晚上休息（不影响）
- ❌ 不做破坏性 git 操作（如 hard reset 到 upstream/main）
- ❌ 163 邮箱已放弃

---

## 持久约定

1. **GitHub 推送必须走 PR** — `git push` → 分支 → PR → merge
2. **备份必须验证** — restore 后检查完整性
3. **危险操作先确认** — 删除、重写、强制覆盖等
4. **Hugging Face 资源归户主** — cntalk 账户下

---

## 当前进行中的项目

- [ ] PR #15（Curator 进化系统）— 已合并 ✓
- [ ] Hermès Agent 身份系统建设（AGENTS.md + MEMORY.md）— 进行中
- [ ] Daily AI Digest GitHub Action — 已实现
- [ ] Skills 格式升级（参考 yupi-skill）— 待完成

---

## 学习参考

- **鱼皮的 github-claw**: 用 GitHub 打造 AI Agent 的完整方案
  - AGENTS.md + MEMORY.md 机制
  - GitHub Actions 自动化
  - Skills 技能包格式
- **鱼皮的 yupi-skill**: 252 ⭐，思维蒸馏成 Agent Skill 的标准格式

---

*最后更新: 2026-05-06*