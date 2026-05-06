#!/usr/bin/env python3
"""
Session Analytics - 会话分析和使用追踪
为 Self-Improvement 提供数据支持
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

SESSION_FILE = Path.home() / ".hermes/.hermes_history"
ANALYTICS_DIR = Path.home() / ".hermes/logs/analytics"
ANALYTICS_FILE = ANALYTICS_DIR / "session_stats.json"

def parse_session_history() -> dict:
    """解析会话历史，提取统计信息"""
    if not SESSION_FILE.exists():
        return {"total_sessions": 0, "total_turns": 0, "topics": []}
    
    content = SESSION_FILE.read_text()
    
    # 简单统计
    stats = {
        "total_size_bytes": len(content),
        "lines": content.count('\n'),
        "estimated_turns": content.count("human:") + content.count("user:"),
    }
    
    return stats

def get_skill_usage_from_logs() -> dict:
    """从日志中分析技能使用情况"""
    skill_usage = defaultdict(int)
    
    # 检查 skill 目录的访问时间
    skills_dir = Path.home() / ".hermes/skills"
    for skill in skills_dir.iterdir():
        if skill.is_dir():
            # 使用目录修改时间作为最后使用代理
            stat = skill.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            skill_usage[skill.name] = mtime.isoformat()  # 转为字符串
    
    return dict(skill_usage)

def generate_analytics_report() -> dict:
    """生成分析报告"""
    session_stats = parse_session_history()
    skill_usage = get_skill_usage_from_logs()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "session_stats": session_stats,
        "skill_usage": skill_usage,
        "insights": []
    }
    
    # 生成洞察
    if session_stats.get("total_turns", 0) > 100:
        report["insights"].append("活跃用户 - 高频使用会话")
    
    recent_skills = [s for s, m in skill_usage.items() 
                    if (datetime.now() - datetime.fromisoformat(m)).days < 7]
    if recent_skills:
        report["insights"].append(f"本周使用了 {len(recent_skills)} 个技能")
    
    return report

def main():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    
    report = generate_analytics_report()
    
    # 保存报告
    ANALYTICS_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("Hermes Session Analytics")
    print("=" * 40)
    print(f"会话大小: {report['session_stats'].get('total_size_bytes', 0) / 1024:.1f} KB")
    print(f"估计轮次: {report['session_stats'].get('estimated_turns', 0)}")
    print(f"技能使用: {len(report['skill_usage'])} 个")
    print()
    if report["insights"]:
        print("洞察:")
        for insight in report["insights"]:
            print(f"  • {insight}")
    print("=" * 40)
    print(f"✅ 报告已保存: {ANALYTICS_FILE}")

if __name__ == "__main__":
    main()