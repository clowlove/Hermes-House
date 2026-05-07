---
name: scrapling
description: Scrapling - 自适应 Web 爬虫框架，支持反爬绕过、自动元素定位、MCP 集成。47k+ stars 的生产级爬虫库。
version: 0.9.0
author: D4Vinci + Hermes Agent
license: BSD-3-Clause
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3, pip]
  api_keys: []
metadata:
  hermes:
    tags: [web-scraping, crawling, anti-bot, cloudflare, adaptive, mcp]
    homepage: https://github.com/D4Vinci/Scrapling
    github_stars: "47.2k"
---

# Scrapling — 自适应 Web 爬虫框架

47k+ stars 的生产级 Python 爬虫库，支持反爬绕过、自动元素定位、浏览器自动化、MCP 集成。

> [!NOTE]
> Scrapling 是一个自适应网页爬取框架，处理从单次请求到全规模爬取的各种场景。
> 解析器能学习网站变化并在页面更新时自动重新定位元素。

---

## 核心概念

| 类 | 用途 | 特点 |
|---|---|---|
| `Fetcher` | HTTP 请求 | 快速，轻量，TLS 指纹伪装，HTTP/3 |
| `StealthyFetcher` | 隐身请求 | 绕过 Cloudflare Turnstile，反爬指纹伪装 |
| `DynamicFetcher` | 动态渲染 | Playwright Chromium 浏览器自动化 |
| `Spider` | 爬虫框架 | 并发、暂停/恢复、流式输出、多会话 |
| `ProxyRotator` | 代理轮换 | 循环/自定义策略 |

---

## 快速开始

### 1. 安装

```bash
# 基础安装（仅解析器）
pip install scrapling

# 安装 fetcher 依赖（HTTP/浏览器支持）
pip install "scrapling[fetchers]"
scrapling install                    # 下载浏览器和依赖
scrapling install --force            # 强制重装

# 安装所有功能
pip install "scrapling[all]"
```

### 2. 基础 HTTP 请求

```python
from scrapling.fetchers import Fetcher, FetcherSession

# 单次请求
page = Fetcher.get('https://example.com')
titles = page.css('h1::text').getall()
print(titles)

# 会话请求（保持 Cookie）
with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/')
    quotes = page.css('.quote .text::text').getall()
```

### 3. 隐身抓取（绕过反爬）

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# 单次隐身请求
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch(
    'https://nopecha.com/demo/cloudflare',
    headless=True,
    network_idle=True,
    solve_cloudflare=True
)
data = page.css('#padded_content a').getall()

# 隐身会话
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://example.com')
```

### 4. 动态网站（JavaScript 渲染）

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

# 单次动态请求
page = DynamicFetcher.fetch(
    'https://quotes.toscrape.com/',
    headless=True,
    network_idle=True
)
quotes = page.xpath('//span[@class="text"]/text()').getall()

# 动态会话
with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://example.com')
```

### 5. 自适应解析（网站结构变化仍有效）

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

### BeautifulSoup 风格

```python
page.find_all('div', {'class': 'quote'})       # 字典语法
page.find_all('div', class_='quote')           # 关键字语法
page.find_by_text('quote', tag='div')          # 按文本内容查找
```

### 正则/文本搜索

```python
page.re(r'\d+\.\d{2}')                   # 正则匹配
page.search('price:')                    # 文本搜索
```

### 元素导航

```python
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')  # 兄弟节点
parent = first_quote.parent                                   # 父元素
similar = first_quote.find_similar()                          # 相似元素
```

---

## Spider 爬虫框架

### 基础 Spider

```python
from scrapling.spiders import Spider, Response, Request

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        # 跟进分页
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"爬取 {len(result.items)} 条数据")
result.items.to_json("quotes.json")      # JSON 导出
result.items.to_jsonl("quotes.jsonl")    # JSONL 导出
```

### Spider 配置选项

```python
class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    # 并发控制
    concurrent_requests = 5              # 并发数
    delay = 1                             # 延迟（秒）
    per_domain_throttle = 2              # per-domain 并发限制

    # 代理和反爬
    proxy = "http://proxy:8080"          # 代理
    robots_txt_obey = True               # 遵守 robots.txt
    blocked_request_detection = True      # 自动检测并重试被阻止的请求

    async def parse(self, response: Response):
        pass
```

### 暂停/恢复

```bash
# 运行爬虫，Ctrl+C 优雅暂停
QuotesSpider(crawldir="./crawl_data").start()

# 恢复爬取（传相同 crawldir）
QuotesSpider(crawldir="./crawl_data").start()
```

### 流式输出（实时处理）

```python
async for item in QuotesSpider().stream():
    print(f"实时数据: {item}")
```

### 开发模式（缓存响应）

```python
class MySpider(Spider):
    name = "demo"
    dev_mode = True  # 首次运行缓存响应，后续直接使用缓存

    async def parse(self, response: Response):
        pass
```

### 多会话 Spider

```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")      # 走隐身会话
            else:
                yield Request(link, sid="fast")         # 走快速会话
```

---

## 代理轮换

```python
from scrapling.fetchers import ProxyRotator

# 循环代理
rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'])

page = StealthyFetcher.fetch(
    'https://example.com',
    proxy=rotator.get_next()
)

# 自定义策略
from scrapling.fetchers import ProxyRotator

def custom_strategy(proxies):
    # 每次返回不同的代理
    import random
    return random.choice(proxies)

rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'], strategy=custom_strategy)
```

---

## CLI 工具（无需写代码）

```bash
# 交互式 Shell
scrapling shell

# 直接提取内容
scrapling extract get 'https://example.com' content.md              # 转为 Markdown
scrapling extract get 'https://example.com' content.txt             # 纯文本
scrapling extract get 'https://example.com' content.html            # HTML

# 带选择器
scrapling extract get 'https://example.com' content.md --css-selector 'h1::text' --impersonate 'chrome'

# 隐身抓取（绕过 Cloudflare）
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' result.html --solve-cloudflare
```

---

## MCP Server（AI 集成）

```bash
# 启动 MCP 服务器
pip install "scrapling[ai]"
scrapling mcp
```

```python
# 或在 Python 中
from scrapling.mcp import serve
serve()
```

然后配置到 AI Agent 的 MCP 客户端，即可通过自然语言控制爬虫。

---

## 异步支持

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession, AsyncDynamicSession

async def main():
    # 异步隐身会话
    async with AsyncStealthySession(max_pages=2) as session:
        tasks = []
        urls = ['https://example.com/page1', 'https://example.com/page2']
        for url in urls:
            tasks.append(session.fetch(url))

        results = await asyncio.gather(*tasks)
        print(session.get_pool_stats())  # 查看浏览器标签池状态

    # 异步动态会话
    async with AsyncDynamicSession() as session:
        page = await session.fetch('https://quotes.toscrape.com/')
        quotes = page.css('.quote .text::text').getall()

asyncio.run(main())
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
        # 返回 None 跳过，或返回 Request 重试
        return None

# 错误请求自动重试
class MySpider(Spider):
    blocked_request_detection = True  # 自动检测并重试

    async def parse(self, response: Response):
        pass
```

---

## 依赖要求

| 依赖 | 说明 |
|------|------|
| Python | >= 3.10 |
| lxml | XML/HTML 解析 |
| cssselect | CSS 选择器 |
| orjson | 快速 JSON（10x faster） |
| playwright | 动态渲染（可选） |
| tld | 顶级域名提取 |

安装可选依赖：
```bash
pip install "scrapling[fetchers]"     # HTTP/浏览器支持
pip install "scrapling[ai]"           # MCP 支持
pip install "scrapling[shell]"         # CLI Shell 支持
pip install "scrapling[all]"           # 所有可选依赖

scrapling install                      # 安装浏览器依赖
```

---

## 性能基准

Scrapling 解析器速度基准（5000 嵌套元素）：

| 库 | 耗时(ms) | vs Scrapling |
|----|:--------:|:------------:|
| **Scrapling** | 2.02 | 1.0x |
| Parsel/Scrapy | 2.04 | 1.01x |
| Raw Lxml | 2.54 | 1.26x |
| PyQuery | 24.17 | ~12x |
| Selectolax | 82.63 | ~41x |
| BS4 + Lxml | 1584.31 | ~784x |

自适应元素查找性能：

| 库 | 耗时(ms) | vs Scrapling |
|----|:--------:|:------------:|
| **Scrapling** | 2.39 | 1.0x |
| AutoScraper | 12.45 | ~5.2x |

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
| 暂停/恢复 | ✅ | ❌ | ✅ | ❌ |
| 流式输出 | ✅ | ❌ | ⭐⭐ | ❌ |

---

## 下一步

1. 安装可选依赖：`pip install "scrapling[all]" && scrapling install`
2. 查看官方文档：https://scrapling.readthedocs.io
3. 查看示例代码：https://github.com/D4Vinci/Scrapling/tree/main/examples