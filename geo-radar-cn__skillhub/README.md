# GEO 雷达 Skill

> **版本**: v2.3.0
> **状态**: ✅ stable
> **简介**: 面向中文用户的 GEO（生成式引擎优化）可见度诊断（10MB 装 1 次）
> **目录**: `geo-radar-cn__skillhub/`
> **slug**: `geo-radar-cn`

---

## 它做什么

输入你的品牌名,LLM 调 Python 爬虫用系统 Chrome 真实打开豆包/Kimi/通义,问 20-30 个查询词,统计你的品牌在 AI 真实回答里的出现频次 / 排名 / 推荐度,输出 8 节结构化报告。

## 跟之前版本的关键差异

| 版本 | 跑批方式 | 安装成本 | 持续成本 | 真实度 | 适用 |
|---|---|---|---|---|---|
| v1.0 | web_search 抓"AI 引用了哪些网页" | 0 | 0 | 30-50% | 最后 fallback |
| v2.1 | agent-browser 真实打开豆包/Kimi/通义 | 50-500MB | 0 | 90%+ | WorkBuddy Power User |
| v2.2 | LLM 模拟 3 平台 | 0 | 0 | 60-80% | 无 Python 环境 fallback |
| **v2.3** | **Playwright + 系统 Chrome 真实抓** | **10MB** | **0** | **90%+** | **默认** |

**v2.3 关键设计**:
- 用 Playwright Python 包(10MB),不下载 Chromium(免 200MB)
- 复用系统已装的 Google Chrome
- 跑一次,cookie 持久化,永久免登录

## 适用场景

- "我的品牌在豆包/Kimi/通义里被提到多少"
- "AI 搜索里我的竞品排第几"
- "我应该发什么内容才能被 AI 引用"
- "哪些网站是 AI 反复引用的源头,要不要去那里发"

## 不适用

- AI 平台不支持 Python 执行(自动降级 v2.2 LLM 模拟)
- 海外英文市场(v2.4 规划)
- 想要 SEO 排名报告(那是 SEO,不是 GEO)

## 输入要求

| 字段 | 必填 | 说明 |
|---|---|---|
| `brand` | ✅ | 品牌名 / 域名 / 产品名 |
| `queries` | ❌ | 目标查询词(缺失时按 category 自动生成 20-30 个) |
| `category` | ❌ | 行业/品类(缺失时 LLM 推断) |
| `competitors` | ❌ | 竞品列表(缺失时 LLM 推断 5-10 个) |
| `mode` | ❌ | 模式选择(v2.3-playwright / v2.2-llm-roleplay / v2.1-agent-browser / v1.0-web-search,默认 v2.3) |

## 运行环境

| 项 | 要求 |
|---|---|
| Python | 3.10+ (系统已有) |
| Playwright | `pip install --user --break-system-packages playwright` (~10MB) |
| Chromium | **不下载**,复用系统 Chrome (Mac: `/Applications/Google Chrome.app/`) |
| 各平台登录态 | 首次使用用户手动登录(cookie 持久化 30 天) |
| 跑批时间 | 3-12 分钟 (20-30 prompts × 3 平台) |
| **总安装成本** | **10MB,5-10 秒装好,永久用** |

## 快速开始

在 WorkBuddy / MiniMax Code / Cursor 等支持 Python 的 AI 平台:

```bash
# 1. 一次性安装(10MB,5-10 秒)
pip install --user --break-system-packages playwright

# 2. 首次使用:用户手动登录各平台
cd /path/to/geo-radar-cn__skillhub
python3 -m crawler.runner --login
# 浏览器自动打开,用户在每个 tab 登录豆包/Kimi/通义,完成后按 Enter
# cookie 持久化 30 天,后续免登录

# 3. 跑批
python3 -m crawler.runner \
  --brand "蜜雪冰城" \
  --auto-prompts \
  --category 奶茶 \
  --use-system-chrome \
  --output json

# 4. 报告位置
ls ~/.geo-radar-cn/reports/
# → geo_report_蜜雪冰城_20260810-203000.json + .md
```

在 Claude.ai / ChatGPT 网页版(无 Python):

```
"用 GEO 雷达 skill 分析下蜜雪冰城"
```

LLM 会自动降级到 v2.2 LLM 模拟模式(60-80% 真实度,0 安装)。

## 三种模式自动切换

LLM 在跑批前自动检测 + 选择:

| 模式 | 触发条件 | 真实度 | 安装 |
|---|---|---|---|
| **v2.3 Playwright**(默认) | AI 平台支持 Python + Playwright 已装 + 系统 Chrome 存在 | 90%+ | 10MB |
| v2.2 LLM 模拟(fallback) | AI 平台无 Python / Playwright 未装 | 60-80% | 0 |
| v2.1 agent-browser(Power User) | 用户说"用 agent-browser 模式" + WorkBuddy | 90%+ | 50-500MB |
| v1.0 web_search(最后 fallback) | 上述都失败 | 30-50% | 0 |

## 输出

8 节 Markdown 报告 + 头部数据来源声明(v2.3 Hard Requirement):

1. 摘要卡(综合分 + verdict + 3 句话结论 + 关键数字 + 数据来源声明)
2. 品牌可见度分(4 维子分)
3. 查询词覆盖(20-30 个查询词各自的命中情况)
4. 竞品对比(5-10 个竞品排名)
5. AI 引擎引用源分析(top 5 引用平台)
6. 优化机会清单(3 步立即可执行)
7. 数据局限(诚实声明爬虫/反爬/登录态影响)
8. 行动清单(30 天可执行 + 红线)

## 文件结构

```
geo-radar-cn__skillhub/
├── SKILL.md                          # 主入口 v2.3 (Playwright + 系统 Chrome)
├── skill.json                        # skill 元数据
├── CHANGELOG.md                      # 变更日志
├── README.md                         # 本文件
├── skill-card.md                     # 商店展示卡
├── _meta.json / _skillhub_meta.json  # skillhub 平台元数据
├── icon.png                          # 1024×1024 封面
├── references/
│   ├── query-templates.md            # 8 行业 × 4 类型查询词模板
│   ├── report-schema.md              # 8 节报告 schema
│   ├── web-search-prompts.md         # v1.0 web_search prompts
│   ├── llm-test-prompts.md           # v2.x LLM 测试 prompts
│   ├── chaos-cases.md                # 混沌测试案例
│   ├── mode-v22-llm-roleplay.md      # v2.2 fallback 文档
│   ├── mode-v21-agent-browser.md     # v2.1 Power User 文档
│   └── mode-v10-web-search.md        # v1.0 最后 fallback 文档
├── scripts/
│   └── crawler/                      # v2.3 爬虫主路径
│       ├── __init__.py
│       ├── doubao.py                 # 豆包爬虫
│       ├── kimi.py                   # Kimi 爬虫
│       ├── tongyi.py                 # 通义千问爬虫
│       └── runner.py                 # GEORunner 批量跑批
├── examples/
│   ├── test-run-*.md                 # 报告范本
│   └── run_mixue_demo.sh             # 蜜雪冰城 demo 脚本
└── tests/
    ├── pattern_checker.py            # 静态模式检查器
    ├── chaos/                        # 混沌测试
    ├── llm_runner.py                 # LLM mock 测试
    └── output_checker.py             # 输出质量检查
```

## CI 套件

```bash
python3 tests/pattern_checker.py     # 静态结构 + 内容 + 标签
python3 tests/chaos/                 # 混沌场景
python3 tests/output_checker.py      # 输出质量
python3 tests/llm_runner.py          # LLM mock
```

## 变更日志

详见 `CHANGELOG.md`。
