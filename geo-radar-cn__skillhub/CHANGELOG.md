# Changelog

GEO 雷达 skill 的所有重要变更都记录在此文件。版本号遵循 [SemVer 2.0](https://semver.org/) 规范。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

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
