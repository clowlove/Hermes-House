#!/usr/bin/env python3
"""
pipeline_runner.py - Hermes 间自动化流水线执行器
"""

import os
import json
import yaml
import subprocess
from datetime import datetime
from pathlib import Path

REPO_PATH = Path("/tmp/hermes-house")
PIPELINE_DIR = REPO_PATH / ".agent" / "pipeline"
CONFIG_FILE = PIPELINE_DIR / "config.yaml"
AGENT_NAME = os.environ.get("AGENT_NAME", "hermes-b")

class PipelineRunner:
    def __init__(self):
        self.config = self.load_config()
        self.agent = AGENT_NAME
        
    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return yaml.safe_load(f)
        return {}
    
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def run(self, cmd: str) -> str:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.stdout + result.stderr
    
    def get_pipeline_dir(self, name: str) -> Path:
        d = PIPELINE_DIR / name
        d.mkdir(parents=True, exist_ok=True)
        return d
    
    def check_triggers(self):
        """检查可执行的流水线"""
        self.log(f"🔍 检查 {self.agent} 相关的流水线...")
        
        triggered = []
        for name, cfg in self.config.get("pipelines", {}).items():
            producers = cfg.get("producers", [])
            consumers = cfg.get("consumers", [])
            
            # 检查是否应该由我生产或消费
            if self.agent in producers or self.agent in consumers:
                triggered.append((name, cfg))
        
        return triggered
    
    def check_pending_work(self, pipeline_name: str, cfg: dict):
        """检查是否有待处理的工作"""
        dir = self.get_pipeline_dir(pipeline_name)
        consumers = cfg.get("consumers", [])
        
        # 如果我是消费者，检查是否有待处理的数据
        if self.agent in consumers:
            stages = cfg.get("stages", {})
            for stage_name in stages.keys():
                pending_files = list(dir.glob(f"*{stage_name}*.json"))
                if pending_files:
                    self.log(f"  📋 {pipeline_name}/{stage_name}: {len(pending_files)} 个待处理")
                    return pending_files
        return []
    
    def run_cycle(self):
        """执行流水线检查"""
        self.log(f"🔄 流水线检查开始 ({self.agent})")
        
        pipelines = self.check_triggers()
        if not pipelines:
            self.log("  无相关流水线")
            return
        
        for name, cfg in pipelines:
            pending = self.check_pending_work(name, cfg)
            if pending:
                self.log(f"  ✅ {name}: 有 {len(pending)} 个待处理任务")
            else:
                self.log(f"  ○ {name}: 无待处理")
        
        self.log("✅ 流水线检查完成")

def main():
    runner = PipelineRunner()
    runner.run_cycle()

if __name__ == "__main__":
    main()