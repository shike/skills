# GEO 雷达 Skill

> **版本**: v1.0.0
> **状态**: ✅ stable
> **简介**: 面向中文用户的 GEO（生成式引擎优化）可见度诊断与优化指引
> **目录**: `geo-radar-cn__skillhub/`
> **slug**: `geo-radar-cn`

---

## 它做什么

输入你的品牌名,skill 用 web_search 跑批,统计你的品牌在 AI 搜索(GOOGLE AI Overview / Perplexity 引用的网页)里被提到的频率、位置、推荐度,然后输出 8 节结构化报告,告诉你"AI 看不看你 + 怎么改进"。

## 适用场景

- "我的品牌在豆包/Kimi/文心/ChatGPT 里被提到多少"
- "AI 搜索里我的竞品排第几"
- "我应该发什么内容才能被 AI 引用"
- "哪些网站是 AI 反复引用的源头,我要不要去那里发"

## 不适用

- 需要 **真实跑 LLM** 测品牌出现的场景(v1.0 走 web_search 代理,~40% 真实国内 GEO 信号)
- 海外英文市场(v1.x 中国大陆 only)
- 想要 SEO 排名报告(那是 SEO,不是 GEO)

## 输入要求

| 字段 | 必填 | 说明 |
|---|---|---|
| `brand` | ✅ | 品牌名 / 域名 / 产品名 |
| `queries` | ⚪ | N 个目标查询词(可选,留空自动生成 20-30 个) |
| `category` | ⚪ | 行业/品类(辅助自动生成查询词) |
| `competitors` | ⚪ | 竞品列表(辅助对比) |

## 8 节报告结构

1. **摘要卡** — verdict + 综合分 + 3 句话结论 + 关键数字
2. **品牌可见度分** — 综合分 + 4 维子分
3. **查询词覆盖** — 每个词的 AI 引用源 top 10 + 品牌标记
4. **竞品对比** — 5-10 个竞品对比表
5. **AI 引擎引用源分析** — top 20 URL / 域名 / 平台分布
6. **优化机会清单** — 3 类(立即做 / 中期 / 长期)+ 4 维评估
7. **数据局限** — 哪些引擎抓不到 + 置信度说明
8. **行动清单 + 资金** — 3 大类 + 3-5 条红线

## ⚠️ 能力边界(诚实声明)

v1.0 用 web_search 抓 AI 引用源:
- ✅ **覆盖**:Google AI Overview + Perplexity 引用基础(~40% 真实国内 GEO 信号)
- ❌ **不覆盖**:豆包 / Kimi / 文心一言 / 腾讯元宝 / 秘塔等国内 AI 引擎(它们是 SPA,内容不公开)
- ⚠️ **想覆盖国内原生 AI 引擎**:v2.0 接 LLM API key 模式

报告第 7 节"数据局限"会明示这一点,不假装 100% 准确。

## 跑批性能

- 单次跑批:N=30 查询词 × 5-10 个结果 = ~200-300 web_search 调用
- 数据时效:🔴 > 2 年的引用标"仅作历史参考",🟢+🟡 ≥ 80% 硬指标
- CI 套件:4 件套(参考 site-intelligence-report)

## 文件结构

```
geo-radar-cn__skillhub/
├── SKILL.md                       # 主入口（7 步工作流 + 14 禁止项）
├── skill.json                     # 运行时元数据
├── skill-card.md                  # 商店展示卡
├── README.md                      # 本文件
├── CHANGELOG.md                   # 版本变更记录
├── PUBLISH-CHECKLIST.md           # 上架清单
├── _meta.json / _skillhub_meta.json
├── icon.png                       # 商店封面图（平台独立字段上传）
├── references/
│   ├── query-templates.md         # 8 行业 × 4 类型查询词模板
│   ├── report-schema.md           # 8 节报告字段定义
│   ├── web-search-prompts.md      # 24 个搜索 prompt 模板
│   └── chaos-cases.md             # 16 个混沌测试用例
├── examples/
│   ├── test-run-2026-08-10-蜜雪冰城-high.md
│   ├── test-run-2026-08-10-nihaovisit-medium.md
│   └── test-run-2026-08-10-某初创品牌-low.md
└── tests/
    ├── pattern_checker.py
    ├── chaos/test_chaos.py
    ├── output_checker.py
    └── llm_runner.py
```

## 自动化测试

```bash
cd geo-radar-cn__skillhub

# 1. 静态模式检查
python3 tests/pattern_checker.py
# 期望：✅ 100+ pass / 0 ❌

# 2. 混沌测试
python3 tests/chaos/test_chaos.py
# 期望：✅ 12+ pass / 0 ❌

# 3. 输出检查
python3 tests/output_checker.py --batch examples/
# 期望：3/3 全过

# 4. 跑批
python3 tests/llm_runner.py --mock
# 期望：3/3 全过
```

详细见 [`SKILL.md`](./SKILL.md)。

## 适用范围

- ✅ 中国大陆市场(v1.0 主战场)
- ⚠️ 海外英文市场(v2.0 规划,基准库和 AI 引擎列表都要换)
- ⏳ 港澳台(v2.0 规划)

## 未来规划

- v1.1:接 LLM API key 模式(豆包/Kimi/文心真实跑批)
- v1.2:行业模板扩展(电商 / 金融 / 医疗)
- v2.0:海外市场(英文 + 多语言)
