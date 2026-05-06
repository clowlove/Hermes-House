#!/usr/bin/env python3
"""
Hermes Self-Improvement - 课后复习机制
在复杂任务完成后，主动询问是否保存经验为技能
"""

import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path.home() / ".hermes/memories/MEMORY.md"
SKILLS_DIR = Path.home() / ".hermes/skills"
SKILL_TEMPLATE = """---
name: {name}
description: {description}
---

# {name}

{content}

## 使用场景

{usages}

## 注意事项

{notes}
"""

def check_complex_task_completed() -> bool:
    """检查是否有复杂的任务完成，可以从中学习"""
    # 检查最近的对话历史，寻找复杂任务模式
    history_file = Path.home() / ".hermes/.hermes_history"
    if not history_file.exists():
        return False
    
    content = history_file.read_text()
    # 简单启发：超过一定长度或包含特定关键词
    return len(content) > 5000 or any(kw in content.lower() for kw in [
        "解决了", "完成了", "成功", "debug", "修复了", "implement", "created"
    ])

def suggest_skill_creation(context: str = "") -> str:
    """生成技能创建建议"""
    suggestion = f"""## 💡 自我进化建议

基于你刚才的工作，我发现了一些值得保存的经验！

### 建议创建技能

**技能名称**: (请描述这个技能解决的问题类型)

**使用场景**: 
- 什么时候应该用这个技能？
- 它解决了什么痛点？

**核心逻辑**:
- 这个技能应该包含什么步骤？
- 有什么陷阱需要避免？

### 如何保存

告诉 Hermes:
```
将以上经验保存为技能: [技能名称]
```

或者让 Hermes 自动分析并创建。

---
_由 Hermes Self-Improvement 于 {datetime.now().strftime('%Y-%m-%d %H:%M')} 生成_
"""
    return suggestion

def auto_extract_patterns() -> list:
    """自动从历史中提取可复用的模式"""
    patterns = []
    # TODO: 实现模式提取逻辑
    return patterns

def main():
    print("Hermes Self-Improvement Check")
    print("=" * 40)
    
    if check_complex_task_completed():
        print("✅ 检测到复杂任务完成")
        print("\n" + suggest_skill_creation())
    else:
        print("ℹ️  本次会话较简单，无需创建技能")

if __name__ == "__main__":
    main()