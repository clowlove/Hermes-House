#!/usr/bin/env python3
"""
Hermes Skill Validator
验证技能目录格式是否正确
"""

import os
import json
import sys
from pathlib import Path

def validate_skill(skill_path: Path) -> tuple[bool, list]:
    """验证单个技能"""
    errors = []
    
    # 检查必需文件
    required_files = ['SKILL.md', 'skill.json']
    for f in required_files:
        if not (skill_path / f).exists():
            errors.append(f"缺少必需文件: {f}")
    
    if errors:
        return False, errors
    
    # 验证 skill.json
    try:
        with open(skill_path / 'skill.json') as f:
            data = json.load(f)
        
        required_fields = ['name', 'version', 'description']
        for field in required_fields:
            if field not in data:
                errors.append(f"skill.json 缺少字段: {field}")
        
        if 'hermes' not in data:
            errors.append("skill.json 缺少 hermes 配置")
        elif 'skill_category' not in data['hermes']:
            errors.append("skill.json 缺少 hermes.skill_category")
            
    except json.JSONDecodeError as e:
        errors.append(f"skill.json 格式错误: {e}")
    
    return len(errors) == 0, errors

def main():
    skills_dir = Path(__file__).parent.parent / 'skills'
    
    if not skills_dir.exists():
        print("❌ skills 目录不存在")
        sys.exit(1)
    
    print("🔍 验证技能...")
    print()
    
    all_valid = True
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir():
            valid, errors = validate_skill(skill_dir)
            if valid:
                print(f"✅ {skill_dir.name}")
            else:
                print(f"❌ {skill_dir.name}")
                for err in errors:
                    print(f"   - {err}")
                all_valid = False
    
    print()
    if all_valid:
        print("🎉 所有技能验证通过！")
        sys.exit(0)
    else:
        print("⚠️ 部分技能存在问题")
        sys.exit(1)

if __name__ == '__main__':
    main()