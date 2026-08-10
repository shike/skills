# location-skill

选址分析相关的 LLM skills 集合。

## 当前状态

| Skill | 版本 | 状态 | 简介 |
|---|---|---|---|
| [site-intelligence-report](./site-intelligence-report__skillhub/) | 1.1.0 | ✅ stable | 10 节结构化选址分析报告（24 字段 + 附录 A/B/C） |

## Skills

### site-intelligence-report (v1.1.0)

基于用户输入的品牌、点位和品类，生成 10 节结构化选址分析报告。

**核心能力**：
- 数据来源：公开网络内容（web_search）
- 零 API Key 配置
- 5 块必加规则：数据时效分级 / 完整标签系统 / 3x3 财务敏感性矩阵 / 概率×影响 风险矩阵 / 行动清单+资金准备
- 鲁棒性：10 场景（web_search 不可用 / 多语言 / 跨 LLM provider / token 截断等）
- 范本：苏州泰华·蜜雪冰城（#001）+ 成都春熙路·咖啡（#002）

**文件结构**：
```
site-intelligence-report__skillhub/
├── SKILL.md                       # 主入口（工作流 5 步 + 14 条禁止项）
├── README.md                      # skill 介绍
├── skill.json                     # 运行时元数据
├── skill-card.md                  # 商店展示卡
├── CHANGELOG.md                   # 版本变更记录
├── references/
│   ├── report-schema.md           # 10 节 + 24 字段定义 + 公式 + 渲染规则
│   ├── web-search-prompts.md      # 24 字段 prompt 模板
│   ├── test-cases.md              # 3 个测试用例 + 评分标准
│   └── category-baseline.md       # 6 品类行业基准表（v1.1.0 新增）
├── examples/
│   ├── test-run-2026-08-07-suzhou-v3.md
│   └── test-run-2026-08-07-chengdu-coffee.md
└── _meta.json / _skillhub_meta.json
```

**自动化测试**：
```bash
python3 tests/pattern_checker.py
```

详细见 [`site-intelligence-report__skillhub/SKILL.md`](./site-intelligence-report__skillhub/SKILL.md)。

## 适用范围

- ✅ 中国大陆城市（v1.1.0 主战场）
- ⏳ 海外场景（v2.0 规划中，参见 [CHANGELOG.md Unreleased](./site-intelligence-report__skillhub/CHANGELOG.md)）

## 未来规划

- 第二个 skill 方向：商圈热度评估 / 租金谈判脚本 / 竞品对标深度分析（待定）
- LLM 真实跑批的 CI 测试（当前只有 pattern checker 静态分析）
- 选址决策的端到端自动化（输入地址 → 输出签约建议）
