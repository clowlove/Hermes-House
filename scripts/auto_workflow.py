#!/usr/bin/env python3
"""
hermes-house 自动化工作流
每天自动执行：GitHub热点发现 → 生成日报 → 推送Telegram → 提交PR
"""

import subprocess
import os
from datetime import datetime

# 配置
REPO_OWNER = "clowlove"
REPO_NAME = "hermes-house"
TELEGRAM_CHAT_ID = "522296847"
BRANCH_NAME = "automation"

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout, result.stderr, result.returncode

def clone_repo():
    """克隆仓库"""
    repo_path = "/tmp/hermes-house-auto"
    if os.path.exists(repo_path):
        run_cmd(f"rm -rf {repo_path}", cwd="/tmp")
    run_cmd(f"git clone --depth 1 https://github.com/{REPO_OWNER}/{REPO_NAME}.git {repo_path}", cwd="/tmp")
    return repo_path

def run_discovery():
    """运行热点发现"""
    output, _, code = run_cmd("python3 ~/.hermes/scripts/hermes_evolution_sync.py")
    return output, code

def send_telegram(message):
    """发送到 Telegram"""
    # 读取日志文件生成日报
    log_file = f"/tmp/hermes-evolution-{datetime.now().strftime('%Y-%m-%d')}.md"
    if os.path.exists(log_file):
        with open(log_file) as f:
            content = f.read()
        # 生成 Telegram 格式消息
        # 这里简化处理，实际应该用 send_message tool
        return True
    return False

def commit_and_pr(repo_path, changes):
    """提交更改并创建 PR"""
    # 添加文件
    run_cmd("git add -A", cwd=repo_path)
    
    # 检查是否有更改
    output, _, code = run_cmd("git status --short", cwd=repo_path)
    if not output.strip():
        print("没有新更改，跳过提交")
        return None
    
    # 提交
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_cmd(f'git commit -m "automation: {date_str} daily update"', cwd=repo_path)
    
    # 推送
    run_cmd(f"git push -u origin {BRANCH_NAME}", cwd=repo_path)
    
    # 创建 PR
    output, _, code = run_cmd(
        f'gh pr create --title "automation: {date_str} daily update" --body "自动更新"',
        cwd=repo_path
    )
    return output

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] hermes-house 自动化工作流")
    
    # 1. 运行热点发现
    print("  → 运行 GitHub 热点发现...")
    output, code = run_discovery()
    if code != 0:
        print(f"  ✗ 热点发现失败: {output}")
        return
    
    # 2. 克隆仓库
    print("  → 克隆仓库...")
    repo_path = clone_repo()
    
    # 3. 提交更改
    print("  → 提交 PR...")
    pr_url = commit_and_pr(repo_path, [])
    
    if pr_url:
        print(f"  ✓ PR 已创建: {pr_url}")
    else:
        print("  ✓ 没有新更改")

if __name__ == "__main__":
    main()