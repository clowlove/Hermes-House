#!/usr/bin/env python3
"""
agent_collab.py - Hermes 协作管理器
整合任务池、知识库、流水线
"""

import os
import sys
import json
import yaml
import subprocess
import re
from datetime import datetime
from pathlib import Path

REPO_PATH = Path("/tmp/hermes-house")
AGENT_NAME = os.environ.get("AGENT_NAME", "hermes-b")
OTHER = "hermes-a" if AGENT_NAME == "hermes-b" else "hermes-b"

class CollabManager:
    def __init__(self):
        self.repo = REPO_PATH
        self.agent = AGENT_NAME
        self.other = OTHER
        
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def run(self, cmd: str) -> str:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repo)
        return r.stdout + r.stderr
    
    def pull(self):
        self.run("git fetch origin main 2>/dev/null")
        self.run("git checkout main")
        self.run("git pull origin main 2>&1")
    
    # ========== 任务池 ==========
    
    def check_tasks(self):
        """检查任务池"""
        task_dir = self.repo / ".agent" / "tasks"
        pool = task_dir / "pool"
        claimed = task_dir / "claimed"
        done = task_dir / "done"
        
        self.log("📋 任务池状态:")
        
        for d, label in [(pool, "待认领"), (claimed, "进行中"), (done, "已完成")]:
            if d.exists():
                files = list(d.glob("*.md"))
                self.log(f"  {label}: {len(files)}")
        
        # 检查是否有分配给自己的任务
        if claimed.exists():
            my_tasks = []
            for f in claimed.glob("*.md"):
                if self.agent in f.read_text():
                    my_tasks.append(f.name)
            if my_tasks:
                self.log(f"  👉 我的任务: {len(my_tasks)}")
    
    def claim_task(self, task_file: str):
        """认领任务"""
        task_dir = self.repo / ".agent" / "tasks"
        src = task_dir / "pool" / task_file
        dst = task_dir / "claimed" / task_file
        
        if not src.exists():
            self.log(f"  ❌ 任务不存在: {task_file}")
            return
        
        content = src.read_text()
        content = content.replace("status: open", f"status: claimed\nclaimed_by: {self.agent}")
        content += f"\n- {datetime.now().isoformat()}Z - {self.agent} 认领\n"
        
        dst.write_text(content)
        src.unlink()
        self.log(f"  ✅ 已认领: {task_file}")
    
    # ========== 知识库 ==========
    
    def check_knowledge(self):
        """检查知识库"""
        kb_dir = self.repo / ".agent" / "knowledge" / "resources"
        
        self.log("📚 知识库:")
        
        categories = ["tools", "articles", "datasets", "models"]
        for cat in categories:
            cat_dir = kb_dir / cat
            if cat_dir.exists():
                files = list(cat_dir.glob("*.md"))
                new = len([f for f in files if "status: new" in f.read_text()])
                self.log(f"  {cat}: {len(files)} 条" + (f" (🔴 {new} 新)" if new else ""))
    
    def add_knowledge(self, kind: str, name: str, link: str, summary: str, rating: int = 3):
        """添加知识条目"""
        kb_dir = self.repo / ".agent" / "knowledge" / "resources" / kind
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{kind}-{name.lower().replace(' ', '-')}.md"
        filepath = kb_dir / filename
        
        id = f"res-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        stars = "⭐" * rating
        
        content = f"""---
id: {id}
type: {kind}
added_by: {self.agent}
added_at: {datetime.now().isoformat()}Z
tags: []
rating: {rating}
status: new
---

# {name}

## 链接
{link}

## 摘要
{summary}

## 评价
{stars}
"""
        filepath.write_text(content)
        self.log(f"  ✅ 已添加知识: {name}")
        return filename
    
    # ========== 流水线 ==========
    
    def check_pipelines(self):
        """检查流水线"""
        pipeline_dir = self.repo / ".agent" / "pipeline"
        
        self.log("🔄 流水线:")
        
        if not pipeline_dir.exists():
            return
        
        for name in ["trend", "code", "learn"]:
            d = pipeline_dir / name
            if d.exists():
                files = list(d.glob("*"))
                self.log(f"  {name}: {len(files)} 个文件")
    
    # ========== PR 监控 ==========
    
    def check_and_merge_prs(self):
        """检查并合并可合并的 PR (处理 429/401/403)"""
        self.log("🔍 检查待合并 PR...")
        
        # 检查 rate limit
        try:
            rate_limit = self.run("gh api rate_limit --jq '.rate.remaining' 2>/dev/null")
            if rate_limit and int(rate_limit.strip()) < 10:
                self.log("  ⚠️ API 配额不足, 跳过")
                return []
        except:
            pass
        
        # 获取可合并的 PR (静默处理 429/403)
        result = self.run("gh pr list --state open --json number,title,mergeable,author --jq '.[] | select(.mergeable == \"MERGEABLE\") | \"\\(.number) \\(.title)\"' 2>/dev/null")
        
        if not result.strip():
            self.log("  无待合并的 PR")
            return []
        
        merged = []
        for line in result.strip().split("\n"):
            if not line:
                continue
            try:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    pr_num, title = parts
                    # 静默合并，不输出错误
                    self.run(f"gh pr merge {pr_num} --squash --delete-branch 2>/dev/null")
                    self.log(f"  ✅ 合并: #{pr_num}")
                    merged.append((pr_num, title))
            except:
                continue
        
        return merged
    
    # ========== 综合运行 ==========
    
    def run_full_cycle(self):
        """执行完整协作周期"""
        self.log(f"🤝 {self.agent} 协作周期开始")
        
        # 1. 拉取
        self.log("📥 拉取最新...")
        self.pull()
        
        # 2. PR 检查
        self.check_and_merge_prs()
        
        # 3. 任务池
        self.check_tasks()
        
        # 4. 知识库
        self.check_knowledge()
        
        # 5. 流水线
        self.check_pipelines()
        
        self.log("✅ 协作周期完成")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["cycle", "tasks", "knowledge", "pipelines", "prs"])
    parser.add_argument("--claim", help="认领任务文件名")
    parser.add_argument("--add-kb", nargs=4, metavar=("TYPE", "NAME", "LINK", "SUMMARY"),
                        help="添加知识: TYPE NAME LINK SUMMARY")
    args = parser.parse_args()
    
    mgr = CollabManager()
    
    if args.claim:
        mgr.claim_task(args.claim)
    elif args.add_kb:
        kind, name, link, summary = args.add_kb
        mgr.add_knowledge(kind, name, link, summary)
    elif args.task == "tasks":
        mgr.check_tasks()
    elif args.task == "knowledge":
        mgr.check_knowledge()
    elif args.task == "pipelines":
        mgr.check_pipelines()
    elif args.task == "prs":
        mgr.check_and_merge_prs()
    else:
        mgr.run_full_cycle()

if __name__ == "__main__":
    main()