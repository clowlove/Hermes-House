---
name: hermes-tweet
description: "Hermes Agent X/Twitter plugin: search tweets, post tweets, read replies, send DMs, monitor accounts, run extraction jobs, and read trends through Xquik."
version: 0.1.6
author: Xquik
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [hermes, uv]
  api_keys: [XQUIK_API_KEY]
metadata:
  hermes:
    tags: [hermes-agent, xquik, twitter, x, tweet-search, tweet-posting, social-media, automation]
    homepage: https://github.com/Xquik-dev/hermes-tweet
---

# Hermes Tweet

Hermes Tweet 是 Hermes Agent 的原生 X/Twitter 插件。它把 Xquik 的 X
automation API 接入 Hermes，适合需要搜索推文、读取用户资料、查看回复、
发布推文、回复推文、发送 DM、管理 monitor、启动 extraction jobs、处理媒体
和读取趋势的 Agent 工作流。

适合这些场景：

- search tweets / search Twitter / search X
- read tweet replies and inspect conversations
- look up X users, account data, media, trends, and monitors
- post tweets and post replies after explicit approval
- send DMs, follow users, or run other account actions after explicit approval
- run X extraction jobs and social-media automation from Hermes Agent

Hermes Tweet 与只包装单个 CLI 的技能不同。它注册为 Hermes plugin toolset，
提供 `tweet_explore`、`tweet_read` 和 `tweet_action` 三个工具，并把写入类
操作默认隔离到显式启用的 action 工具中。

## Install

推荐用 Hermes 插件安装：

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

也可以把 PyPI 包安装进 Hermes Python 环境：

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

## Configure

创建 Xquik API key 后，把它放进 Hermes 运行环境：

```bash
export XQUIK_API_KEY="xq_..."
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

`HERMES_TWEET_ENABLE_ACTIONS=false` 是推荐默认值。它让 Hermes 可以安全使用
read-only 工具做 tweet search、account reads、trend research 和 planning，
但不会暴露发推、回复、DM、follow、monitor 变更等 action endpoints。

只有在工作流确实需要写操作，并且用户明确批准后，才设置：

```bash
export HERMES_TWEET_ENABLE_ACTIONS="true"
```

## Tools

| Tool | Purpose |
|------|---------|
| `tweet_explore` | Search the bundled Xquik endpoint catalog. No API call required. |
| `tweet_read` | Call catalog-listed read-only endpoints for search, users, trends, media, and reports. |
| `tweet_action` | Call write-like or private endpoints. Hidden or disabled unless actions are enabled. |

Always start with `tweet_explore` when you need to find the right endpoint.
Then call `tweet_read` for read-only API paths. Use `tweet_action` only for
approved writes or private account operations.

## Workflow

1. Use `tweet_explore` with a short query such as `tweet search`, `post tweet`,
   `read replies`, `send DM`, `user lookup`, `export followers`, or `trends`.
2. Pick a catalog-listed `/api/v1/...` path.
3. Use `tweet_read` for GET endpoints that are not marked as actions.
4. Use `tweet_action` only when the user approved the exact action, endpoint,
   and payload.

## Examples

Search tweets:

```json
{"query":"tweet search","method":"GET"}
```

Then call `tweet_read` with the catalog path, for example:

```json
{"path":"/api/v1/x/tweets/search","query":{"q":"AI agents","limit":25}}
```

Post a tweet:

```json
{"query":"post tweet","include_actions":true}
```

Then call `tweet_action` only after the user approves the text:

```json
{"path":"/api/v1/x/tweets","method":"POST","body":{"account":"@example","text":"Hello from Hermes Tweet"},"reason":"Post the user-approved tweet."}
```

## Safety

- Never ask the user to paste API keys, passwords, cookies, or tokens into chat.
- Never pass credentials as tool arguments.
- Use only catalog-listed `/api/v1/...` endpoints.
- Keep `tweet_action` disabled for unattended sessions unless the workflow has
  an explicit approval step.
- Do not retry writes through alternate routes after auth, account-state, or
  policy errors.

## Links

- Repository: https://github.com/Xquik-dev/hermes-tweet
- PyPI: https://pypi.org/project/hermes-tweet/
- Guide: https://docs.xquik.com/guides/hermes-tweet
