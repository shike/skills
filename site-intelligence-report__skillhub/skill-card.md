## Description

基于用户输入的品牌、点位和品类，生成 24 字段结构化选址分析报告。数据来源为公开网络内容，无需任何 API Key 配置。包含财务反推 + 自动变红 + 附录 A（换品类）+ 附录 C（8 项决策深度分析）+ 盈亏平衡 + 公开房源 + 风险评分卡 + 谈判话术。

## License

MIT

## Use Case

Retail brand expansion teams, site selection analysts, and individual entrepreneurs use this skill to evaluate a specific store location. The skill generates a 24-field structured report covering location profile, competitor analysis, foot traffic estimates, customer profile, similar store performance, risk assessment, financial projection (with breakeven analysis and 6-month cashflow forecast), public rental listings, delivery volume of competitors, risk score card, seasonality, and negotiation talking points, all based on publicly available web sources. Supports multi-address comparison mode (2+ addresses in one query).

Deployment geography: China (primary), global (any city with public data).

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

**Risk**: All data is sourced from public web content, which may include outdated, inaccurate, or biased information.

**Mitigation**: The skill explicitly marks data sources and freshness, requires citation for every fact, and never fabricates data. Missing data is labeled as "未找到公开数据" rather than guessed. Financial projections are explicitly labeled as estimates with assumptions stated.

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
