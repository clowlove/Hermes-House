---
name: cli-utilities
description: 实用 CLI 工具集 - HTTP 请求、JSON 处理、日期计算、文件转换等常用命令。快速执行，无需 Python 脚本。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl, jq, date, python3]
  api_keys: []
metadata:
  hermes:
    tags: [cli, curl, jq, json, http, utilities]
    homepage: https://github.com/hermes-agent
---

# CLI 工具集

实用的命令行工具，快速执行常用操作。无需编写 Python 脚本即可完成。

---

## HTTP 请求

### curl 基础

```bash
# GET 请求
curl https://api.example.com/data

# GET 并格式化 JSON 输出
curl -s https://api.example.com/data | jq .

# GET 带 Header
curl -s -H "Authorization: Bearer TOKEN" https://api.example.com/data

# POST JSON
curl -s -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# 带超时
curl -s --max-time 10 https://api.example.com/data
```

### 实用 curl 模式

```bash
# 下载文件
curl -L -o output.pdf https://example.com/file.pdf

# 带查询参数
curl -s "https://api.example.com/search?q=keyword&page=1"

# 验证 HTTP 状态码
curl -s -o /dev/null -w "%{http_code}" https://api.example.com

# 下载并显示进度
curl -L -# -o output.zip https://example.com/file.zip
```

---

## JSON 处理

### jq 基础

```bash
# 格式化输出
echo '{"a":1,"b":2}' | jq .

# 提取字段
cat data.json | jq '.name'
cat data.json | jq '.[0].title'

# 数组操作
cat data.json | jq '.[].name'           # 提取所有 name
cat data.json | jq 'map(select(.age > 18))'  # 过滤
cat data.json | jq 'map(.price * .quantity)'  # 计算

# 聚合
cat data.json | jq 'map(.value) | add'  # 求和
cat data.json | jq 'map(.value) | length'  # 计数

# 组合
cat data.json | jq '[.[] | select(.status == "active")]'

# 重命名字段
cat data.json | jq 'map({id, name: .title})'
```

### 高级 jq

```bash
# 分组
cat data.json | jq 'group_by(.category)'

# 唯一值
cat data.json | jq '[.[].category] | unique'

# 条件判断
cat data.json | jq 'map(if .value > 100 then . else empty end)'

# 合并对象
echo '{"a":1}' | jq -s '.[0] * .[1]'

# 日期转换
date -u +%Y-%m-%dT%H:%M:%SZ | jq -sR '{timestamp: .}'
```

---

## 日期时间

```bash
# 当前日期时间
date                        # Thu Jan 16 10:30:00 CST 2025
date +"%Y-%m-%d"            # 2025-01-16
date +"%Y-%m-%d %H:%M:%S"   # 2025-01-16 10:30:00
date -u +"%Y-%m-%dT%H:%M:%SZ"  # ISO 格式

# 昨天/明天
date -d "yesterday" +"%Y-%m-%d"
date -d "tomorrow" +"%Y-%m-%d"
date -d "1 week ago" +"%Y-%m-%d"
date -d "30 days ago" +"%Y-%m-%d"

# 下个月
date -d "next month" +"%Y-%m-%d"

# 时间戳
date +%s                    # 当前时间戳
date -d "2025-01-01" +%s    # 指定日期时间戳
date -d @1704067200 +"%Y-%m-%d"  # 时间戳转日期

# 计算日期间隔
echo $(( ($(date -d "2025-01-15" +%s) - $(date -d "2025-01-01" +%s) ) / 86400 ))  # 天数差
```

---

## 文件处理

```bash
# 文件信息
wc -l file.txt              # 行数
wc -w file.txt              # 词数
stat file.txt               # 详细信息
file file.txt               # 文件类型

# 查找
find . -name "*.json" -type f
find . -mtime -7 -type f    # 7天内修改的文件
find . -size +100M          # >100MB 的文件

# 内容搜索
grep -r "pattern" .          # 递归搜索
grep -l "pattern" *.txt     # 只显示文件名
grep -c "pattern" file.txt  # 计数

# 批量重命名
rename 's/\.txt\.bak$/\.txt/' *.txt.bak

# 文件对比
diff file1.txt file2.txt
diff -u file1.txt file2.txt | head -20
```

---

## 文本处理

```bash
# 排序去重
sort file.txt | uniq -c | sort -rn  # 统计重复行
sort -t',' -k2 -n file.csv  # 按第二列数字排序

# 列提取
cut -d',' -f1,3 file.csv    # 提取第1、3列
awk -F',' '{print $1, $3}' file.csv

# 文本替换
sed 's/old/new/g' file.txt
sed -i 's/old/new/g' file.txt  # 直接修改文件

# 格式化输出
column -t -s',' file.csv    # 表格对齐
pr -t -2 file.txt           # 双栏排版
```

---

## 网络诊断

```bash
# 检查端口连通性
nc -zv host 80
nc -zv host 443

# DNS 查询
dig example.com
nslookup example.com
host example.com

# 路由追踪
traceroute example.com
tracert example.com  # Windows

# 带宽测试
curl -o /dev/null -s -w "%{speed_download}" https://example.com/file

# WHOIS 查询
whois example.com
```

---

## 系统监控

```bash
# 资源使用
df -h                       # 磁盘空间
du -sh *                    # 目录大小
free -h                     # 内存
top -bn1 | head -20         # CPU 进程

# 快速监控
watch -n 1 'command'        # 每秒执行

# 查找大文件
find . -type f -size +100M -exec ls -lh {} \;
```

---

## 管道组合示例

```bash
# API 调用 + JSON 解析 + 统计
curl -s "https://api.example.com/items" | jq '[.[] | select(.active == true)] | length'

# 日志分析：统计 IP 访问量
grep "GET /api" access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 批量下载 + 解压
curl -sL "https://example.com/data.zip" -o /tmp/data.zip && unzip /tmp/data.zip

# 定时任务：每日备份
0 2 * * * tar -czf /backup/$(date +\%Y\%m\%d).tar.gz /data
```

---

## 实用脚本模板

### 批量下载

```bash
#!/bin/bash
# download.sh - 批量下载文件列表
while read url; do
  curl -L -o "$(basename $url)" "$url"
done < urls.txt
```

### API 轮询

```bash
#!/bin/bash
# poll.sh - 定时请求直到满足条件
while true; do
  result=$(curl -s "https://api.example.com/status")
  if echo "$result" | jq -e '.ready == true' > /dev/null; then
    echo "$result"
    break
  fi
  sleep 5
done
```

---

## 跨平台注意

| 命令 | Linux | macOS | Windows |
|------|-------|-------|---------|
| curl | ✅ | ✅ | ⚠️ 需 WSL |
| jq | ✅ | ✅ | ⚠️ 需 WSL |
| date | ✅ | ✅ | ⚠️ 需 Git Bash |
| sed | ✅ | ✅ | ⚠️ 需 WSL |
| grep | ✅ | ✅ | ⚠️ 需 WSL |

Windows 建议使用 [Git Bash](https://gitforwindows.org/) 或 WSL。

---

## 下一步

1. 将常用命令加入 alias：`alias json="jq ."`
2. 创建脚本模板库快速复用
3. 结合 cron 实现自动化任务