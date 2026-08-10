# GEO 雷达 Skill

> **版本**: v2.1.0
> **状态**: ✅ stable
> **简介**: 面向中文用户的 GEO（生成式引擎优化）可见度诊断与优化指引（WorkBuddy 原生版）
> **目录**: `geo-radar-cn__skillhub/`
> **slug**: `geo-radar-cn`

---

## 它做什么

输入你的品牌名,skill 让 **WorkBuddy 里的 LLM 自己用 agent-browser 打开豆包/Kimi/通义**,真实问 20-30 个查询词,统计你的品牌在 AI 回答里的出现频次 / 排名位置 / 推荐度 / 引用源,输出 8 节结构化报告,告诉你"AI 看不看你 + 怎么改进"。

## 跟之前版本的关键差异

| 版本 | 跑批方式 | LLM 角色 | 依赖 |
|---|---|---|---|
| v1.0 | web_search 抓"AI 引用了哪些网页" | 拿间接信号,写报告 | 无 |
| v2.0 | Playwright Python 爬虫 | 拿 JSON,写报告 | playwright + chromium(~200MB) |
| **v2.1** | **agent-browser 让 LLM 自己控制 Chromium** | **自己跑问询 + 抓数据 + 写报告** | **WorkBuddy + agent-browser(自带)** |

## 适用场景

- "我的品牌在豆包/Kimi/通义 里被提到多少"
- "AI 搜索里我的竞品排第几"
- "我应该发什么内容才能被 AI 引用"
- "哪些网站是 AI 反复引用的源头,我要不要去那里发"

## 不适用

- 不在 WorkBuddy 环境(降级到 v2.0 Python 爬虫在 `examples/legacy-v2.0-python-crawler/`)
- 海外英文市场(v2.2 规划)
- 想要 SEO 排名报告(那是 SEO,不是 GEO)

## 输入要求

| 字段 | 必填 | 说明 |
|---|---|---|
| `brand` | ✅ | 品牌名 / 域名 / 产品名 |
| `queries` | ❌ | 目标查询词(缺失时按 category 自动生成 20-30 个) |
| `category` | ❌ | 行业/品类(缺失时 LLM 推断) |
| `competitors` | ❌ | 竞品列表(缺失时 LLM 推断 5-10 个) |

## 运行环境

| 项 | 要求 |
|---|---|
| WorkBuddy | v5.3.11+ |
| agent-browser skill | v1.3.0+(WorkBuddy 官方,可一键装) |
| 各平台登录态 | 首次使用用户手动登录(cookie 持久化) |
| 跑批时间 | 5-25 分钟(20-30 prompts × 3 平台) |

## 快速开始

```bash
# 1. 在 WorkBuddy 装好 agent-browser skill(一次性,~500MB)
npm install -g agent-browser
agent-browser install

# 2. 在 WorkBuddy 浏览器里手动登录豆包/Kimi/通义(一次,cookie 持久化)

# 3. 在 WorkBuddy 对话框输入:
"用 GEO 雷达 skill 分析下蜜雪冰城"
```

## 输出

8 节 Markdown 报告:
1. 摘要卡(综合分 + verdict)
2. 品牌可见度分(4 维子分)
3. 查询词覆盖(20-30 个查询词各自的命中情况)
4. 竞品对比(5-10 个竞品排名)
5. AI 引擎引用源分析(top 5 引用平台)
6. 优化机会清单(3 步立即可执行)
7. 数据局限(诚实声明爬虫/反爬/登录态影响)
8. 行动清单(30 天可执行 + 红线)

## v2.0 Python 爬虫 (CLI 备用)

如果不在 WorkBuddy 环境,降级用 v2.0 Python 爬虫:
- 代码: `examples/legacy-v2.0-python-crawler/`
- 文档: `examples/legacy-v2.0-python-crawler/README.md`
- 适用: 纯 CLI / 沙箱 / CI / 无人值守跑批

## v1.0 web_search (最后 fallback)

如果连浏览器都不想用,降级 v1.0:
- LLM 调自己的 web_search 工具
- 数据是间接信号(~40% 真实 GEO 覆盖)
- 不推荐,仅作快速预览

## 文件结构

```
geo-radar-cn__skillhub/
├── SKILL.md                          # 主入口 (v2.1 WorkBuddy native)
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
│   └── agent-browser-setup.md        # v2.1 agent-browser 集成指南
├── examples/
│   ├── test-run-*.md                 # 报告范本(高/中/低数据)
│   └── legacy-v2.0-python-crawler/   # v2.0 Python 爬虫 CLI 备用
│       ├── README.md
│       ├── scripts/crawler/          # 爬虫代码(doubao/kimi/tongyi/runner)
│       ├── run_mixue_demo.sh         # 蜜雪冰城 demo 脚本
│       └── crawler-setup.md          # v2.0 安装文档
└── tests/
    ├── pattern_checker.py            # 静态模式检查器 (12 节)
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
