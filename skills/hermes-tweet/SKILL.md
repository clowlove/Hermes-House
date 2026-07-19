---
name: hermes-tweet
description: "Use the native Hermes Agent plugin for X research, monitoring, extraction, and approval-gated X actions through Xquik. Trigger for tweet search, replies, users, trends, monitors, media, DMs, posting, or other X/Twitter workflows. Not affiliated with X Corp."
license: MIT
allowed-tools:
  - tweet_explore
  - tweet_read
  - tweet_action
metadata:
  version: 0.1.8
  author: Burak Bayır (@kriptoburak), Xquik
  platforms: [linux, macos]
  prerequisites:
    commands: [hermes, uv]
    api_keys: [XQUIK_API_KEY]
  hermes:
    tags: [hermes-agent, xquik, twitter, x, tweet-search, tweet-posting, social-media, automation]
    homepage: https://github.com/Xquik-dev/hermes-tweet
---

# Hermes Tweet

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.

Hermes Tweet 是 Hermes Agent 的原生 X/Twitter 插件。它把 Xquik 的 X
automation API 接入 Hermes，适合需要搜索推文、读取用户资料、查看回复、
发布推文、回复推文、发送 DM、管理 monitor、启动 extraction jobs、处理媒体
和读取趋势的 Agent 工作流。

当前 `0.1.8` 版本需要 Python `>=3.11` 和支持第三方插件的 Hermes Agent。
这是 Hermes 原生 plugin toolset，不是 MCP server。

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

如果插件已安装但未启用，运行 `hermes plugins enable hermes-tweet`。修改运行
环境后，在交互式会话运行 `/reload`，或重启 gateway 和 cron 进程。

也可以把 PyPI 包安装进 Hermes Python 环境：

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

## Configure

创建 Xquik API key 后，把它放进 Hermes 运行环境。不要把 key 值粘贴到
prompt、issue、日志或工具参数中：

```bash
export XQUIK_API_KEY="xq_..."
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

`HERMES_TWEET_ENABLE_ACTIONS=false` 是推荐默认值。它让 Hermes 可以安全使用
read-only 工具做 tweet search、account reads、trend research 和 planning，
但不会暴露发推、回复、DM、follow、monitor 变更等 action endpoints。

未配置 `XQUIK_API_KEY` 时，Hermes Tweet 只公开无需网络的 `tweet_explore`。
这是预期的安全门控，不是安装失败。

只有在工作流确实需要写操作，并且用户明确批准后，才设置：

```bash
export HERMES_TWEET_ENABLE_ACTIONS="true"
```

## Tools

| Tool | Purpose |
|------|---------|
| `tweet_explore` | Search the bundled Xquik endpoint catalog. No key or API call required. |
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
5. Never guess endpoints or create a direct HTTP fallback.

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
- Do not use account connection, re-authentication, API-key, billing, credit
  top-up, or support-ticket endpoints.
- Keep `tweet_action` disabled for unattended sessions unless the workflow has
  an explicit approval step.
- Do not retry writes through alternate routes after auth, account-state, or
  policy errors.

## Links

- [Repository](https://github.com/Xquik-dev/hermes-tweet)
- [PyPI](https://pypi.org/project/hermes-tweet/)
- [Guide](https://docs.xquik.com/guides/hermes-tweet)
