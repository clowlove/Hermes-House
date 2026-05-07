---
name: matplotlib-charts
description: 使用 matplotlib 生成图表 - 趋势图、柱状图、饼图、热力图等。导出 PNG/SVG/PDF，用于报告和可视化。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3]
  python_libs: [matplotlib, pandas, numpy]
  api_keys: []
metadata:
  hermes:
    tags: [chart, matplotlib, visualization, plot, data-viz]
    homepage: https://github.com/hermes-agent
---

# Matplotlib 图表生成

生成各类数据图表，用于报告和可视化。支持 PNG/SVG/PDF 格式输出。

---

## 基础设置

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 无头模式，不显示窗口

# 中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表大小
plt.figure(figsize=(12, 6))
```

---

## 常用图表

### 1. 趋势折线图

```python
import matplotlib.pyplot as plt
import pandas as pd

def plot_trend(dates, values, title, ylabel, output_path):
    """趋势折线图"""
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, marker='o', linewidth=2, markersize=6)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12)
    plt.xlabel('日期', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
dates = ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']
values = [100, 120, 115, 140, 135]
plot_trend(dates, values, 'AI 话题热度趋势', '讨论量', 'trend.png')
```

### 2. 柱状图

```python
def plot_bar(categories, values, title, ylabel, output_path, horizontal=False):
    """柱状图"""
    plt.figure(figsize=(10, 6))
    
    colors = plt.cm.Blues([(i+1)/len(categories)*0.8 + 0.2 for i in range(len(categories))])
    
    if horizontal:
        bars = plt.barh(categories, values, color=colors)
        plt.xlabel(ylabel, fontsize=12)
        plt.ylabel('')
    else:
        bars = plt.bar(categories, values, color=colors)
        plt.ylabel(ylabel, fontsize=12)
        plt.xticks(rotation=45, ha='right')
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.grid(axis='both', alpha=0.3)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
platforms = ['微博', '知乎', 'Twitter', 'B站', '微信公众号']
counts = [150, 120, 90, 75, 45]
plot_bar(platforms, counts, '平台分布', '文章数量', 'platform_bar.png')
```

### 3. 饼图

```python
def plot_pie(labels, values, title, output_path):
    """饼图"""
    plt.figure(figsize=(10, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    explode = [0.05] * len(labels)  # 分离效果
    
    plt.pie(values, labels=labels, colors=colors, explode=explode,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('equal')  # 正圆
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
labels = ['正面', '中性', '负面']
sizes = [65, 25, 10]
plot_pie(labels, sizes, '情感分布', 'sentiment_pie.png')
```

### 4. 多系列折线图

```python
def plot_multi_line(dates, series_dict, title, ylabel, output_path):
    """多系列折线图"""
    plt.figure(figsize=(14, 7))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
    markers = ['o', 's', '^', 'D', 'v']
    
    for i, (series_name, values) in enumerate(series_dict.items()):
        plt.plot(dates, values, label=series_name, 
                color=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                linewidth=2, markersize=6)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12)
    plt.xlabel('日期', fontsize=12)
    plt.legend(loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
dates = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
series = {
    'AI话题': [120, 135, 142, 138, 155, 180, 165],
    '科技话题': [85, 92, 88, 95, 90, 78, 82]
}
plot_multi_line(dates, series, '话题热度对比', '讨论量', 'comparison.png')
```

### 5. 热力图

```python
import numpy as np

def plot_heatmap(data, labels_x, labels_y, title, output_path, cmap='YlOrRd'):
    """热力图"""
    plt.figure(figsize=(12, 8))
    
    # 归一化数据
    data_normalized = np.array(data, dtype=float)
    data_normalized = (data_normalized - data_normalized.min()) / (data_normalized.max() - data_normalized.min() + 1e-10)
    
    im = plt.imshow(data_normalized, cmap=cmap, aspect='auto')
    
    # 设置刻度
    plt.xticks(range(len(labels_x)), labels_x, rotation=45, ha='right')
    plt.yticks(range(len(labels_y)), labels_y)
    
    # 添加数值标签
    for i in range(len(labels_y)):
        for j in range(len(labels_x)):
            text = plt.text(j, i, f'{data[i][j]:.0f}',
                          ha='center', va='center', color='black', fontsize=9)
    
    plt.colorbar(im, label='强度')
    plt.title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
hours = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
# 生成示例数据
data = np.random.randint(10, 100, (7, 6))
plot_heatmap(data, hours, days, '活跃时段热力图', 'heatmap.png')
```

---

## 样式主题

### 暗色主题（适合深色背景）

```python
def dark_style():
    plt.style.use('dark_background')
    plt.rcParams['figure.facecolor'] = '#1a1a2e'
    plt.rcParams['axes.facecolor'] = '#16213e'
    plt.rcParams['axes.edgecolor'] = '#0f3460'
    plt.rcParams['text.color'] = '#e8e8e8'
    plt.rcParams['axes.labelcolor'] = '#e8e8e8'
    plt.rcParams['xtick.color'] = '#e8e8e8'
    plt.rcParams['ytick.color'] = '#e8e8e8'
    plt.rcParams['grid.color'] = '#0f3460'
```

### 简洁主题

```python
def minimal_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 11
```

---

## Pandas 集成

```python
import pandas as pd

def plot_from_dataframe(df, x_col, y_cols, title, output_path, kind='line'):
    """从 DataFrame 绘图"""
    plt.figure(figsize=(12, 6))
    
    df.plot(x=x_col, y=y_cols, kind=kind, figsize=(12, 6), 
            title=title, grid=True, alpha=0.8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path

# 使用示例
df = pd.DataFrame({
    '日期': pd.date_range('2025-01-01', periods=30),
    'AI话题': np.random.randint(50, 200, 30),
    '科技话题': np.random.randint(30, 150, 30)
})
plot_from_dataframe(df, '日期', ['AI话题', '科技话题'], '话题趋势', 'trend_df.png')
```

---

## 与报告集成

```python
from report_generation import generate_markdown_report

def create_data_report(data_dict, output_dir='/tmp/reports'):
    """生成带图表的数据报告"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    charts = {}
    
    # 生成各类型图表
    if 'platform_counts' in data_dict:
        path = f'{output_dir}/platform.png'
        plot_bar(list(data_dict['platform_counts'].keys()),
                list(data_dict['platform_counts'].values()),
                '平台分布', '数量', path)
        charts['platform'] = path
    
    if 'sentiment' in data_dict:
        path = f'{output_dir}/sentiment.png'
        plot_pie(['正面', '中性', '负面'], 
                data_dict['sentiment'], '情感分析', path)
        charts['sentiment'] = path
    
    return charts
```

---

## 输出格式

| 格式 | 用途 | 设置 |
|------|------|------|
| PNG | 一般展示 | `dpi=150` |
| SVG | 矢量图，可编辑 | `format='svg'` |
| PDF | 打印/出版 | `format='pdf'` |
| 300 dpi | 高清印刷 | `dpi=300` |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中文乱码 | 使用英文标签，或安装中文字体 |
| 负号显示 | `plt.rcParams['axes.unicode_minus'] = False` |
| 图例遮挡 | `plt.legend(loc='best')` |
| 标签重叠 | `plt.xticks(rotation=45)` |
| 图例太多 | 放在图表右侧或下方 |

---

## 下一步

1. 结合 SQLite skill 读取历史数据
2. 结合 report-generation skill 生成可视化报告
3. 在 cron 任务中自动生成图表