---
name: GEO 雷达 v2.3：基于 Playwright + 系统 Chrome 的多 LLM 引擎可见度真实诊断（10MB 装 1 次）
version: 2.3.0
description: |
  面向中文用户的 GEO（生成式引擎优化）可见度诊断 skill,10MB 装 1 次永久用。
  v2.3 核心:用 Playwright Python 爬虫 + 系统 Chrome 复用(免下 200MB Chromium),
  真实打开豆包/Kimi/通义 网页,输入 prompt,抓真实 LLM 输出(文本+截图+引用源),
  分析品牌在 AI 回答中的出现频次 / 排名位置 / 推荐度。
  不需要 API key,只需要用户首次在浏览器登录各平台(cookie 持久化,30 天免登录)。
  跑一次:20-30 prompts × 3 平台 = 60-90 次问询,约 3-12 分钟。
  v2.2 LLM 模拟模式保留为无 Python 环境 fallback(Claude/ChatGPT 等)。
  v2.1 agent-browser 模式保留为 WorkBuddy Power User 高级玩法(可选,~50-500MB)。
  v1.0 web_search 模式保留为最后 fallback。
  输入品牌名(必填)+ 目标查询词(可选)+ 行业/竞品(可选),
  输出 8 节结构化报告(摘要卡 / 品牌可见度分 / 查询词覆盖 /
  竞品对比 / 引用源分析 / 优化机会 / 数据局限 / 行动清单)。
entry: SKILL.md
runtime: llm
tags:
  - GEO
  - AI 搜索
  - 品牌可见度
  - 生成式引擎优化
  - LLM 引用
  - 内容优化
  - 竞品分析
  - 真实 LLM 输出
  - 10MB 装 1 次
  - 系统 Chrome 复用
---

# GEO 雷达 v2.3 · Skill 主入口（Python 爬虫 + 系统 Chrome）

> **核心能力(v2.3)**:输入品牌名 → 自动生成查询词(可选) → **Playwright 爬虫用系统 Chrome 真实打开豆包/Kimi/通义** → 输出 8 节结构化报告
>
> **v2.3 vs v2.2 vs v2.1 vs v1.0 关键差异**:
> | 版本 | 跑批方式 | 安装成本 | 持续成本 | 真实度 | 跨平台 |
> |---|---|---|---|---|---|
> | v1.0 | web_search 抓"AI 引用了哪些网页" | 0 | 0 | 30-50% | ✅ |
> | v2.1 | agent-browser 真实打开豆包/Kimi/通义 | 50-500MB | 0 | 90%+ | ❌ 仅 WorkBuddy |
> | v2.2 | LLM 模拟 3 平台 | 0 | 0 | 60-80% | ✅ |
> | **v2.3** | **Playwright + 系统 Chrome 真实抓** | **10MB** | **0** | **90%+** | **⚠️ WorkBuddy/MiniMax Code/Cursor** |
>
> **能力边界**:v2.3 需要 Python 3.10+ + Playwright(~10MB) + 系统 Chrome;详见"运行环境要求"。
> **诚实声明**:报告基于真实 LLM 输出,但爬虫可能受反爬/登录态影响,详见第 7 节"数据局限"。

---

## 适用场景

- "我的品牌在豆包/Kimi/通义里被提到多少"(基于真实抓取)
- "AI 搜索里我的竞品排第几"
- "我应该发什么内容才能被 AI 引用"
- "哪些网站是 AI 反复引用的源头,要不要去那里发"

## 不适用

- AI 平台不支持 Python 执行(如 Claude.ai / ChatGPT 网页版)→ 降级 v2.2 LLM 模拟
- 海外英文市场(v2.4 规划)
- 行业不在 8 行业模板内且用户不输入 `category`(降级通用模板,效果下降)

## 运行环境要求(v2.3 关键)

| 项 | 要求 | 大小 |
|---|---|---|
| Python | 3.10+ | 系统已有 |
| Playwright | `pip install playwright` | **~10MB** |
| Chromium | **不下载** — 复用系统 Chrome | 0 |
| 系统 Chrome | Mac: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` / Linux: `/usr/bin/google-chrome` | 用户已装 |
| 各平台登录态 | **首次使用**:运行 `python -m crawler.runner --login`,浏览器自动打开,**用户手动登录**豆包/Kimi/通义,cookie 自动保存到 `~/.geo-radar-cn/browser-profile-*/`,后续免登录 30 天 | 一次 |
| 跑批时间 | 20-30 prompts × 3 平台 = 60-90 次问询,约 **3-12 分钟** | — |
| 反爬间隔 | 默认 3 秒/次(可调) | — |
| 国内环境 | 必须,海外 LLM 平台不在 v2.3 范围 | — |

**总安装成本:10MB,5-10 秒装好,永久用,真实数据 90%+**。

---

## 三种模式(按平台自动选)

| 模式 | 触发条件 | 文档 |
|---|---|---|
| **v2.3 Python 爬虫(默认)** | AI 平台支持 Python 执行(WorkBuddy / MiniMax Code / Cursor / Windsurf 等) | 本 README |
| v2.2 LLM 模拟(fallback) | AI 平台不支持 Python(Claude.ai / ChatGPT 网页版等) | `references/mode-v22-llm-roleplay.md` |
| v2.1 agent-browser(可选) | WorkBuddy 用户,想要 Playwright 替代方案(50-500MB 安装) | `references/mode-v21-agent-browser.md` |
| v1.0 web_search(最后 fallback) | 上述全失败,LLM 用 web_search 工具 | `references/mode-v10-web-search.md` |

LLM 在跑批前自动检测:
```python
if python_executable_available() and playwright_installed() and chrome_path_exists():
    mode = "v2.3 Python 爬虫"
elif llm_can_roleplay():
    mode = "v2.2 LLM 模拟"
else:
    mode = "v1.0 web_search"
```

---

## 输入要求

字段定义见 `skill.json` 的 `input_schema`。
- **必填**:`brand`(品牌名 / 域名 / 产品名)
- **选填**:`queries`(N 个目标查询词)、`category`(行业/品类)、`competitors`(竞品列表)

**输入格式**:JSON(推荐)或自然语言。LLM 需把自然语言解析为 `input_schema`,解析失败字段用下方 Fallback 规则。解析后向用户确认 1 次(必填 `brand`)即可启动。

**Fallback 规则**(用户输入缺失或异常时):

| 字段 | 缺/异常 | Fallback |
|---|---|---|
| `brand` 缺失 | **必填,直接询问用户** | — |
| `brand` 是 URL | LLM 解析为域名(如 `https://nihaovisit.com` → `nihaovisit.com`),报告里"品牌可见度"按域名算 | 不可阻塞 |
| `queries` 缺失 | 自动基于 `brand` + `category` 调用 `references/llm-test-prompts.md` 生成 20-30 个查询词 | 自动 |
| `queries` 数量 < 5 | 提示用户"查询词太少,自动补充 N 个";LLM 在用户提供的词基础上补充 | 半自动 |
| `category` 缺失 | LLM 基于 `brand` 推断(品牌名含品类词如"奶茶店"直接命中;否则用通用 4 类型模板) | 自动 |
| `competitors` 缺失 | LLM 基于 `brand` + `category` 推断 5-10 个竞品(参见 `references/llm-test-prompts.md` 行业竞品库) | 自动 |

---

## 工作流(7 步)

### Step 0:输入解析

LLM 把自然语言解析为 4 字段,解析后向用户确认 1 次。

**示例 — 用户自然语言**:
> "帮我看下蜜雪冰城在 AI 搜索里被提到多少"

LLM 解析为:
```json
{
  "brand": "蜜雪冰城",
  "queries": null,
  "category": "奶茶",
  "competitors": null
}
```

**示例 — 用户给了部分字段**:
> "分析下 nihaovisit.com,主要问题:北京旅游攻略、中国签证、外国人来华"

LLM 解析为:
```json
{
  "brand": "nihaovisit.com",
  "queries": ["北京旅游攻略", "中国签证", "外国人来华"],
  "category": "旅游",
  "competitors": null
}
```

### Step 0.5:主语锁定(Hard Constraint)

解析后第一件事锁定主品牌 / 主域名 / 主行业,全文围绕主品牌展开。

1. **品牌可见度分**必须针对主品牌
2. **竞品对比**只能列同行业竞品,其他品牌数字仅做对标引用,不进入主评分
3. **优化机会清单**只针对主品牌的可执行动作
4. **行动清单**针对主品牌,不能"如果换品牌为 X"展开测算

### Step 0.6:数据时效分级(Hard Constraint)

报告所有数据必须标时效,过期数据不能当决策依据。

| 等级 | 时效 | 决策参考性 | 标注 |
|---|---|---|---|
| 🟢 | < 6 月 | 直接可用 | `🟢 YYYY-MM` |
| 🟡 | 6-12 月 | 可用,建议复核 | `🟡 YYYY-MM, 已 X 月` |
| 🟠 | 1-2 年 | 决策前需现场验证 | `🟠 YYYY-MM, 已 X 年` |
| 🔴 | > 2 年 | 仅作历史参考 | `🔴 YYYY-XX, 已 X 年, 仅作历史参考` |

数据分类:
- 📌 历史事实(报道发布时间/网页发布时间)
- ⏱️ 经营现状(实时性弱,2024 年中报道在 2026-08 仍可参考但需复核)

**报告头部必备数据时效分布表**(4 档 + 占比),**硬指标**:🟢 + 🟡 ≥ 80%;🔴 ≤ 10%。

### Step 0.7:查询词自动生成(关键)

**当 `queries` 缺失或不足 5 个时**,执行自动生成。

**Step 0.7.1:行业推断**
- 品牌名直接命中:`蜜雪冰城` → 奶茶 / `nihaovisit` → 旅游 / `Notion` → 生产力 SaaS
- 用户给 `category` 直接用
- 都不命中:用通用 4 类型模板(20 个)

**Step 0.7.2:加载行业模板**

`references/llm-test-prompts.md` 内置 8 行业 × 4 类型(推荐/对比/痛点/决策)查询词模板:

- 8 行业:奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融
- 4 类型:推荐型(找品牌)/ 对比型(品牌 PK)/ 痛点型(找解决方案)/ 决策型(分场景)
- 每个行业 20 个查询词(5 × 4)

**Step 0.7.3:注入品牌名**

模板查询词含占位符 `[品牌]` / `[品类]`,LLM 替换为具体值:

```
模板:"2026 最受欢迎 [品类] 品牌"
注入:[品类]=奶茶 → "2026 最受欢迎奶茶品牌"

模板:"[品牌] vs [竞品]"
注入:[品牌]=蜜雪冰城, [竞品]=古茗 → "蜜雪冰城 vs 古茗"
```

**Step 0.7.4:数量控制**

- 默认生成 20-30 个查询词
- 4 类型各 5-7 个
- 用户给了部分 → 补充到 20-30 个

**Step 0.7.5:输出到 LLM 上下文**

```json
{
  "auto_generated_queries": [
    "2026 最受欢迎奶茶品牌",       // 推荐型
    "高性价比奶茶排行",             // 推荐型
    "平价奶茶推荐",                 // 推荐型
    ...
    "蜜雪冰城 vs 古茗",            // 对比型
    "蜜雪冰城 vs 喜茶",            // 对比型
    ...
    "奶茶怎么选",                  // 痛点型
    "开奶茶店选址",                // 痛点型
    ...
    "学生党奶茶",                  // 决策型
    "上班族奶茶",                  // 决策型
    ...
  ],
  "industry": "奶茶",
  "competitors": ["古茗", "喜茶", "益禾堂", "茶百道", "沪上阿姨"]
}
```

### Step 1:模式选择(自动)

LLM 跑批前先自动检测 + 选择模式:

```python
def select_mode():
    # v2.3 Python 爬虫(默认)
    if python_available() and playwright_installed() and chrome_path_exists():
        return "v2.3"

    # v2.2 LLM 模拟(fallback)
    if llm_can_roleplay():
        return "v2.2"

    # v1.0 web_search(最后 fallback)
    if llm_has_web_search():
        return "v1.0"

    # 全失败
    return "ERROR: 报告无法生成"

# 用户也可手动指定 mode
if user_says("真实数据"):
    mode = "v2.3"  # 或 v2.1 if WorkBuddy + agent-browser 已装
```

### Step 2:v2.3 Python 爬虫跑批(默认 · 真实 LLM 输出)

**这是 v2.3 的核心步骤** — 用 Playwright + 系统 Chrome 真实打开豆包/Kimi/通义,模拟用户在浏览器里问问题,抓真实 LLM 输出。

#### Step 2.0:前置检查 + 平台登录

```bash
# 1. 安装 Playwright(只需 10MB,不下载 Chromium)
pip install --user --break-system-packages playwright

# 2. 首次使用:用户手动登录各平台
cd /path/to/geo-radar-cn__skillhub
python3 -m crawler.runner --login
# 浏览器自动打开,用户在每个 tab 登录豆包/Kimi/通义,完成后按 Enter
# cookie 自动保存到 ~/.geo-radar-cn/browser-profile-{platform}/
# 后续 30 天免登录
```

#### Step 2.1:跑批命令

```bash
# 完整跑批(3 平台 × 20 prompts = 60 次问询,约 3-6 分钟)
# 默认用系统 Chrome(--use-system-chrome 自动检测,免下 200MB Chromium)
python3 -m crawler.runner \
  --brand "蜜雪冰城" \
  --auto-prompts \
  --category 奶茶 \
  --use-system-chrome \
  --output json

# 或用用户提供的 prompts
python3 -m crawler.runner \
  --brand "蜜雪冰城" \
  --prompts my_queries.json \
  --use-system-chrome \
  --output markdown
```

**关键设计**:`--use-system-chrome` 自动检测并复用系统已装的 Chrome,跳过 `playwright install chromium`(~200MB)下载。

#### Step 2.2:每次问询抓取的数据

- 平台名(豆包/Kimi/通义)
- 用户 prompt
- LLM 回答完整文本(text)
- 引用源列表(citations: 标题 + URL)
- 页面截图(供审计)
- 耗时(秒)
- 成功/失败状态

#### Step 2.3:关键约束

- 禁止用模型记忆填充,**所有数据必须来自真实爬虫问询**
- 爬虫失败 → 重试 1 次,仍失败则标"该平台问询失败:v2.3 跑批受限"
- 反爬间隔 ≥ 3 秒(默认)
- 截图保留 7 天,过期自动清理(用户可改)

#### Step 2.4:v2.3 抓取能力边界(诚实声明)

- ✅ 豆包 — 用户量最大(4.4 亿月活),爬取最成熟
- ✅ Kimi — 技术向用户,API 爬取成熟
- ✅ 通义千问 — 阿里系,商业覆盖强
- ⚠️ 文心一言 / 腾讯元宝 / 秘塔 — v2.3 未实现爬虫模块(可后续加)
- ❌ ChatGPT / Claude / Gemini — 需海外环境,v2.4 规划
- ⚠️ 平台反爬升级时,v2.3 爬虫可能失效(需更新 selector)

### Step 3:聚合 + 评分

**Step 3.1:品牌出现频次统计**
- 遍历所有 web_search 结果
- 检查 `brand` 字符串是否出现在标题/摘要中
- 命中率 = 出现次数 / 总结果数

**Step 3.2:推荐度评分**(查询词类型加权)
- 推荐型查询词命中 → +3 分(用户在找品牌,被提到说明强推荐)
- 决策型查询词命中 → +2 分(分场景提到,有价值)
- 对比型查询词命中 → +2 分(被拿来对比,说明有竞争力)
- 痛点型查询词命中 → +1 分(被引用为解决方案)

**Step 3.3:4 维子分计算**(0-100)
- **被引用频次**(40%):品牌在所有查询词中出现的平均概率
- **推荐度**(30%):推荐型查询词命中比例
- **内容质量**(20%):引用品牌的网页是否结构化(含数据 / 列表 / 对比表)
- **平台覆盖**(10%):品牌在多少个不同域名/平台上被引用

**Step 3.4:综合分 = 4 维加权**

**Step 3.5:竞品对比**
- 同样的查询词列表,对每个竞品也跑评分
- 输出 5-10 个竞品的综合分 + 4 维子分 + 排名

**Step 3.6:Verdict 自动调整**

| 综合分 | verdict |
|---|---|
| 0-30 | 🔴 红(不可见/低可见) |
| 31-60 | 🟡 黄(中等可见,有空间) |
| 61-100 | 🟢 绿(强可见,保持+扩展) |

### Step 3.7:完整标签系统(Hard Constraint)

每条关键数据必须标 4 个标签。

**标签 1:来源等级(5 级)** — 🏛️ 官方 / 📊 行业 / 📰 媒体 / 🏪 平台 / 👤 UGC。
- 🏛️:品牌官网/上市公司财报/政府文件
- 📊:行业研究机构(中指/克而瑞/艾瑞/QuestMobile)
- 📰:媒体(财经/科技媒体)
- 🏪:平台(百度/知乎/小红书/微信公众号)
- 👤:UGC(用户帖子/评论)
- 多源引用标最高级;UGC 仅辅助参考

**标签 2:置信度(3 级)** — 🟢 高(多源+官方/行业)/ 🟡 中(单源+行业/平台)/ 🔴 低(单源+自媒体/推算)。

**标签 3:推算依据** — 所有 LLM 推算数字标"推算方法 + 依据基准"。

**标签 4:决策可执行性(3 级)** — ✅ 立即可签 / ⚠️ 需现场验证后签 / ❌ 数据不足。

### Step 4:报告渲染

按 `references/report-schema.md` 输出规范渲染 Markdown。

**v2.3 报告头部必加 1 段**(诚实声明):

```markdown
## 数据来源说明(必加)

本报告基于 **v2.3 Playwright + 系统 Chrome 真实模式** 生成。
LLM 调 Python 爬虫真实打开豆包/Kimi/通义 网页,抓真实 LLM 输出。

- ✅ 90%+ 真实平台输出(豆包/Kimi/通义 实际回答)
- ⚠️ 需用户已登录目标平台(cookie 持久化到 ~/.geo-radar-cn/browser-profile-*/)
- ⚠️ 跑批时间 3-12 分钟(看网络 + LLM 速度)
- 🎯 安装:pip install playwright (~10MB,免下 Chromium,复用系统 Chrome)
```

**渲染条件**:

| 章节 | 触发条件 |
|---|---|
| 报告主体 8 节(一-八) | 始终渲染 |
| 附录 A「立即可执行 3 步」 | verdict = 🔴 或 🟡 时触发 |
| 附录 B「数据局限」 | 始终渲染(Hard Requirement) |
| 附录 C「30 天行动清单」 | 始终渲染(可立即打印执行) |
| 数据来源说明(v2.3 新增) | **v2.3 必加,顶部** |
| 数据来源 | 始终渲染 |
| 免责声明 | 始终渲染(Hard Requirement) |

**输出位置**:当前工作目录的 `geo_report_<品牌>_<日期>.md`。

---

## 禁止项清单(违反则报告作废,**Hard Constraints**)

### 主语相关(1-3)
1. 禁止自动延展为其他品牌的可见度测算(主语锁定)
2. 禁止在「建议」里反客为主(「推荐 X 品牌」不能成为主结论)
3. 禁止未要求的多品牌对比 / 跨行业对比

### 内容相关(4-7)
4. 禁止自动加用户未要求的子报告
5. 禁止把竞品对标错位为主语
6. 禁止在主报告字段里做品牌替换
7. 禁止对用户输入做扩展性解读(如"既然你要查 GEO,顺便看下 SEO")

### 表达相关(8-11)
8. 禁止营销味表达(必赚/稳赚/震撼/保姆级/AI 速成)
9. 禁止 AI 套路开场(今天分享/我来聊聊/我帮一个朋友)
10. 禁止把行业级宏观内容当结论(如"2026 年中国 AI 搜索市场 1000 亿"当作品牌可见度结论)
11. 禁止模板化填空(报告里必须有具体数据,不能 8 节全是占位符)

### 数据相关(12-14)
12. 禁止用模型记忆填充(所有数据必须来自本次爬虫问询,或 v2.2 模式下的 LLM 模拟)
13. 禁止编造数据(无来源 URL / 无截图的数字禁止出现)
14. 禁止改动用户输入(用户给的 `brand` / `queries` 不能修改)

---

## 鲁棒性与降级(15 场景)

| 场景 | 行为 |
|---|---|
| **Python 不可用** | 切 v2.2 LLM 模拟(fallback) |
| **Playwright 未装** | 提示 `pip install playwright`,或自动跑 pip install,失败切 v2.2 |
| **Chromium 未下载且无系统 Chrome** | 提示装 Google Chrome / Edge,或 `playwright install chromium`(~200MB) |
| **未登录目标平台** | 跑批前检测 cookie 状态,未登录则报错"请先运行 `python -m crawler.runner --login`",exit 1 |
| **单平台爬虫失败** | 重试 1 次,仍失败则该平台所有结果标"问询失败",其他平台继续;verdict 仍按成功平台算 |
| **单次问询超时(>60s)** | 该次标"超时失败",不计入总成功率;继续下一个 |
| **平台反爬拦截** | 检测页面错误/验证码,标"反爬拦截",报告第 7 节明示,verdict 强制 🟡 |
| **selector 找不到** | 自动 snapshot -i 找新 selector,或提示用户手动报告(已实测 v2.3 selector 是 `textarea[placeholder="发消息..."]`) |
| `references/*.md` 文件缺失 | 仅 1 个文件缺失时,用 SKILL.md 内联规则补足;多个缺失时返回错误并提示用户 |
| `examples/` 缺失 | 不影响 LLM 执行(范本是参考文件),按 SKILL.md + references 仍可渲染报告 |
| 用户用自然语言而非 JSON 输入 | LLM 先解析为 `input_schema`,解析失败字段用 Fallback 规则;解析后向用户确认 1 次(必填 `brand`)即可启动 |
| LLM 输出被 token 限制截断 | 优先完成"主体 8 节 + 摘要卡";附录 A/B/C 与数据来源可分批追加(`## 续 Part 2` 子文件);免责声明 Hard Requirement 不可省略 |
| 县城及以下品牌数据稀缺 | 大量字段标"未找到公开数据"+ 附录 B 明示三线/县城局限 |
| **v2.2 兼容模式** | Python 不可用时自动切;LLM 扮演 3 平台,报告头部明示"v2.2 LLM 模拟" |
| **v1.0 兼容模式** | Python + LLM 模拟都失败时切;LLM 调 web_search 工具,所有引用都标"⚠️ web_search 代理信号" |

---

## 适用范围

**v1.x 中国大陆 only**:
- ✅ 一线 / 新一线 / 二线 / 三线城市(全国性品牌都支持)
- ✅ 8 大内置行业(奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融)
- ✅ 中文输入 / 中文报告
- ⏳ 县城及以下 / 县级市:数据稀缺,大量字段标"未找到公开数据",降级用通用模板
- ❌ 海外城市(港澳台 / 东南亚 / 北美 / 欧洲):v2.4 规划
- ❌ 海外品牌(Starbucks 中国除外):v2.4 规划
- ❌ 其他行业(医疗 / 法律 / 制造业):未在 8 行业 baseline,降级用通用模板(效果下降)

**输入城市检查**:
- LLM 在 Step 0 解析后必须确认 `brand` 在中国境内(基于品牌名常识)
- 不在中国("TikTok""Netflix""Tesla"):verdict 强制 🔴 + verdict_reason 写明"v1.x 不支持海外场景,参见 v2.4 计划"
- 港澳台品牌:verdict 🟡 + verdict_reason 写明"港澳台数据可参考大陆基准,但需额外验证政策差异"

---

## 立即可执行 3 步(优化机会附录 A)

报告渲染完成后,在第 6 节"优化机会清单"末尾固定给出 3 步立即可执行的动作:

1. **去高频引用平台发内容**(基于第 5 节 top 5 平台):知乎回答 / 小红书笔记 / 36氪投稿 / 微信公众号
2. **结构化现有内容**(基于第 5 节"内容质量"子分低的):加 FAQ Schema / 加对比表 / 加统计数据
3. **外链建设**(基于第 5 节"平台覆盖"子分低的):在 5 个高权威域名(36氪/虎嗅/界面/钛媒体/亿欧)上发 PR 稿

每步 4 维评估:**预估成本 / 预期收益 / 风险评估 / 决策可执行性**。

---

## 引用来源标注

报告末尾必须有 `## 数据来源` 章节,每条数据标 3 个字段:
- 来源 URL
- 来源等级(🏛️/📊/📰/🏪/👤)
- 数据时效(🟢/🟡/🟠/🔴)

---

## 免责声明(Hard Requirement)

所有报告必须在末尾追加 `## 免责声明` 章节,4 部分齐全:
- **数据来源说明**:基于 Playwright + 系统 Chrome 真实抓取豆包/Kimi/通义的输出,不构成投资/营销建议
- **使用限制**:本报告不替代专业 GEO 服务;爬虫可能受平台反爬/登录态影响,见第 7 节"数据局限"
- **重要提醒**:v2.3 覆盖国内 3 大 LLM 平台;海外 LLM / 其他国内平台 v2.4 规划;关键决策请咨询 GEO 专业顾问
- **授权与免责**:本 skill 生成的报告仅供参考,作者不对使用结果负责;v2.2 LLM 模拟模式仅作无 Python 环境的 fallback;v1.0 web_search 模式仅作快速预览

---

## 输出自检(Hard Requirement)

报告渲染完成后必须逐项验证,不通过则报告视为不完整。

| 类别 | 检查项 |
|---|---|
| A. 数据来源说明 | 报告头部有"v2.3 Playwright 真实模式" 1 段声明,**Hard Requirement** |
| B. 主语锁定 | 主品牌在摘要卡 ≥1 次;4 维子分基于主品牌;关键执行建议 + 行动清单针对主品牌;其他品牌仅作对标 |
| C. 禁止项 | 无"如果换品牌为 X"完整测算;无跨行业对比;无营销味/AI 套路/模型记忆/改动用户输入 |
| D. 必填项 | 8 节主体;附录 A 触发正确;附录 B 数据局限;附录 C 行动清单;数据来源;免责声明 |
| E. 数据时效 | 报告头部有分布表;🟢+🟡 ≥ 80%;🔴 ≤ 10%;🔴 标"仅作历史参考" |
| F. 标签系统 | 关键数据 100% 来源等级 + 置信度;推算数字 100% 推算依据;关键结论 100% 决策可执行性 |
| G. 品牌可见度分 | 综合分 + 4 维子分都给出;verdict 与综合分一致 |
| H. 竞品对比 | 5-10 个竞品都有综合分 + 排名;主品牌标记 |
| I. 行动清单 | 3 步立即可执行;每步 4 维评估;3-5 条红线(用户绝对不能做) |

**不通过处置**:
- 1-2 项 → 补全/重写对应章节
- 3 项以上 → 报告视为不合格,重新生成
- 数据来源说明缺失 → 必须重写报告(Hard Requirement)
- 主语锁定类不通过 → 必须重写报告
- 数据时效类不通过(🔴 > 10%)→ 必须替换过期数据
- 标签系统类不通过 → 必须补全标签
