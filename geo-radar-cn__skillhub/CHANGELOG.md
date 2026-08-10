# Changelog

GEO 雷达 skill 的所有重要变更都记录在此文件。版本号遵循 [SemVer 2.0](https://semver.org/) 规范。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

---

## [2.3.0] - 2026-08-10

### 🚀 重大重构（v2.3 · 10MB 装 1 次 · 真实数据 · skillhub 上架主版本）

#### 背景：v2.2 的根本问题

v2.2 用 LLM 模拟"豆包/Kimi/通义"3 个国内主流 LLM 平台,虽然 0 安装即装即用,但：
- **不是真实平台输出**(LLM 模拟 ≠ 真实豆包回答)
- 同 prompt 不同 LLM 答案不同
- 数据滞后性(LLM 训练数据 vs 平台最新回答)

用户反馈：**"我要真实数据"**。v2.2 模拟不满足这个核心需求。

#### v2.3 解决方案

**Playwright + 系统 Chrome 复用**:
- `pip install playwright` = 10MB(5-10 秒装好,永久用)
- **不** 下载 Chromium(免 200MB)
- 用系统已装的 Google Chrome 跑
- 真实打开豆包/Kimi/通义,模拟用户问询
- cookie 持久化 30 天,首次登录后续免登录

**总成本:10MB 装 1 次,0 持续成本,真实数据 90%+**。

#### 跨 AI 平台策略

- v2.3(默认):WorkBuddy / MiniMax Code / Cursor 等支持 Python 执行的 AI 平台
- v2.2(fallback):Claude.ai / ChatGPT 网页版等无 Python 平台
- v2.1(可选):WorkBuddy Power User,想用 agent-browser 替代
- v1.0(最后):所有都失败时的 web_search

LLM 在跑批前自动检测环境,选最合适的模式。

#### 关键诚实声明

- ✅ 真实平台输出 90%+(豆包/Kimi/通义 实际回答)
- ⚠️ 需用户已登录目标平台(cookie 持久化到 ~/.geo-radar-cn/browser-profile-*/)
- ⚠️ 跑批时间 3-12 分钟(看网络 + LLM 速度)
- ⚠️ 10MB 装 1 次(Mac 用户的 Mac 已有 Google Chrome;Linux/Windows 用户需先装 Chrome)

#### 新增（v2.3）

- **`SKILL.md` 重写 v2.3.0** — frontmatter 改 v2.3,Step 1 改"Playwright + 系统 Chrome",加 1 段头部数据来源声明
- **`scripts/crawler/` 恢复主路径** — 从 git 79574f2 恢复 v2.0 的爬虫代码,移到 `scripts/crawler/`(不再放 examples/legacy)
- **`references/mode-v22-llm-roleplay.md`** — v2.2 fallback 文档(3 角色 prompt + 降级路径)
- **`references/mode-v21-agent-browser.md`** — v2.1 Power User 高级模式文档
- **`references/mode-v10-web-search.md`** — v1.0 最后 fallback 文档

#### 变更（v2.3）

- **`examples/legacy-v2.0-python-crawler/`** → **`scripts/crawler/`**(主路径,不再 legacy)
- **`examples/legacy-v2.0-python-crawler/run_mixue_demo.sh`** → **`examples/run_mixue_demo.sh`**
- **`references/crawler-setup.md`** → **`references/mode-v21-agent-browser.md`**(重定位)
- **Step 1 从"LLM 模拟 3 平台"改为"Playwright + 系统 Chrome 真实抓"**
- **鲁棒性表** — 加 5 个 v2.3 场景(Python 不可用/Playwright 未装/Chromium 未下载/未登录/selector 找不到)
- **8 节报告结构** — 完全保留(v2.3 沿用 v2.0 的 8 节规范)
- **标签系统 + 数据时效分级 + 免责声明** — 完全保留(Hard Constraints)
- **`skill.json` `input_schema` 加 `mode` 字段** — 用户可指定模式

#### 模式自动降级路径

```python
def select_mode():
    if python_executable_available() and playwright_installed() and chrome_path_exists():
        return "v2.3 Playwright + 系统 Chrome"  # 默认
    elif llm_can_roleplay():
        return "v2.2 LLM 模拟"  # fallback
    elif llm_has_web_search():
        return "v1.0 web_search"  # 最后 fallback
    else:
        return "ERROR: 报告无法生成"

if user_says("真实数据"):
    mode = "v2.3"  # 或 v2.1 if WorkBuddy + agent-browser 已装
```

#### 兼容性

- **v2.2 LLM 模拟**:保留作 fallback(无 Python 平台)
- **v2.1 agent-browser**:保留作 Power User 高级模式(WorkBuddy + 50-500MB)
- **v2.0 Playwright Python 爬虫**:被 v2.3 取代(相同的爬虫代码,只是默认用系统 Chrome)
- **v1.0 web_search**:保留作最后 fallback
- **v2.3 Playwright + 系统 Chrome**:新默认(10MB 装 1 次,真实 90%+)

#### 上架到 skillhub 的版本

v2.3 是上架主版本,10MB 装 1 次,跨平台(支持 Python 的 AI 平台)。

---

## [2.2.0] - 2026-08-10

### 🔄 重大重构（v2.2 · 已被 v2.3 取代为 fallback）

> **状态**：v2.2 LLM 模拟模式已被 v2.3 取代为"无 Python 环境的 fallback",不再是默认。文档迁移到 `references/mode-v22-llm-roleplay.md`。

#### 核心变更

- 用 LLM 模拟 3 个国内主流 LLM 平台(豆包/Kimi/通义)回答 20-30 个查询词
- 0 安装,跨所有 AI 平台
- 反映 60-80% 的 GEO 信号

#### 为什么被取代

v2.2 的根本问题是**不是真实平台输出**。用户反馈"我要真实数据",v2.2 模拟不满足这个核心需求。v2.3 用 Playwright + 系统 Chrome 真实抓取,10MB 装 1 次,真实 90%+。

#### v2.2 现在是无 Python 环境的 fallback

仅在 Claude.ai / ChatGPT 网页版等不支持 Python 执行的 AI 平台启用。

---

## [2.1.0] - 2026-08-10

### 🔄 重大重构（v2.1 · WorkBuddy 原生 · 已被 v2.3 取代为 Power User 高级模式）

> **状态**：v2.1 agent-browser 模式已被 v2.3 取代为"WorkBuddy Power User 高级模式",不再是默认。文档迁移到 `references/mode-v21-agent-browser.md`。

#### 核心变更

- v2.0 Playwright Python 爬虫 → v2.1 agent-browser(WorkBuddy 内置)
- LLM 调 WorkBuddy 内置的 agent-browser skill
- 真实打开豆包/Kimi/通义,模拟用户问询

#### 为什么被取代

v2.1 需要 50-500MB 安装(agent-browser + Chromium),成本太高,且限定 WorkBuddy 平台。v2.3 用 Playwright + 系统 Chrome 复用,只要 10MB 装 1 次,跨更多平台。

#### v2.1 现在是 WorkBuddy Power User 高级模式

仅在用户明确要"agent-browser 模式"且在 WorkBuddy 环境跑时启用。

---

## [2.0.0] - 2026-08-10

### 🔄 重大重构（v2.0 · 已被 v2.3 取代）

> **已弃用**：v2.0 Playwright Python 爬虫整体被 v2.3 取代,代码从 git 79574f2 恢复到 `scripts/crawler/`(主路径)。本节记录作为历史参考。

#### 核心变更

- v1.0 web_search 代理 → v2.0 Playwright Python 爬虫
- 用 Playwright 模拟用户在浏览器里打开豆包/Kimi/通义,输入 prompt,等回答,抓真实 LLM 输出
- 不需要 API key,只需要用户首次在浏览器登录各平台(cookie 持久化)

#### v2.3 优化

v2.3 沿用 v2.0 的爬虫代码,只优化 1 点:**默认用系统 Chrome 复用,免下 200MB Chromium**。

---

## [1.0.0] - 2026-08-07

### 🎉 首发版本

#### 核心能力

- 输入品牌名(必填)+ 目标查询词(可选,自动生成)
- 输出 8 节结构化报告:摘要卡 / 品牌可见度分 / 查询词覆盖 / 竞品对比 / 引用源分析 / 优化机会 / 数据局限 / 行动清单
- 基于 web_search 代理信号覆盖 Google AI Overview + Perplexity 引用的网页

#### 8 行业 × 4 类型查询词模板

- 8 行业:奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融
- 4 类型:推荐型(找品牌)/ 对比型(品牌 PK)/ 痛点型(找解决方案)/ 决策型(分场景)
- 每个行业 20 个查询词(5 × 4)

#### 关键技术决策

- 4 维评分:被引用频次(40%)+ 推荐度(30%)+ 内容质量(20%)+ 平台覆盖(10%)
- Verdict 阈值:🔴 0-30 / 🟡 31-60 / 🟢 61-100
- 数据时效分级:🟢 < 6 月 / 🟡 6-12 月 / 🟠 1-2 年 / 🔴 > 2 年
- 来源等级 5 级:🏛️ 官方 / 📊 行业 / 📰 媒体 / 🏪 平台 / 👤 UGC

#### 已知局限(已在 v2.0/v2.1/v2.2/v2.3 解决)

- ⚠️ v1.0 数据是"AI 引用了哪些网页",**不是**"AI 怎么回答"
- ⚠️ 国内 AI 引擎(豆包/Kimi/通义)是 SPA,web_search 抓不到真实 LLM 输出
- v2.0 用 Playwright 爬虫直接问 LLM,解决这个根本问题
- v2.1 改用 agent-browser,WorkBuddy 原生
- v2.2 用 LLM 模拟,即装即用(60-80%)
- v2.3 用 Playwright + 系统 Chrome 复用,10MB 装 1 次,真实 90%+
