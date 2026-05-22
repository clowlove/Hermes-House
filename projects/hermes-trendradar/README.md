# Hermès TrendRadar

AI 驱动的热点话题聚合工具，支持多平台新闻追踪和情感分析。

[![npm](https://img.shields.io/npm/v/hermes-trendradar?style=for-the-badge)](https://www.npmjs.com/package/hermes-trendradar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## 安装

```bash
npm install hermes-trendradar
```

## 使用方法

```bash
# 查看热点话题（Free: 限10条, Pro: 无限）
trendradar trending -n 20

# 聚合新闻（Pro only）
trendradar aggregate --query AI

# 情感分析（Pro only）
trendradar sentiment --topic AI
```

## 定价

| 计划 | 价格 | 功能 |
|------|------|------|
| **Free** | 免费 | trending 最多10条，3个平台 |
| **Pro** | $10/月 | 无限结果、sentiment、aggregate、全平台 |

升级到 Pro：运行 `trendradar upgrade` 获取说明。

## 开发

```bash
npm install
npm run build
```

## 支持这个项目

如果你觉得这个工具对你有帮助：

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Sponsor-orange?style=for-the-badge&logo=github-sponsors)](https://github.com/sponsors/[REDACTED])

## 许可证

MIT