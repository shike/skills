---
name: GEO 雷达 v2.1：基于 agent-browser 的多 LLM 引擎可见度真实诊断（WorkBuddy 原生）
version: 2.1.0
description: |
  面向中文用户的 GEO（生成式引擎优化）可见度诊断 skill。
  v2.1 核心：通过 WorkBuddy 内置的 agent-browser skill（vercel-labs/agent-browser CLI）
  直接打开豆包/Kimi/通义网页,输入 prompt,抓真实 LLM 输出(文本+截图+引用源),
  分析品牌在 AI 回答中的出现频次 / 排名位置 / 推荐度。
  v2.0 的 Playwright Python 爬虫降为 CLI 备用(放 examples/legacy-v2.0-python-crawler/)。
  v1.0 web_search 代理模式保留为最后 fallback(数据是间接信号,不推荐使用)。
  输入品牌名(必填)+ 目标查询词(可选)+ 行业/竞品(可选),
  输出 8 节结构化报告(摘要卡 / 品牌可见度分 / 查询词覆盖 /
  竞品对比 / 引用源分析 / 优化机会 / 数据局限 / 行动清单)。
entry: SKILL.md
runtime: llm
requiredSkills:
  - agent-browser  # WorkBuddy 官方 v1.3.0+,让 LLM 直接控制 Chromium
tags:
  - GEO
  - AI 搜索
  - 品牌可见度
  - 生成式引擎优化
  - LLM 引用
  - 内容优化
  - 竞品分析
  - 真实 LLM 输出
  - agent-browser
  - WorkBuddy 原生
---

# GEO 雷达 v2.1 · Skill 主入口（WorkBuddy 原生版）

> **核心能力(v2.1)**:输入品牌名 → 自动生成查询词(可选) → **LLM 调用 agent-browser 直接打开豆包/Kimi/通义真实问询** → 输出 8 节结构化报告
>
> **v2.1 vs v2.0 vs v1.0 关键差异**:
> | 版本 | 核心方式 | LLM 角色 | 依赖 |
> |---|---|---|---|
> | v1.0 | web_search 抓"AI 引用了哪些网页" | 拿间接数据,写报告 | 无 |
> | v2.0 | Playwright Python 爬虫 | 拿 JSON 数据,写报告 | playwright + chromium(~200MB) |
> | **v2.1** | **agent-browser 让 LLM 自己控制 Chromium** | **自己跑问询 + 抓数据 + 写报告** | **agent-browser(WorkBuddy 自带)** |
>
> **能力边界**:v2.1 依赖 WorkBuddy + agent-browser skill;详见"运行环境要求"。
> **诚实声明**:报告基于真实 LLM 输出,但可能受反爬/登录态影响,详见第 7 节"数据局限"。

---

## 适用场景

- "我的品牌在豆包/Kimi/文心/ChatGPT 里被提到多少"
- "AI 搜索里我的竞品排第几"
- "我应该发什么内容才能被 AI 引用"
- "哪些网站是 AI 反复引用的源头,要不要去那里发"
- "我的内容在 Google AI Overview 里出现率多少"

## 不适用

- 想要 SEO 排名报告(那是 SEO,不是 GEO)
- 海外英文市场(v2.2 规划)
- 行业不在 8 行业模板内且用户不输入 `category`(降级通用模板,效果下降)
- 不在 WorkBuddy 环境下运行(降级用 v2.0 Python 爬虫或 v1.0 web_search)

## 运行环境要求(v2.1 关键)

| 项 | 要求 | 检查命令 |
|---|---|---|
| WorkBuddy 桌面客户端 | v5.3.11+ (Electron 37+,已验证) | `ls /Applications/WorkBuddy.app` |
| agent-browser skill | v1.3.0+ | `agent-browser --version` |
| Node.js 18+ | WorkBuddy 自带 | `node --version` |
| Chromium ~500MB | agent-browser install 自动装 | `~/.cache/ms-playwright/` |
| 各平台登录态 | **首次使用**:用户手动在 WorkBuddy 浏览器里登录豆包/Kimi/通义,cookie 通过 agent-browser daemon 持久化,后续免登录 | 检查 `~/.workbuddy/app/session/Partitions/` |
| 跑批时间 | 20-30 prompts × 3 平台 = 60-90 次问询,LLM 自主执行,约 **5-20 分钟**(看 LLM 速度) | — |
| 反爬间隔 | 每次问询间 3-5 秒(LLM 自己 sleep) | — |
| 国内环境 | 必须,海外 LLM 平台不在 v2.1 范围 | — |

**WorkBuddy 内 agent-browser 缺失?** 提示用户:
```bash
# 一次性安装(约 5-10 分钟,~500MB Chromium)
npm install -g agent-browser
agent-browser install

# 装好后 WorkBuddy 重启,自动识别 agent-browser skill
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

### Step 1:LLM 调用 agent-browser 跑真实问询(v2.1 核心)

**这是 v2.1 的核心步骤** — LLM 自身作为"用户",用 agent-browser 模拟真实操作浏览器,问豆包/Kimi/通义,拿真实 LLM 输出。

#### Step 1.0:前置检查

```bash
# 1. 验证 agent-browser 可用
agent-browser --version
# 期望输出 1.3.0+;如果 command not found,提示用户安装(见"运行环境要求")

# 2. 启动一次 browser daemon,确认无环境错误
agent-browser open https://www.doubao.com/chat/
agent-browser close
# 如果这一步失败,检查 references/agent-browser-setup.md 的 troubleshooting
```

#### Step 1.1:跑批总流程(LLM 执行)

对每个平台 × 每个 prompt,LLM 执行以下子流程:

```
对 platform in [豆包, Kimi, 通义]:
    1. agent-browser open <platform_url>           # 打开平台
    2. agent-browser wait --load load               # 等首屏
    3. agent-browser snapshot -i                    # 找输入框 element ID

    对 prompt in prompts:
        4. agent-browser type <input_selector> "<prompt>"   # 输入
           # selector 推荐: textarea[placeholder*="发消息"] / div[contenteditable="true"]
           # LLM 第一次用 snapshot -i 看到真实 selector

        5. agent-browser snapshot -i                          # 找"发送"按钮
           # 优先按 Enter(更稳),找不到按钮时降级到 Enter

        6. 用 Enter 键发送(或 click 发送按钮)

        7. 轮询等回答完成(LLM 自己做):
           prev_len = -1; stable_count = 0
           for _ in range(20):                                # 最多 60 秒
               sleep(3)
               current = agent-browser snapshot                # 抓页面文本
               current_text = extract_assistant_message(current)  # LLM 提取最新回答
               if len(current_text) == prev_len and len(current_text) > 10:
                   stable_count += 1
                   if stable_count >= 2: break                 # 稳定 2 次
               else:
                   stable_count = 0
               prev_len = len(current_text)

        8. agent-browser snapshot                              # 抓最终回答
           text = extract_assistant_message(snapshot)
           # 提取引用源:LLM 找 snapshot 里所有 a[href*="//"] 的链接

        9. agent-browser screenshot                            # 留档(写到 ~/.geo-radar-cn/screenshots/<platform>_<n>.png)

        10. 记录 result:
            {platform, prompt, text, citations, screenshot_path, duration_sec, success}

        11. sleep(3)                                           # 反爬间隔

    # 12. 不需要 close!保留 daemon 给下一个 platform 用
# 13. 所有 platform 跑完, agent-browser close
```

#### Step 1.2:平台 URL + 输入框选择器参考表

| 平台 | URL | 输入框典型 selector | 发送方式 |
|---|---|---|---|
| 豆包 Doubao | `https://www.doubao.com/chat/` | `textarea[placeholder="发消息..."]` | 按 Enter |
| Kimi 月之暗面 | `https://kimi.moonshot.cn/` | `div[contenteditable="true"]` 或 `textarea` | 按 Enter |
| 通义千问 | `https://tongyi.aliyun.com/qianwen/` | `textarea[placeholder*="输入"]` | 按 Enter |

**重要**:**不要硬编码 selector**。LLM 第一步用 `agent-browser snapshot -i` 看到真实 DOM,自己提取 selector。selector 可能改。

#### Step 1.3:每次问询抓取的数据(LLM 内部维护)

LLM 维护一个 results 列表(类似 v2.0 的 JSON schema):
```json
{
  "platform": "doubao",
  "prompt": "推荐 2025 平价奶茶品牌",
  "text": "<完整 LLM 回答文本>",
  "citations": [{"title": "...", "url": "https://..."}],
  "screenshot_path": "~/.geo-radar-cn/screenshots/doubao_001.png",
  "duration_sec": 12.4,
  "success": true
}
```

#### Step 1.4:跑批规模与时间预估

- 默认:**20-30 prompts × 3 平台 = 60-90 次问询**
- 每次问询平均 10-20 秒(含打字/等回答/snapshot)
- 反爬间隔 3 秒
- **总跑批时间: 5-20 分钟**(看 LLM 速度 + 平台响应)
- 截图保留 7 天(LLM 自己清理)

#### Step 1.5:关键约束

- **禁止用模型记忆填充**:所有 data 必须来自真实问询
- **回答失败重试 1 次**:仍失败标"该平台问询失败",其他继续
- **反爬间隔 ≥ 3 秒**:LLM 每次问询后 sleep(3)
- **截图留档**:每次问询留 1 张,放 `~/.geo-radar-cn/screenshots/`
- **session 复用**:同一 platform 多 prompt 用同一 daemon,不 close 中间
- **final close**:所有 platform 跑完才 `agent-browser close`

#### Step 1.6:v2.1 抓取能力边界(诚实声明)

- ✅ 豆包 — 用户量最大(4.4 亿月活),最成熟
- ✅ Kimi — 技术向用户,成熟
- ✅ 通义千问 — 阿里系,商业覆盖强
- ⚠️ 文心一言 / 腾讯元宝 / 秘塔 — v2.1 未实现(可后续加,流程一样)
- ❌ ChatGPT / Claude / Gemini — 需海外环境,v2.2 规划
- ⚠️ 平台反爬升级时,LLM 自己适应(DOM 变化时 snapshot -i 重新找 selector)
- ⚠️ 平台要求强制登录(没登录直接 redirect 到 ?from_logout=1)— 跑批前 LLM 检测登录态,未登录 → 报错

#### Step 1.7:登录态检测与降级(关键)

跑批前 LLM 主动检测:
```bash
agent-browser open https://www.doubao.com/chat/
sleep(2)
snapshot = agent-browser snapshot
# LLM 判断:
#   - snapshot 含 "登录" 按钮 + URL 是 /chat/ → 未登录
#   - snapshot 含 "有什么我能帮你的吗" + 无 "登录" 按钮 → 已登录
#   - URL 含 ?from_logout=1 → 未登录
```

**未登录时**:
- **不要自动尝试登录**(不安全,可能触发风控)
- **明确告知用户**:请在 WorkBuddy 浏览器里手动登录豆包/Kimi/通义
- 用户登录后,cookie 通过 agent-browser daemon 持久化,自动生效
- 重试跑批

**降级路径**(用户拒绝/不能登录时):
- 平台 A 未登录 → 跳过该平台,只跑 B/C
- 全部未登录 → 报告顶部明示"v2.1 跑批受限:无登录态,降级 v1.0 web_search 代理"

#### Step 1.8:CLI 备用方案(v2.0 Python 爬虫)

如果用户不在 WorkBuddy 跑(纯 CLI / 沙箱环境),降级用 v2.0:
- 代码在 `examples/legacy-v2.0-python-crawler/`
- 文档在 `examples/legacy-v2.0-python-crawler/README.md`
- 适用:CI 自动化 / 无 GUI 服务器 / 纯 CLI 用户
- 限制:同 v2.0(selector 硬编码,DOM 改要改代码)

#### Step 1.9:v1.0 web_search 模式(最后 fallback)

如果用户连 agent-browser 都不想用(纯对话场景),降级 v1.0:
- 用 LLM 自己的 web_search 工具抓"AI 引用了哪些网页"
- 数据是间接信号(不是真实 LLM 输出,**不推荐**)
- 报告顶部明示"⚠️ v1.0 web_search 代理模式,非真实 LLM 输出"

### Step 2:聚合 + 评分

**Step 2.1:品牌出现频次统计**
- 遍历所有 results
- 检查 `brand` 字符串是否在 text 中出现
- 命中率 = 出现次数 / 有效结果数

**Step 2.2:推荐度评分**(查询词类型加权)
- 推荐型查询词命中 → +3 分(用户在找品牌,被提到说明强推荐)
- 决策型查询词命中 → +2 分(分场景提到,有价值)
- 对比型查询词命中 → +2 分(被拿来对比,说明有竞争力)
- 痛点型查询词命中 → +1 分(被引用为解决方案)

**Step 2.3:4 维子分计算**(0-100)
- **被引用频次**(40%):品牌在所有查询词中出现的平均概率
- **推荐度**(30%):推荐型查询词命中比例
- **内容质量**(20%):回答里包含结构化数据(列表/对比表/数据)/引用权威源
- **平台覆盖**(10%):品牌在多少个不同平台/域名上被引用

**Step 2.4:综合分 = 4 维加权**

**Step 2.5:竞品对比**
- 同样的 queries,对每个竞品也跑评分
- 输出 5-10 个竞品的综合分 + 4 维子分 + 排名

**Step 2.6:Verdict 自动调整**

| 综合分 | verdict |
|---|---|
| 0-30 | 🔴 红(不可见/低可见) |
| 31-60 | 🟡 黄(中等可见,有空间) |
| 61-100 | 🟢 绿(强可见,保持+扩展) |

### Step 2.7:完整标签系统(Hard Constraint)

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

### Step 3:报告渲染

按 `references/report-schema.md` 输出规范渲染 Markdown。

**渲染条件**:

| 章节 | 触发条件 |
|---|---|
| 报告主体 8 节(一-八) | 始终渲染 |
| 附录 A「立即可执行 3 步」 | verdict = 🔴 或 🟡 时触发 |
| 附录 B「数据局限」 | 始终渲染(Hard Requirement) |
| 附录 C「30 天行动清单」 | 始终渲染(可立即打印执行) |
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
12. 禁止用模型记忆填充(所有数据必须来自本次真实问询,或 v1.0 模式下的 web_search)
13. 禁止编造数据(无来源 URL / 无截图的数字禁止出现)
14. 禁止改动用户输入(用户给的 `brand` / `queries` 不能修改)

---

## 鲁棒性与降级(13 场景)

| 场景 | 行为 |
|---|---|
| **agent-browser 未装** | LLM 跑 Step 1.0 检测 `agent-browser --version` 失败,提示用户安装命令,降级到 v2.0 Python 爬虫(examples/)或 v1.0 web_search |
| **未登录目标平台** | 跑批前 snapshot 检测登录态,未登录 → 提示用户手动登录,不自动登录 |
| **Chromium 未下载** | 提示 `agent-browser install`,exit |
| **agent-browser daemon 启动失败** | snapshot -i 失败,检查 Node.js 18+ 和 references/agent-browser-setup.md 的 troubleshooting |
| **单平台爬虫失败** | 重试 1 次,仍失败则该平台所有结果标"问询失败",其他平台继续;verdict 仍按成功平台算 |
| **单次问询超时(>60s)** | 轮询 20 次 × 3 秒仍不稳定,标"超时失败",不计入总成功率;继续下一个 |
| **平台反爬拦截** | 检测页面错误/验证码,标"反爬拦截",报告第 7 节明示,verdict 强制 🟡 |
| **selector 找不到** | snapshot -i 找不到输入框,LLM 重新看 DOM 找新 selector;仍失败 → 跳过该 platform,提示用户 |
| `references/*.md` 文件缺失 | 仅 1 个文件缺失时,用 SKILL.md 内联规则补足;多个缺失时返回错误并提示用户 |
| `examples/` 缺失 | 不影响 LLM 执行(范本是参考文件),按 SKILL.md + references 仍可渲染报告 |
| 用户用自然语言而非 JSON 输入 | LLM 先解析为 `input_schema`,解析失败字段用 Fallback 规则;解析后向用户确认 1 次(必填 `brand`)即可启动 |
| LLM 输出被 token 限制截断 | 优先完成"主体 8 节 + 摘要卡";附录 A/B/C 与数据来源可分批追加(`## 续 Part 2` 子文件);免责声明 Hard Requirement 不可省略 |
| 县城及以下品牌数据稀缺 | 大量字段标"未找到公开数据"+ 附录 B 明示三线/县城局限 |
| **v2.0 Python 爬虫模式** | 用户不在 WorkBuddy → 提示看 `examples/legacy-v2.0-python-crawler/README.md` |
| **v1.0 web_search 兼容模式** | 用户拒绝用浏览器 → 用 LLM 自己的 web_search 工具(快速但不准),所有引用都标"⚠️ web_search 代理信号,非真实 LLM 输出" |

---

## 适用范围

**v1.x 中国大陆 only**:
- ✅ 一线 / 新一线 / 二线 / 三线城市(全国性品牌都支持)
- ✅ 8 大内置行业(奶茶 / 咖啡 / 餐饮 / SaaS / 教育 / 旅游 / 电商 / 金融)
- ✅ 中文输入 / 中文报告
- ⏳ 县城及以下 / 县级市:数据稀缺,大量字段标"未找到公开数据",降级用通用模板
- ❌ 海外城市(港澳台 / 东南亚 / 北美 / 欧洲):v2.2 规划
- ❌ 海外品牌(Starbucks 中国除外):v2.2 规划
- ❌ 其他行业(医疗 / 法律 / 制造业):未在 8 行业 baseline,降级用通用模板(效果下降)

**输入城市检查**:
- LLM 在 Step 0 解析后必须确认 `brand` 在中国境内(基于品牌名常识)
- 不在中国("TikTok""Netflix""Tesla"):verdict 强制 🔴 + verdict_reason 写明"v1.x 不支持海外场景,参见 v2.2 计划"
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
- **数据来源说明**:基于 agent-browser 真实问询豆包/Kimi/通义的输出,不构成投资/营销建议
- **使用限制**:本报告不替代专业 GEO 服务;爬虫可能受平台反爬/登录态影响,见第 7 节"数据局限"
- **重要提醒**:v2.1 覆盖国内 3 大 LLM 平台;海外 LLM / 其他国内平台 v2.2 规划;关键决策请咨询 GEO 专业顾问
- **授权与免责**:本 skill 生成的报告仅供参考,作者不对使用结果负责;v1.0 web_search 模式仅作快速预览,数据是间接信号;v2.0 Python 爬虫仅作 CLI 备用

---

## 输出自检(Hard Requirement)

报告渲染完成后必须逐项验证,不通过则报告视为不完整。

| 类别 | 检查项 |
|---|---|
| A. 主语锁定 | 主品牌在摘要卡 ≥1 次;4 维子分基于主品牌;关键执行建议 + 行动清单针对主品牌;其他品牌仅作对标 |
| B. 禁止项 | 无"如果换品牌为 X"完整测算;无跨行业对比;无营销味/AI 套路/模型记忆/改动用户输入 |
| C. 必填项 | 8 节主体;附录 A 触发正确;附录 B 数据局限;附录 C 行动清单;数据来源;免责声明 |
| D. 数据时效 | 报告头部有分布表;🟢+🟡 ≥ 80%;🔴 ≤ 10%;🔴 标"仅作历史参考" |
| E. 标签系统 | 关键数据 100% 来源等级 + 置信度;推算数字 100% 推算依据;关键结论 100% 决策可执行性 |
| F. 品牌可见度分 | 综合分 + 4 维子分都给出;verdict 与综合分一致 |
| G. 竞品对比 | 5-10 个竞品都有综合分 + 排名;主品牌标记 |
| H. 行动清单 | 3 步立即可执行;每步 4 维评估;3-5 条红线(用户绝对不能做) |

**不通过处置**:
- 1-2 项 → 补全/重写对应章节
- 3 项以上 → 报告视为不合格,重新生成
- 主语锁定类不通过 → 必须重写报告
- 数据时效类不通过(🔴 > 10%)→ 必须替换过期数据
- 标签系统类不通过 → 必须补全标签
