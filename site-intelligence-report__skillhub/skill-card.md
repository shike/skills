## Description

基于用户输入的品牌、点位和品类，生成 24 字段结构化选址分析报告。数据来源为公开网络内容，无需任何 API Key 配置。包含财务反推 + 自动变红 + 附录 A（换品类）+ 附录 C（8 项决策深度分析）+ 盈亏平衡 + 公开房源 + 风险评分卡 + 谈判话术。

## License

MIT

## Use Case

Retail brand expansion teams, site selection analysts, and individual entrepreneurs use this skill to evaluate a specific store location. The skill generates a 24-field structured report covering location profile, competitor analysis, foot traffic estimates, customer profile, similar store performance, risk assessment, financial projection (with breakeven analysis and 6-month cashflow forecast), public rental listings, delivery volume of competitors, risk score card, seasonality, and negotiation talking points, all based on publicly available web sources. Supports multi-address comparison mode (2+ addresses in one query).

Deployment geography: **China only (v1.x)**. 海外场景（英文/非中国城市）需要不同基准库和品牌参考，v2.0 规划中。参见 [CHANGELOG.md Unreleased](./CHANGELOG.md) 了解 v2.0 计划。

## Key Features

- **24 structured fields** — 10 main report sections + 3 appendices (A: alternatives when verdict is red, B: data limitations, C: 8-dimension decision analysis)
- **Data freshness grading** — every fact tagged with 🟢<6mo / 🟡6-12mo / 🟠1-2y / 🔴>2y, report header shows distribution
- **Complete label system** — source level (🏛️/📊/📰/🏪/👤) + confidence (🟢/🟡/🔴) + decision actionability (✅/⚠️/❌)
- **3x3 financial sensitivity matrix** — 9 scenarios per price band, replacing single-variable sensitivity
- **Probability × impact risk matrix** — 6 dimensions, replacing weighted-average scoring
- **Action list with 4-dimension assessment** — cost / benefit / risk / decision actionability per action
- **Funding checklist** — 3 categories (one-time / ramp-up / emergency), preventing under-capitalization
- **Breakeven analysis** — daily volume required + sensitivity
- **6-month cashflow forecast** — ramp-up assumptions + payback month
- **Public rental listings** — 58.com / Anjuke data (median / P25 / P75)
- **Competitor delivery volume** — Meituan / Ele.me monthly sales
- **Negotiation talking points** — script-style based on public data
- **Multi-address comparison mode** — input 2+ addresses, output comparison matrix + recommendation
- **Auto-red verdict mechanism** — when monthly profit ≤ 0 OR payback > 24 months, automatically downgrade verdict to red
- **8-dimension decision framework** (Appendix C) — category fit, differentiation, **pre-signing legal check (8 hard items)**, location history, position value, personal/resource risk, exit/stop-loss, insurance/hedging
- **Zero configuration** — no API key required

## Known Risks and Mitigations

**Risk 1: Data accuracy and freshness** — All data is sourced from public web content, which may include outdated, inaccurate, or biased information.
**Mitigation**: The skill explicitly marks data sources and freshness (🟢<6mo / 🟡6-12mo / 🟠1-2y / 🔴>2y), requires citation for every fact, and never fabricates data. Missing data is labeled as "未找到公开数据" rather than guessed. Report header enforces a data freshness distribution table (🟢+🟡 ≥ 80%, 🔴 ≤ 10%).

**Risk 2: Industry baseline hallucination** — Financial projections (回本周期 / 盈亏平衡 / 3x3 矩阵 / 6 月现金流) depend on industry baseline values (客单价 / 食材成本率 / 装修单价 / 人工配比), which an LLM may hallucinate.
**Mitigation**: v1.1.0 introduces `references/category-baseline.md` with pinned baseline values for 6 categories (奶茶/咖啡/快餐/正餐/麻辣烫/烘焙), sourced from CCFA 2024-2025 reports, Meituan industry reports, and brand financial disclosures. Every推算数字 must reference this table or be explicitly marked as LLM 推算 with reasoning chain.

**Risk 3: Cross-LLM provider compatibility** — Different LLM providers (OpenAI / Anthropic / Google / local models) have different API formats, JSON-mode behaviors, and reasoning block conventions.
**Mitigation**: Prompt templates are designed to work across providers (Chat / Responses / Messages API). JSON-mode is disabled to favor natural language rendering. The skill includes a robustness table for handling `<think>` blocks (stripped before rendering) and various output formats.

**Risk 4: Subject drift (主语漂移)** — LLM may unconsciously shift the report's subject from the user's brand to a more famous competitor (e.g., writing financial projections for 霸王茶姬 when the user asked for 蜜雪冰城).
**Mitigation**: Step 0.5 主语锁定 is a Hard Constraint. Step 5 自检 verifies 主品牌 appears in summary card, financial model uses 主品牌, action list targets 主品牌, and no "如果换品牌为 X" complete financial projections exist. Pattern checker (`tests/pattern_checker.py`) verifies A1-A4 in CI.

## Reference

- [Report Schema Definition](references/report-schema.md)
- [Web Search Prompts](references/web-search-prompts.md)
- [Test Cases](references/test-cases.md)
- [Sample Test Run - Suzhou Mixue](examples/test-run-2026-08-07-suzhou-v3.md)
- [Sample Test Run - Chengdu Coffee](examples/test-run-2026-08-07-chengdu-coffee.md)

## Skill Output

- **Type**: text, markdown, files
- **Format**: Markdown report saved to working directory
- **Content**: 10 sections + 3 appendices (A: alternatives when red, B: data limitations, C: 8-dimension decision analysis). Each fact includes at least one source link. Multi-address mode outputs comparison matrix + N individual reports.

## Skill Version

1.1.0
