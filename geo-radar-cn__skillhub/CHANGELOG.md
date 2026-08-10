# Changelog

GEO 雷达 skill 的所有重要变更都记录在此文件。版本号遵循 [SemVer 2.0](https://semver.org/) 规范。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

---

## [2.1.0] - 2026-08-10

### 🚀 重大重构（v2.1 · WorkBuddy 原生）

#### 核心变更：v2.0 Playwright Python 爬虫 → v2.1 agent-browser（WorkBuddy 内置）

**v2.0 的根本问题**：
- v2.0 用 Playwright Python 爬虫跑 GEO 问询，需要 `pip install playwright + chromium`(~200MB)
- 沙箱装不上（PEP 668 + 网络慢），CLI 部署门槛高
- 跟 WorkBuddy 生态脱节，selector 硬编码（DOM 改要改代码）
- 用户实际运行环境是 WorkBuddy 桌面，Python 爬虫是反方向

**v2.1 解决方案**：
- **LLM 自身作为"用户"**，调 WorkBuddy 内置的 `agent-browser` skill（vercel-labs/agent-browser CLI）
- LLM 自己 `open` 豆包 → `snapshot -i` 找输入框 → `type` → `snapshot` 抓回答 → `screenshot` 留档
- 零 Python 依赖（agent-browser 用现成 Chromium）
- selector 自适应（LLM 自己看 DOM，平台改版 LLM 自己适配）
- 报告由 LLM 自己写（不再依赖 Python 生成 JSON）

#### 新增（v2.1）

- **重写 `SKILL.md`** — frontmatter v2.1.0,新增 `requiredSkills: [agent-browser]`,Step 1 重写为"LLM 调 agent-browser 跑批"
- **`references/agent-browser-setup.md`** — 替代旧的 `crawler-setup.md`,教 LLM 一步步调 agent-browser（前置检查/安装/登录/单次问询序列/平台 selector 参考/故障排查）
- **`examples/legacy-v2.0-python-crawler/`** — v2.0 Python 爬虫代码备份
  - `scripts/crawler/` 完整保留（doubao.py / kimi.py / tongyi.py / runner.py）
  - `run_mixue_demo.sh` 保留
  - `crawler-setup.md` 保留
  - `README.md` 写清楚何时用 CLI 备用

#### 变更（v2.1）

- **`scripts/crawler/`** → `examples/legacy-v2.0-python-crawler/scripts/crawler/`（移到 examples 目录）
- **`scripts/run_mixue_demo.sh`** → `examples/legacy-v2.0-python-crawler/run_mixue_demo.sh`
- **`references/crawler-setup.md`** → `examples/legacy-v2.0-python-crawler/crawler-setup.md`
- **`SKILL.md` 13 场景鲁棒性表** — 适配 v2.1（新增"agent-browser 未装"和"selector 找不到"两个场景）
- **`SKILL.md` 8 节报告结构** — 完全保留(v2.1 沿用 v2.0 的 8 节规范)
- **`SKILL.md` 标签系统 + 数据时效分级 + 免责声明** — 完全保留(Hard Constraints)

#### 平台支持

| 平台 | v2.0 | v2.1 | 备注 |
|---|---|---|---|
| 豆包 Doubao | ✅ | ✅ | 4.4 亿月活,数据最多 |
| Kimi 月之暗面 | ✅ | ✅ | 长文本能力强 |
| 通义千问 | ✅ | ✅ | 阿里系,商业覆盖 |
| 文心一言 | ⚠️ 未实现 | ⚠️ 未实现 | v2.2 计划 |
| 腾讯元宝 | ⚠️ 未实现 | ⚠️ 未实现 | v2.2 计划 |
| 秘塔 | ⚠️ 未实现 | ⚠️ 未实现 | v2.2 计划 |
| ChatGPT/Claude | ❌ 海外 | ❌ 海外 | v2.2 计划 |

#### 模式对比

| 版本 | 跑批方式 | LLM 角色 | 依赖 | 适用场景 |
|---|---|---|---|---|
| v1.0 | web_search 抓"AI 引用了哪些网页" | 拿间接信号写报告 | 无 | 最后 fallback |
| v2.0 | Playwright Python 爬虫 | 拿 JSON 写报告 | playwright + chromium(~200MB) | CLI/沙箱/CI |
| **v2.1** | **agent-browser** | **自己跑问询+抓数据+写报告** | **WorkBuddy + agent-browser** | **默认(WorkBuddy 桌面)** |

#### 兼容性

- **v1.0 web_search 模式**：保留为最后 fallback（LLM 调 web_search 工具，数据是间接信号）
- **v2.0 Python 爬虫**：保留为 CLI 备用（`examples/legacy-v2.0-python-crawler/`,用于纯 CLI / 沙箱 / CI）
- **v2.1 agent-browser**：新默认（WorkBuddy 桌面）

---

## [2.0.0] - 2026-08-10

### 🔄 重大重构（v2.0 · 已被 v2.1 取代）

> **已弃用**：v2.0 整体被 v2.1 取代,代码移到 `examples/legacy-v2.0-python-crawler/`。本节记录作为历史参考。

#### 核心变更：v1.0 web_search 代理 → v2.0 Playwright 爬虫

**v1.0 的根本问题**:
- v1.0 用 web_search 抓"AI 引擎引用了哪些网页"（间接信号）
- 实际上**真正的 GEO** 是"直接问 LLM 怎么回答"（真实信号）
- v1.0 报告虽然数据真实,但**不是 GEO**,是"AI 引用源 SEO 监测"
- 国内 AI 引擎（豆包/Kimi/通义）是 SPA,web_search 抓不到真实 LLM 输出

**v2.0 解决方案**:
- 用 **Playwright 爬虫**模拟用户在浏览器里打开豆包/Kimi/通义,输入 prompt,等回答,抓文本+截图+引用源
- 不需要 API key,只需要用户**首次**在浏览器登录各平台（cookie 持久化）
- 跑一次：20-30 prompts × 3 平台 = 60-90 次问询,约 3-12 分钟

#### 新增（v2.0）

- **`scripts/crawler/doubao.py`** — 豆包爬虫（playwright, 8.7KB）
- **`scripts/crawler/kimi.py`** — Kimi 爬虫（6.7KB）
- **`scripts/crawler/tongyi.py`** — 通义千问爬虫（6.5KB）
- **`scripts/crawler/runner.py`** — GEORunner 批量跑批 + JSON/Markdown 报告生成（9.7KB）
- **`scripts/crawler/__init__.py`** — 模块导出
- **`references/crawler-setup.md`** — Playwright 安装 + 平台登录 + 跑批完整流程
- **`references/llm-test-prompts.md`** — 8 行业 × 4 类型 LLM 测试 prompt 库（替代旧的 web-search-prompts.md）

#### 平台支持

| 平台 | 优先级 | 月活 | 跑批成熟度 |
|---|---|---|---|
| 豆包 Doubao | 🥇 优先 | 4.4 亿 | ✅ 成熟 |
| Kimi 月之暗面 | 🥇 优先 | 6000 万 | ✅ 成熟 |
| 通义千问 | 🥈 备选 | 5000 万 | ✅ 成熟 |
| 文心一言 / 腾讯元宝 / 秘塔 | — | — | ⚠️ v2.0 未实现 |
| ChatGPT / Claude / Gemini | — | — | ❌ 海外环境,v2.1 计划 |

---

## [1.0.0] - 2026-08-07

### 🎉 首发版本

#### 核心能力

- 输入品牌名（必填）+ 目标查询词（可选,自动生成）
- 输出 8 节结构化报告：摘要卡 / 品牌可见度分 / 查询词覆盖 / 竞品对比 / 引用源分析 / 优化机会 / 数据局限 / 行动清单
- 基于 web_search 代理信号覆盖 Google AI Overview + Perplexity 引用的网页

#### 8 行业 × 4 类型查询词模板

- 8 行业：奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融
- 4 类型：推荐型（找品牌）/ 对比型（品牌 PK）/ 痛点型（找解决方案）/ 决策型（分场景）
- 每个行业 20 个查询词（5 × 4）

#### 关键技术决策

- 4 维评分：被引用频次（40%）+ 推荐度（30%）+ 内容质量（20%）+ 平台覆盖（10%）
- Verdict 阈值：🔴 0-30 / 🟡 31-60 / 🟢 61-100
- 数据时效分级：🟢 < 6 月 / 🟡 6-12 月 / 🟠 1-2 年 / 🔴 > 2 年
- 来源等级 5 级：🏛️ 官方 / 📊 行业 / 📰 媒体 / 🏪 平台 / 👤 UGC

#### 已知局限（已在 v2.0 解决）

- ⚠️ v1.0 数据是"AI 引用了哪些网页",**不是**"AI 怎么回答"
- ⚠️ 国内 AI 引擎（豆包/Kimi/通义）是 SPA,web_search 抓不到真实 LLM 输出
- v2.0 用 Playwright 爬虫直接问 LLM,解决这个根本问题
