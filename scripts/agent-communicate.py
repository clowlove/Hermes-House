#!/usr/bin/env python3
"""
agent-communicate.py - Hermes Agent 间自主通信引擎
自动检查、处理、回复消息
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置
REPO_PATH = Path("/tmp/hermes-house")
AGENT_NAME = os.environ.get("AGENT_NAME", "hermes-b")  # hermes-a 或 hermes-b
INBOX = REPO_PATH / "agent-comm/messages/inbox"
OUTBOX = REPO_PATH / "agent-comm/messages/outbox"
CONFIG = REPO_PATH / "agent-comm/config.json"

class AgentCommunicator:
    def __init__(self):
        self.repo = REPO_PATH
        self.agent = AGENT_NAME
        self.other = "hermes-a" if AGENT_NAME == "hermes-b" else "hermes-b"
        
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def run(self, cmd: str) -> str:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repo)
        return result.stdout + result.stderr
    
    def pull(self):
        """拉取最新代码"""
        self.log("📥 拉取最新代码...")
        self.run("git fetch origin main 2>/dev/null")
        self.run("git checkout main")
        output = self.run("git pull origin main 2>&1")
        if "Already up to date" not in output:
            self.log("  代码已更新")
        return self.repo.exists()
    
    def read_config(self) -> dict:
        """读取配置"""
        if CONFIG.exists():
            return json.loads(CONFIG.read_text())
        return {}
    
    def parse_message(self, filepath: Path) -> dict:
        """解析消息文件"""
        content = filepath.read_text(encoding="utf-8")
        msg = {
            "file": filepath.name,
            "from": None,
            "action": None,
            "timestamp": None,
            "title": None,
            "body": content
        }
        
        # 解析文件头
        if "From: " in content:
            match = re.search(r"From:.*?\[From:\s*(\w+)", content)
            if match:
                msg["from"] = match.group(1)
        
        if "类型:" in content or "type:" in content.lower():
            match = re.search(r"类型:\s*(\w+)", content)
            if not match:
                match = re.search(r"type:\s*(\w+)", content, re.I)
            if match:
                msg["action"] = match.group(1).lower()
        
        if "# " in content:
            msg["title"] = content.split("# ")[1].split("\n")[0]
        
        return msg
    
    def check_inbox(self) -> list:
        """检查收件箱新消息"""
        if not INBOX.exists():
            return []
        
        messages = []
        for f in sorted(INBOX.glob("*.md")):
            # 检查是否是我的消息（发给我或广播）
            content = f.read_text(encoding="utf-8")
            if f"To: {self.agent}" in content or "To: ALL" in content or f"[To: {self.agent}]" in content:
                messages.append(self.parse_message(f))
            elif "From:" in content:
                # 检查from字段
                match = re.search(r"From:.*?\[From:\s*(\w+)", content)
                if match and match.group(1) != self.agent:
                    messages.append(self.parse_message(f))
        
        return messages
    
    def handle_message(self, msg: dict) -> Optional[str]:
        """处理消息并生成回复"""
        action = msg.get("action", "")
        title = msg.get("title", "")
        body = msg.get("body", "")
        
        self.log(f"  处理: {msg.get('file')} - {title}")
        
        # 根据类型处理
        if action in ["ping"]:
            return self.create_pong()
        
        elif action in ["task", "info"]:
            return self.create_reply(msg, "收到，已处理")
        
        return None
    
    def create_pong(self) -> str:
        """创建 pong 回复"""
        counter = len(list(OUTBOX.glob("*"))) + 1
        filename = f"pong-{self.agent}-{self.other}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        content = f"""# [From: {self.agent.upper()}] → [To: {self.other.upper()}]

## 时间: {datetime.now().isoformat()}Z

## 类型: pong

---

### 内容

pong! 连接正常，心跳检测通过。

**状态**: 
- ✅ 通信正常
- ✅ 消息处理正常
- ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

---

### 签名

```
{self.agent.upper()}
 hermes-agent v1.0
 Auto-generated pong
```
"""
        filepath = OUTBOX / filename
        filepath.write_text(content, encoding="utf-8")
        return filename
    
    def create_reply(self, original: dict, response: str) -> str:
        """创建回复消息"""
        counter = len(list(OUTBOX.glob("*"))) + 1
        filename = f"reply-{self.agent}-{self.other}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        content = f"""# [From: {self.agent.upper()}] → [To: {self.other.upper()}]

## 时间: {datetime.now().isoformat()}Z

## 类型: reply

---

### 回复内容

{response}

---

### 原文参考

{original.get('file')}: {original.get('title')}

---

### 签名

```
{self.agent.upper()}
 hermes-agent v1.0
```
"""
        filepath = OUTBOX / filename
        filepath.write_text(content, encoding="utf-8")
        return filename
    
    def push_messages(self) -> bool:
        """推送发件箱消息"""
        pending = list(OUTBOX.glob("*.md"))
        if not pending:
            return True
        
        self.log(f"📤 推送 {len(pending)} 条消息...")
        
        branch = f"agent-comm/{self.agent}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 创建分支
        self.run(f"git checkout -b {branch}")
        
        # 添加文件
        self.run(f"git add agent-comm/messages/outbox/*.md")
        
        # 提交
        commit_msg = f"feat(agent): {self.agent} messages {datetime.now().strftime('%Y%m%d')}"
        result = self.run(f"git commit -m '{commit_msg}'")
        
        if "nothing to commit" in result:
            self.run("git checkout main")
            return True
        
        # 推送
        self.run(f"git push -u origin {branch} 2>&1")
        
        # 创建 PR
        pr_result = self.run(f"gh pr create --title 'feat(agent): {self.agent} messages' --body 'Agent 间通信消息' 2>&1")
        
        self.run("git checkout main")
        
        return "pull" in pr_result.lower() or "http" in pr_result
    
    def run_cycle(self):
        """执行一个通信周期"""
        self.log(f"🔄 {self.agent} 通信周期开始")
        
        # 1. 拉取最新
        if not self.pull():
            self.log("  ❌ 仓库不可用")
            return
        
        # 2. 检查收件箱
        messages = self.check_inbox()
        self.log(f"  收件箱: {len(messages)} 条新消息")
        
        # 3. 处理消息
        for msg in messages:
            reply_file = self.handle_message(msg)
            if reply_file:
                self.log(f"  ✅ 创建回复: {reply_file}")
        
        # 4. 推送发件箱
        self.push_messages()
        
        self.log(f"✅ 通信周期完成")

def main():
    comm = AgentCommunicator()
    comm.run_cycle()

if __name__ == "__main__":
    main()