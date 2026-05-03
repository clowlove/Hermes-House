---
name: scrapling
description: Scrapling - 自适应 Web 爬虫框架，支持反爬绕过、自动元素定位、MCP 集成。42k stars 的专业级爬虫库。
version: 0.4.7
author: D4Vinci + Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3, pip]
  api_keys: []
metadata:
  hermes:
    tags: [web-scraping, crawling, anti-bot, cloudflare, adaptive, mcp]
    homepage: https://github.com/D4Vinci/Scrapling
    github_stars: "42.2k"
---

# Scrapling — 自适应 Web 爬虫框架

42k stars 的专业级 Python 爬虫库，支持反爬绕过、自动元素定位、浏览器自动化。

---

## 核心概念

| 类 | 用途 | 特点 |
|---|---|---|
| `Fetcher` | HTTP 请求 | 快速，轻量，支持 TLS 指纹伪装 |
| `StealthyFetcher` | 隐身请求 | 绕过 Cloudflare Turnstile，反爬 |
| `DynamicFetcher` | 动态渲染 | 支持 Playwright 浏览器自动化 |
| `Spider` | 爬虫框架 | 并发、暂停/恢复、流式输出 |

---

## 快速开始

### 1. 基础 HTTP 请求

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com')
titles = page.css('h1::text').getall()
print(titles)
```

### 2. 隐身抓取（绕过反爬）

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch(
    'https://nopecha.com/demo/cloudflare',
    headless=True,
    network_idle=True
)
data = page.css('#padded_content a').getall()
```

### 3. 动态网站（JavaScript 渲染）

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://quotes.toscrape.com/',
    headless=True,
    network_idle=True
)
quotes = page.css('.quote .text::text').getall()
```

### 4. 自适应解析（网站结构变化仍有效）

```python
# auto_save 首次自动保存选择器
products = page.css('.product', auto_save=True)

# 后续使用 adaptive=True 自动适应变化
products = page.css('.product', adaptive=True)
```

---

## 选择器语法

### CSS 选择器

```python
page.css('div.item::text').getall()      # 获取文本
page.css('a::attr(href)').getall()       # 获取属性
page.css('.product', first=True).get()   # 获取第一个
```

### XPath 选择器

```python
page.xpath('//div[@class="item"]/text()').getall()
```

### 正则/文本搜索

```python
page.re(r'\d+\.\d{2}')                   # 正则匹配
page.search('price:')                    # 文本搜索
```

---

## Session 会话管理

```python
from scrapling.fetchers import FetcherSession, StealthySession

# 保持 Cookie 和状态
with FetcherSession(impersonate='chrome') as session:
    session.post('https://example.com/login', data={'user': 'test'})
    page = session.get('https://example.com/dashboard')

# 隐身会话
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://example.com')
```

---

## Spider 爬虫框架

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}

MySpider().start()
```

### Spider 配置选项

```python
class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]
    concurrency = 5              # 并发数
    delay = 1                   # 延迟（秒）
    robots_txt_obey = True      # 遵守 robots.txt
    proxy = "http://proxy:8080" # 代理

    async def parse(self, response: Response):
        # 解析逻辑
        pass
```

---

## 代理轮换

```python
from scrapling.fetchers import ProxyRotator

rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'])

page = StealthyFetcher.fetch(
    'https://example.com',
    proxy=rotator.get_next()
)
```

---

## 高级功能

### MCP Server（AI 集成）

```bash
# 启动 MCP 服务器
scrapling mcp

# 或在 Python 中
from scrapling.mcp import serve
serve()
```

### CLI 工具（无需写代码）

```bash
# 直接从终端爬取
scrapling fetch https://example.com --selector "h1::text"

# 查看文档
scrapling --help
```

---

## 错误处理

```python
from scrapling.fetchers import Fetcher
from scrapling.spiders import Spider

# 单次请求错误处理
try:
    page = Fetcher.get('https://example.com')
except Exception as e:
    print(f"请求失败: {e}")

# Spider 错误处理
class MySpider(Spider):
    async def handle_error(self, error, request):
        print(f"爬取失败: {request.url} - {error}")
        # 返回重试请求或跳过
        return None
```

---

## 依赖要求

| 依赖 | 说明 |
|------|------|
| Python | >= 3.9 |
| lxml | XML/HTML 解析 |
| cssselect | CSS 选择器 |
| orjson | 快速 JSON（10x faster） |
| playwright | 动态渲染（可选） |
| tld | 顶级域名提取 |

安装可选依赖：
```bash
pip install scrapling[playwright]  # 动态渲染支持
pip install scrapling[all]         # 所有可选依赖
```

---

## 与其他工具对比

| 功能 | Scrapling | requests | Scrapy | Playwright |
|------|-----------|----------|--------|------------|
| 难度 | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 反爬绕过 | ✅✅✅✅✅ | ❌ | ⭐⭐ | ⭐⭐⭐ |
| 自适应解析 | ✅ | ❌ | ❌ | ❌ |
| 规模爬取 | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 浏览器自动化 | ✅ | ❌ | ❌ | ✅ |
| AI/MCP 集成 | ✅ | ❌ | ❌ | ❌ |

---

## 下一步

1. 安装可选依赖：`pip install scrapling[playwright]`
2. 查看官方文档：https://scrapling.readthedocs.io
3. 查看示例代码：https://github.com/D4Vinci/Scrapling/tree/main/examples