---
name: report-generation
description: 生成结构化报告 - Markdown/HTML/PDF 格式的聚合报告、趋势分析、数据摘要。支持定时生成和推送。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3, markdown, wkhtmltopdf]
  python_libs: [markdown, weasyprint, jinja2]
  api_keys: []
metadata:
  hermes:
    tags: [report, pdf, markdown, html, generation, summary]
    homepage: https://github.com/hermes-agent
---

# 报告生成

生成 Markdown/HTML/PDF 格式的结构化报告。适合每日趋势摘要、数据分析报告、定时推送等场景。

---

## 支持格式

| 格式 | 工具 | 特点 |
|------|------|------|
| Markdown | stdlib | 纯文本，易于推送 |
| HTML | Jinja2 | 精美样式，可转 PDF |
| PDF | WeasyPrint/wkhtmltopdf | 最终交付 |

---

## 快速开始

### 1. Markdown 报告

```python
def generate_markdown_report(title, sections):
    """生成 Markdown 报告"""
    md = f"# {title}\n\n"
    md += f"_生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
    
    for section_title, content in sections.items():
        md += f"## {section_title}\n\n{content}\n\n"
    
    return md

# 使用示例
report = generate_markdown_report(
    "每日趋势摘要",
    {
        "热点话题": "- AI: 1000 mentions, 正面情绪 78%\n- 特斯拉: 800 mentions, 正面情绪 65%",
        "平台分布": "| 平台 | 数量 | 占比 |\n|-----|------|-----|\n| 微博 | 150 | 35% |\n| 知乎 | 120 | 28% |",
        "预测趋势": "预计下周 AI 相关话题将持续增长"
    }
)

with open('report.md', 'w') as f:
    f.write(report)
```

### 2. HTML 报告（带样式）

```python
from jinja2 import Template

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
               max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 10px; }
        h2 { color: #0f3460; margin-top: 30px; }
        .meta { color: #666; font-size: 0.9em; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #0f3460; color: white; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .summary { background: #f1f3f5; padding: 15px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p class="meta">生成时间: {{ timestamp }}</p>
    
    {% for section_title, content in sections.items() %}
    <h2>{{ section_title }}</h2>
    <div class="summary">{{ content }}</div>
    {% endfor %}
</body>
</html>
"""

def generate_html_report(title, sections, timestamp=None):
    template = Template(html_template)
    return template.render(
        title=title,
        sections=sections,
        timestamp=timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

html_report = generate_html_report(
    "每日趋势摘要",
    {
        "热点话题": "AI 相关话题位居榜首，全网讨论量超过 10 万次",
        "情感分析": "正面情绪占比 <span class='positive'>78%</span>，负面情绪占比 <span class='negative'>12%</span>"
    }
)

with open('report.html', 'w') as f:
    f.write(html_report)
```

### 3. PDF 报告

```python
# 方法1: WeasyPrint (推荐)
from weasyprint import HTML

def markdown_to_pdf(markdown_content, output_path):
    """Markdown -> HTML -> PDF"""
    import markdown
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
    HTML(string=f"<html><body style='font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px;'>{html_content}</body></html>").write_pdf(output_path)

# 方法2: wkhtmltopdf
import subprocess

def html_to_pdf(html_path, output_path):
    subprocess.run([
        'wkhtmltopdf',
        '--page-size', 'A4',
        '--margin-top', '20mm',
        '--margin-bottom', '20mm',
        html_path,
        output_path
    ], check=True)

# 使用示例
markdown_to_pdf(report, 'report.pdf')
```

---

## 趋势报告模板

```python
def generate_trend_report(topic_data, platform_stats, predictions):
    """生成趋势分析报告"""
    
    sections = {
        "概览": f"""
- **监测话题**: {topic_data['topic']}
- **时间范围**: {topic_data['date_range']}
- **总讨论量**: {topic_data['total_mentions']:,}
- **独立来源**: {topic_data['unique_sources']}
        """.strip(),
        
        "平台分布": _format_table(platform_stats, ['平台', '数量', '占比']),
        
        "情感趋势": f"""
- **平均情感得分**: {topic_data['avg_sentiment']:.2%} (正面)
- **情感变化趋势**: {'↑ 上升' if topic_data['sentiment_trend'] > 0 else '↓ 下降'} {abs(topic_data['sentiment_trend']):.1%}
- **主要正面来源**: {topic_data['top_positive_sources']}
- **主要负面来源**: {topic_data['top_negative_sources']}
        """.strip(),
        
        "预测与建议": predictions
    }
    
    report = generate_markdown_report(
        f"📊 {topic_data['topic']} 趋势分析报告",
        sections
    )
    
    return report

def _format_table(data, headers):
    """格式化表格为 Markdown"""
    md = f"| {' | '.join(headers)} |\n"
    md += f"| {' | '.join(['---'] * len(headers))} |\n"
    for row in data:
        md += f"| {' | '.join(str(x) for x in row)} |\n"
    return md
```

---

## 定时报告生成

```python
# Cron 任务中调用
import sqlite3
from datetime import datetime, timedelta

def daily_report():
    """每日趋势报告生成"""
    
    # 1. 从数据库获取数据
    with sqlite3.connect('~/.hermes/data/agent.db') as db:
        cursor = db.execute('''
            SELECT topic, COUNT(*) as count 
            FROM news_aggregates 
            WHERE created_at > ?
            GROUP BY topic
            ORDER BY count DESC
            LIMIT 10
        ''', ((datetime.now() - timedelta(days=1)).isoformat(),))
        
        top_topics = cursor.fetchall()
    
    # 2. 生成报告
    report = generate_markdown_report(
        f"📰 每日资讯摘要 - {datetime.now().strftime('%Y-%m-%d')}",
        {"Top 话题": _format_table(top_topics, ['话题', '数量'])}
    )
    
    # 3. 保存并推送
    with open(f'reports/daily_{date}.md', 'w') as f:
        f.write(report)
    
    return report
```

---

## 样式指南

| 元素 | 建议 |
|------|------|
| 标题 | # 一级标题，## 二级标题 |
| 列表 | 使用 - 或 *，嵌套不超过 2 层 |
| 表格 | 始终包含表头分隔线 |
| 代码 | 使用 ``` 包裹，标注语言 |
| 强调 | **粗体** 关键数据，*斜体* 次要信息 |
| Emoji | 适度使用 📊📰🔔 等图标 |
| 链接 | [文字](URL) 格式 |

---

## 与通知渠道集成

```python
from mcp_trendradar_send_notification import send_notification

def send_daily_report():
    report = daily_report()
    
    # 发送到所有配置的通知渠道
    send_notification(
        message=report,
        title="📰 每日趋势报告",
        channels=["telegram", "feishu", "email"]
    )
```

---

## 最佳实践

1. **结构清晰** - 使用多级标题组织内容
2. **数据驱动** - 用具体数字而非模糊描述
3. **可视化** - 适当使用表格和列表
4. **时效性** - 标注数据时间范围
5. **行动建议** - 报告末尾包含明确的建议或预测

---

## 下一步

1. 结合 TrendRadar MCP 生成趋势报告
2. 配置定时 cron 任务自动推送
3. 使用 SQLite skill 存储历史报告数据