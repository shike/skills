# 选址分析报告（site-intelligence-report）

基于公开网络内容，生成结构化选址分析报告。零配置，无需 API Key。

## 触发场景

- 「我想在 [地址] 开 [品牌/品类]」
- 「分析下 [地址] 适不适合开 [品牌]」
- 「评估 [品牌] 在 [城市] 还能开吗」

## 输入

```json
{
  "brand": "蜜雪冰城",
  "address": "北京市西城区西单大悦城 B1 层 A-12",
  "city": "北京",
  "category": "奶茶",
  "expected_rent": 30000,
  "expected_area": 30
}
```

## 输出

Markdown 报告保存到工作目录：`site_report_<地址简写>_<品类>_<日期>.md`

## 报告结构

**主体 10 节**：摘要卡 / 点位信息 / 周边竞品 / 人流估算 / 客群画像 / 同类门店 / 风险评估 / 财务测算 / 谈判筹码 / 行动清单

**附录**：A 换品类建议（verdict=🔴 且原因为财务） / B 数据局限（始终） / C 决策深度分析（始终，8 项）

## 文件结构

```
site-intelligence-report__skillhub/
├── SKILL.md                  # 主入口
├── README.md                 # 本文件
├── skill.json                # 运行时元数据
├── skill-card.md             # 商店展示卡
├── references/
│   ├── report-schema.md      # 字段定义 + 附录 A/B/C
│   ├── web-search-prompts.md # 联网搜索 prompt
│   └── test-cases.md         # 3 个测试用例
└── examples/
    ├── test-run-2026-08-07-suzhou-v3.md       # 范本：苏州泰华·蜜雪冰城
    └── test-run-2026-08-07-chengdu-coffee.md  # 范本：成都春熙路·咖啡
```

## License

MIT
