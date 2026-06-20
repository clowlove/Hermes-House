# Parallel Agent Analysis Pattern
# 参考: zubair-trabzada/ai-legal-claude (1.3k stars)
# 设计模式: 1个主agent协调 + N个并行子agent多维度分析

## 核心模式

```python
# 主agent负责任务分解和结果聚合
# 子agent并行执行各自维度分析

ANALYSIS_AGENTS = {
    "risk_agent": "风险维度分析",
    "clause_agent": "条款逐条分析", 
    "missing_agent": "缺失保护分析",
    "compliance_agent": "合规检查",
    "negotiate_agent": "谈判策略"
}

# 并行执行 + 结果聚合
async def parallel_review(document):
    results = await asyncio.gather(
        risk_agent.analyze(document),
        clause_agent.analyze(document),
        missing_agent.analyze(document),
        compliance_agent.analyze(document),
        negotiate_agent.analyze(document)
    )
    return aggregate_results(results)
```

## 适用场景

1. **多维度评估任务** - 需要从不同角度分析同一对象
2. **竞品多维度对比** - 价格/质量/服务/物流 等
3. **客户询盘分析** - 需求/预算/信誉/紧迫度 多维
4. **风险评估** - 市场/汇率/物流/政策 风险

## PDF 报告生成参考

```bash
# 工具链: reportlab / weasyprint / pdfkit
# 流程:
# 1. 生成 HTML 报告模板
# 2. 转换为 PDF
# 3. 添加图表/评分卡
```

## 技能分组参考

- **Analysis** - 深度分析类（review, risks, compare）
- **Generation** - 内容生成类（nda, terms, privacy）
- **Compliance** - 合规检查类

## 来源

github.com/zubair-trabzada/ai-legal-claude
- 1.3k stars, Python
- 14 commands, 5 parallel agents
- Contract review, risk analysis, NDA generation