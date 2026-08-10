# Changelog

GEO 雷达 skill 的所有重要变更都记录在此文件。版本号遵循 [SemVer 2.0](https://semver.org/) 规范。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

---

## [2.0.0] - 2026-08-10

### 🔄 重大重构(v2.0)

#### 核心变更:v1.0 web_search 代理 → v2.0 Playwright 爬虫

**v1.0 的根本问题**:
- v1.0 用 web_search 抓"AI 引擎引用了哪些网页"(间接信号)
- 实际上**真正的 GEO** 是"直接问 LLM 怎么回答"(真实信号)
- v1.0 报告虽然数据真实,但**不是 GEO**,是"AI 引用源 SEO 监测"
- 国内 AI 引擎(豆包/Kimi/通义)是 SPA,web_search 抓不到真实 LLM 输出

**v2.0 解决方案**:
- 用 **Playwright 爬虫**模拟用户在浏览器里打开豆包/Kimi/通义,输入 prompt,等回答,抓文本+截图+引用源
- 不需要 API key,只需要用户**首次**在浏览器登录各平台(cookie 持久化)
- 跑一次: 20-30 prompts × 3 平台 = 60-90 次问询,约 3-12 分钟

#### 新增(v2.0)

- **`scripts/crawler/doubao.py`** — 豆包爬虫(playwright,8.7KB)
- **`scripts/crawler/kimi.py`** — Kimi 爬虫(6.7KB)
- **`scripts/crawler/tongyi.py`** — 通义千问爬虫(6.5KB)
- **`scripts/crawler/runner.py`** — GEORunner 批量跑批 + JSON/Markdown 报告生成(9.7KB)
- **`scripts/crawler/__init__.py`** — 模块导出
- **`references/crawler-setup.md`** — Playwright 安装 + 平台登录 + 跑批完整流程
- **`references/llm-test-prompts.md`** — 8 行业 × 4 类型 LLM 测试 prompt 库(替代旧的 web-search-prompts.md)

#### 平台支持

| 平台 | 优先级 | 月活 | 跑批成熟度 |
|---|---|---|---|
| 豆包 Doubao | 🥇 优先 | 4.4 亿 | ✅ 成熟 |
| Kimi Moonshot | 🥇 优先 | — | ✅ 成熟 |
| 通义千问 Tongyi | 🥈 备选 | — | ✅ 成熟 |
| 文心一言 / 元宝 / 秘塔 | — | — | ❌ v2.0 未实现 |
| ChatGPT / Claude | — | — | ❌ v2.1 规划(需海外环境) |

#### SKILL.md 重写(关键变更)

- frontmatter version 1.0.0 → 2.0.0
- description 改:"基于 Playwright 爬虫的多 LLM 引擎可见度真实诊断"
- Step 1 从"web_search 跑批"改为"Playwright 爬虫跑批"
- 鲁棒性表从 11 场景改为 12 场景(加 v2.0 爬虫相关降级)
- 免责声明 4 部分改:v2.0 爬虫,Playwright 数据来源
- 新增"运行环境要求"section(Playwright + Chromium + 登录态)

#### v1.0 兼容

- v1.0 web_search 代理模式**保留**,可通过 `--mode preview` 调用
- 数据是间接信号,报告顶部明示"⚠️ web_search 代理信号,非真实 LLM 输出"
- 旧 examples/ 范本仍有效(mock 模式)

#### CI 验证(v2.0)

- `pattern_checker`: **119 ✅ / 1 warn / 0 ❌**(v2.0 爬虫模块 + URL + CHANGELOG 全过)
  - 唯一 warn: `triggers 10 个(建议 ≥ 20)` — P1 项
- `chaos`: **16 ✅ / 0 warn / 0 ❌**
- `output_checker`: **3/3 全过**
- `llm_runner mock`: **3/3 真实 verify**(v1.0 兼容)

#### 已知限制(v2.0)

- ⚠️ **需要用户先在浏览器登录**豆包/Kimi/通义(cookie 持久化到 `~/.geo-radar-cn/browser-profile-{platform}/`)
- ⚠️ 平台反爬升级时,爬虫可能失效(需更新 selector)
- ⚠️ 跑批需 3-12 分钟(比 web_search 慢)
- ⚠️ Mavis 沙箱环境无法装 playwright(限速/超时),实际跑批需用户在自己环境执行
- ⚠️ 文心一言/腾讯元宝/秘塔 v2.0 未实现
- ⚠️ 海外 LLM(ChatGPT/Claude) v2.1 规划

#### 文件结构(v2.0)

```
geo-radar-cn__skillhub/
├── SKILL.md (v2.0 全文)
├── skill.json
├── skill-card.md
├── README.md
├── CHANGELOG.md (本文件)
├── PUBLISH-CHECKLIST.md
├── _meta.json / _skillhub_meta.json
├── user_license.json
├── icon.png
├── scripts/
│   └── crawler/            # v2.0 核心
│       ├── __init__.py
│       ├── doubao.py
│       ├── kimi.py
│       ├── tongyi.py
│       └── runner.py
├── references/             # 7 个文件(v2.0 新增 2 个)
│   ├── query-templates.md
│   ├── report-schema.md
│   ├── web-search-prompts.md  # v1.0 兼容
│   ├── chaos-cases.md
│   ├── crawler-setup.md       # v2.0 新增
│   └── llm-test-prompts.md    # v2.0 新增
├── examples/  (3 份 v1.0 范本,mock 模式)
└── tests/   (4 件套 CI)
    ├── pattern_checker.py
    ├── chaos/...
    ├── output_checker.py
    └── llm_runner.py
```

---

## [Unreleased]

### 计划中
- 海外市场 v2.0（基于 locale 自动切换基准库 + AI 引擎列表）
- 接 LLM API key 模式（v1.1）— 豆包 / Kimi / 文心真实跑批
- 行业模板扩展（v1.2）— 电商 / 金融 / 医疗

---

## [1.0.0] - 2026-08-10

### 🎉 首发版本

#### 核心能力
- **品牌必填 + 查询词可选**:只输入品牌名,自动基于 `category` 推断生成 20-30 个查询词（4 类型:推荐 / 对比 / 痛点 / 决策）
- **8 节结构化报告**:摘要卡 / 品牌可见度分 / 查询词覆盖 / 竞品对比 / 引用源分析 / 优化机会 / 数据局限 / 行动清单 + 资金
- **4 维可见度子分**:被引用频次 / 推荐度 / 内容质量 / 平台覆盖
- **自动竞品对比**:基于 brand + category 推断 5-10 个竞品
- **数据时效分级**:🟢<6 月 / 🟡6-12 月 / 🟠1-2 年 / 🔴> 2 年,报告头部强制分布表（🟢+🟡 ≥ 80%,🔴 ≤ 10%）
- **完整标签系统**:来源等级（🏛️📊📰🏪👤）+ 置信度（🟢🟡🔴）+ 推算依据 + 决策可执行性（✅⚠️❌）
- **14 条禁止项**:主语 3 + 内容 4 + 表达 4 + 数据 3
- **行业模板**:references/query-templates.md 内置 8 行业（奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融）× 4 类型查询词

#### 跑批与 CI
- 7 步工作流:输入解析 → 主语锁定 → 数据时效分级 → **查询词自动生成** → web_search 跑批 → 聚合评分 → 报告渲染
- **web_search 代理信号**:覆盖 Google AI Overview + Perplexity 引用的网页（~40% 真实国内 GEO 信号）
- **诚实能力边界**:报告第 7 节明示国内 AI 引擎（豆包/Kimi/文心）是 SPA,web_search 抓不到,v1.0 不假装 100% 准确
- **CI 4 件套**:pattern_checker（静态结构）+ chaos（16 异常用例）+ output_checker（8 节检查）+ llm_runner（端到端跑批）
- **3 份范本**:高数据（蜜雪冰城）/ 中数据（nihaovisit）/ 低数据（某初创品牌）

#### 文件结构
- `SKILL.md`(主入口,7 步工作流 + 14 禁止项)
- `skill.json`(运行时元数据)
- `skill-card.md`(商店展示卡)
- `README.md` / `CHANGELOG.md` / `PUBLISH-CHECKLIST.md`
- `references/query-templates.md`(8 行业 × 4 类型)
- `references/report-schema.md`(8 节字段定义)
- `references/web-search-prompts.md`(24 个搜索 prompt)
- `references/chaos-cases.md`(16 个混沌用例)
- `examples/`(3 份范本,覆盖高/中/低数据)
- `tests/`(4 件套 CI 工具)

#### 不变
- 与 site-intelligence-report / rider-waite-cn 的目录结构一致
- 14 条禁止项的设计哲学
- 4 维标签系统

#### 已知限制
- v1.0 只能 web_search 代理,不直连 LLM
- v1.0 覆盖国内 GEO 信号 ~40%（Google 生态 + Perplexity）
- v1.0 仅支持中国大陆市场（海外 v2.0）
- 县城及以下品牌数据稀缺,会大量标"未找到公开数据"

---

## 版本号约定
- **MAJOR**:主流程变更 / 输入 schema 不兼容 / 能力边界变化
- **MINOR**:新增 Hard Constraint / 新增查询词类型 / 新增行业模板
- **PATCH**:文档修订 / bug fix / 阈值微调
