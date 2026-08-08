# location-skill

选址分析相关的 LLM skills 集合。

## Skills

### site-intelligence-report

基于用户输入的品牌、点位和品类，生成 10 节结构化选址分析报告（24 字段 + 附录 A/B/C）。

- 数据来源：公开网络内容（web_search）
- 零 API Key 配置
- 包含：数据时效分级、完整标签系统、3x3 财务敏感性矩阵、概率×影响风险矩阵、行动清单 + 资金准备
- 鲁棒性：10 场景（web_search 不可用 / 多语言 / 跨 LLM provider / token 截断等）
- 范本：苏州泰华·蜜雪冰城（#001）+ 成都春熙路·咖啡（#002）

详细见 `site-intelligence-report__skillhub/SKILL.md`。
