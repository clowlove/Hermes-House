#!/usr/bin/env python3
"""
Hermès Journal - AI Growth Logger
自动记录 Hermès Agent 的成长历程

Usage:
    python hermes_journal.py --add "完成新功能开发"
    python hermes_journal.py --milestone "获得第一个赞助者"
    python hermes_journal.py --stats
    python hermes_journal.py --render
"""

import argparse
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

JOURNAL_FILE = Path(__file__).parent.parent / "hermes-journal.md"
GIT_LOG_FILE = Path(__file__).parent.parent / "memory" / "git_commits.json"

def get_days_since_start():
    """计算从项目开始到现在的时间"""
    start_date = datetime(2026, 4, 28)
    delta = datetime.now() - start_date
    return delta.days

def get_git_stats():
    """获取 Git 统计信息"""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=7 days ago"],
            capture_output=True,
            text=True,
            cwd=JOURNAL_FILE.parent
        )
        commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            cwd=JOURNAL_FILE.parent
        )
        total_commits = int(result.stdout.strip()) if result.stdout.strip() else 0
        
        return commits, total_commits
    except:
        return 0, 0

def get_skills_count():
    """统计技能数量"""
    skills_dir = Path(__file__).parent.parent / "skills"
    if skills_dir.exists():
        return len(list(skills_dir.rglob("SKILL.md")))
    return 0

def format_section(title, content):
    """格式化新的日志章节"""
    today = datetime.now().strftime("%Y-%m-%d")
    days = get_days_since_start()
    
    section = f"""
## 📅 {today} | 第 {days} 天 - {title}

### 🎯 今日成就

{content}

### 📊 快速统计

| 指标 | 数值 |
|------|------|
| 项目天数 | {days} |
| 技能数量 | {get_skills_count()} |
| Git 提交(7天) | {get_git_stats()[0]} |
| Git 提交(总) | {get_git_stats()[1]} |

---
"""
    return section

def add_entry(title, content, commit=False):
    """添加新的日志条目"""
    section = format_section(title, content)
    
    # 读取现有内容
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 "---" 分隔符，在其前插入新内容
    marker = "\n---\n\n*本日志由"
    if marker in content:
        parts = content.split(marker)
        new_content = parts[0] + section + "---\n" + marker + parts[1]
    else:
        new_content = section + "\n---\n" + content
    
    # 写入
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 日志已更新: {title}")
    
    # Git 提交
    if commit:
        try:
            subprocess.run(["git", "add", "hermes-journal.md"], check=True, cwd=JOURNAL_FILE.parent)
            subprocess.run(
                ["git", "commit", "-m", f"📝 Journal: {title}"],
                check=True,
                cwd=JOURNAL_FILE.parent
            )
            subprocess.run(["git", "push"], check=True, cwd=JOURNAL_FILE.parent)
            print("✅ 已提交到 Git")
        except Exception as e:
            print(f"⚠️ Git 提交失败: {e}")

def add_milestone(milestone):
    """添加里程碑记录"""
    today = datetime.now().strftime("%Y-%m-%d")
    days = get_days_since_start()
    
    entry = f"- [ ] **{today}** - {milestone} ✨"
    
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到待记录列表
    if "- [ ] *" in content:
        content = content.replace("- [ ] *", entry + "\n- [ ] *", 1)
    else:
        content = content.replace("# 📌 待记录", f"# 📌 待记录\n{entry}")
    
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 里程碑已记录: {milestone}")

def render_stats():
    """渲染统计信息"""
    skills = get_skills_count()
    commits_7d, total_commits = get_git_stats()
    days = get_days_since_start()
    
    print(f"""
╔══════════════════════════════════════╗
║     🧩 Hermès Agent 统计面板          ║
╠══════════════════════════════════════╣
║  📅 运行天数: {days:>3} 天                  ║
║  🛠️  技能数量: {skills:>3} 个                ║
║  📝 Git 提交(7天): {commits_7d:>3}              ║
║  📝 Git 提交(总): {total_commits:>3}              ║
╚══════════════════════════════════════╝
""")

def main():
    parser = argparse.ArgumentParser(description="Hermès Journal - AI 成长日志")
    parser.add_argument("--add", nargs=2, metavar=("标题", "内容"), 
                        help="添加新日志条目")
    parser.add_argument("--milestone", type=str, help="添加里程碑")
    parser.add_argument("--stats", action="store_true", help="显示统计")
    parser.add_argument("--commit", action="store_true", default=True, help="自动提交到 Git")
    
    args = parser.parse_args()
    
    if args.stats:
        render_stats()
    elif args.milestone:
        add_milestone(args.milestone)
        if args.commit:
            try:
                subprocess.run(["git", "add", "hermes-journal.md"], check=True, cwd=JOURNAL_FILE.parent)
                subprocess.run(
                    ["git", "commit", "-m", f"🏆 Milestone: {args.milestone}"],
                    check=True,
                    cwd=JOURNAL_FILE.parent
                )
                subprocess.run(["git", "push"], check=True, cwd=JOURNAL_FILE.parent)
            except Exception as e:
                print(f"⚠️ Git 操作失败: {e}")
    elif args.add:
        title, content = args.add
        add_entry(title, content, commit=args.commit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()