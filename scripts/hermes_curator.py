#!/usr/bin/env python3
"""
Hermes Curator - 自动整理技能库
基于使用频率、质量评分自动整理、合并、删除技能
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path.home() / ".hermes/skills"
CURATOR_LOG = Path.home() / ".hermes/logs/curator"
CURATOR_REPORT = CURATOR_LOG / "run.json"
RETENTION_DAYS = 30  # 超过30天未使用的技能标记为待删除

def run(cmd: str) -> Tuple[bool, str, str]:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def get_skill_metadata(skill_path: Path) -> Dict:
    """读取技能的 skill.json 元数据"""
    meta_file = skill_path / "skill.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text())
    return {}

def get_skill_usage(skill_path: Path) -> Dict:
    """估算技能使用情况"""
    # 检查最后修改时间（反映最近使用）
    stat = skill_path.stat()
    last_modified = datetime.fromtimestamp(stat.st_mtime)
    days_since_modified = (datetime.now() - last_modified).days
    
    # 检查技能内容行数
    skill_md = skill_path / "SKILL.md"
    lines = skill_md.read_text().count('\n') if skill_md.exists() else 0
    
    return {
        "last_used_days_ago": days_since_modified,
        "lines": lines,
        "name": skill_path.name
    }

def grade_skills() -> List[Dict]:
    """评分所有技能"""
    skills = []

    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        # 跳过特殊目录
        if skill_dir.name.startswith('.') or skill_dir.name == 'node_modules':
            continue
        
        usage = get_skill_usage(skill_dir)
        meta = get_skill_metadata(skill_dir)
        
        # 计算分数
        score = 100
        score -= min(usage["last_used_days_ago"], 30)  # 最多扣30分
        score -= max(0, 50 - usage["lines"]) // 10  # 内容太少扣分
        
        # 检查是否是内置/重要技能
        if meta.get("bundled") or meta.get("important"):
            score += 20
        
        # 检查名称是否有特殊标记
        if skill_dir.name.startswith(("system-", "core-", "hermes-")):
            score += 15
        
        skills.append({
            "name": skill_dir.name,
            "path": str(skill_dir),
            "score": max(0, score),
            "last_used_days_ago": usage["last_used_days_ago"],
            "lines": usage["lines"],
            "meta": meta
        })
    
    # 按分数排序
    skills.sort(key=lambda x: x["score"], reverse=True)
    return skills

def generate_report(skills: List[Dict], action: str = "graded") -> Dict:
    """生成 curator 报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_skills": len(skills),
        "action": action,
        "skills_by_score": {
            "top": [s["name"] for s in skills[:5]],
            "bottom": [s["name"] for s in skills[-5:]] if len(skills) > 5 else []
        },
        "details": []
    }
    
    for s in skills:
        report["details"].append({
            "name": s["name"],
            "score": s["score"],
            "last_used_days_ago": s["last_used_days_ago"],
            "recommendation": "keep" if s["score"] > 50 else "review" if s["score"] > 20 else "prune"
        })
    
    return report

def print_curator_report(skills: List[Dict], report: Dict):
    """打印美化报告"""
    print("═══════════════════════════════════════════════")
    print("       Hermes Curator — 技能库整理报告")
    print("═══════════════════════════════════════════════")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 技能总数: {len(skills)}")
    print()
    
    print("🏆 TOP 5 技能 (高分)")
    print("-" * 40)
    for i, s in enumerate(skills[:5], 1):
        print(f"  {i}. {s['name']:<30} Score: {s['score']}")
    
    print()
    print("⚠️  待审核 (低分)")
    print("-" * 40)
    for s in skills[-5:]:
        status = "🗑️ 建议删除" if s["score"] < 20 else "📝 建议优化"
        print(f"  • {s['name']:<28} Score: {s['score']:>3}  {status}")
    
    print()
    print("📈 分布统计")
    print("-" * 40)
    high = len([s for s in skills if s["score"] >= 70])
    mid = len([s for s in skills if 30 <= s["score"] < 70])
    low = len([s for s in skills if s["score"] < 30])
    print(f"  高分 (≥70): {high} 个")
    print(f"  中分 (30-69): {mid} 个")
    print(f"  低分 (<30): {low} 个")
    
    print()
    print("💡 操作建议")
    print("-" * 40)
    prune_candidates = [s for s in skills if s["score"] < 20 and s["last_used_days_ago"] > RETENTION_DAYS]
    if prune_candidates:
        print(f"  🗑️  可删除 {len(prune_candidates)} 个长期未使用的技能:")
        for s in prune_candidates[:5]:
            print(f"     - {s['name']} (未使用 {s['last_used_days_ago']} 天)")
    else:
        print("  ✅ 技能库健康，无需删除")
    
    print("═══════════════════════════════════════════════")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Hermes Curator 启动...")
    
    # 确保目录存在
    CURATOR_LOG.mkdir(parents=True, exist_ok=True)
    
    # 评分技能
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 分析技能库...")
    skills = grade_skills()
    report = generate_report(skills)
    
    # 保存报告
    CURATOR_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 生成 Markdown 报告
    report_md = f"""# Curator 运行报告

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

- 技能总数: {len(skills)}
- 高分技能: {len([s for s in skills if s['score'] >= 70])}
- 待优化: {len([s for s in skills if 20 <= s['score'] < 70])}
- 建议删除: {len([s for s in skills if s['score'] < 20])}

## TOP 5 技能

| 排名 | 技能 | 评分 | 最后使用 |
|------|------|------|----------|
"""
    for i, s in enumerate(skills[:5], 1):
        report_md += f"| {i} | {s['name']} | {s['score']} | {s['last_used_days_ago']}天前 |\n"
    
    report_md += f"""
## 待审核技能

| 技能 | 评分 | 最后使用 | 建议 |
|------|------|----------|------|
"""
    for s in skills[-10:]:
        report_md += f"| {s['name']} | {s['score']} | {s['last_used_days_ago']}天前 | {'删除' if s['score'] < 20 else '优化'} |\n"
    
    (CURATOR_LOG / "REPORT.md").write_text(report_md)
    
    # 打印报告
    print_curator_report(skills, report)
    
    print(f"\n✅ 报告已保存: {CURATOR_REPORT}")
    print(f"✅ Markdown 报告: {CURATOR_LOG / 'REPORT.md'}")

if __name__ == "__main__":
    main()