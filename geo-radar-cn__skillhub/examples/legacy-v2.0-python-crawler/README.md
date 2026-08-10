# v2.0 Playwright Python 爬虫（CLI 备用方案）

> **状态**:**已弃用**。v2.1 (WorkBuddy native + agent-browser) 是推荐方案。本目录代码保留作 CLI / 沙箱 / CI 自动化环境下的**备用方案**。

## 何时用这个

| 场景 | 用 v2.1 (推荐) | 用 v2.0 (本目录) |
|---|---|---|
| WorkBuddy 桌面交互 | ✅ | ❌ |
| 纯 CLI / 服务器 | ❌ | ✅ |
| 沙箱 / CI 自动化 | ❌ | ✅ |
| 无 GUI 环境 | ❌ | ✅ |
| 跑批需要可重复 / 无人值守 | ⚠️ (LLM 驱动,可能慢) | ✅ (Python 脚本,可 cron) |
| 鲁棒性 | ✅ (LLM 适应 DOM 变化) | ⚠️ (selector 硬编码) |

## 跟 v2.1 的关键差异

| 维度 | v2.0 Python 爬虫 | v2.1 agent-browser |
|---|---|---|
| 驱动方式 | Python 脚本 (Playwright) | LLM 调 agent-browser CLI |
| Selector 维护 | 硬编码(改 DOM 需改代码) | LLM 自动 snapshot -i 适配 |
| 报告生成 | Python 写 JSON + MD | LLM 自己写 |
| 部署 | `pip install playwright + chromium`(~200MB) | WorkBuddy + `npm install -g agent-browser`(~500MB) |
| 跑批时间 | 3-12 分钟(脚本) | 5-25 分钟(LLM) |
| 登录态 | Playwright persistent context | agent-browser daemon |

## 文件结构

```
examples/legacy-v2.0-python-crawler/
├── README.md               # 本文件
├── scripts/
│   └── crawler/            # 爬虫代码(从 v2.0 搬过来)
│       ├── __init__.py
│       ├── doubao.py       # 豆包爬虫
│       ├── kimi.py         # Kimi 爬虫
│       ├── tongyi.py       # 通义千问爬虫
│       └── runner.py       # 批量跑批 + 报告生成
├── run_mixue_demo.sh       # 一键跑批脚本(蜜雪冰城示例)
└── crawler-setup.md        # v2.0 时的安装文档
```

## 快速开始(CLI 环境)

```bash
# 1. 安装依赖
pip install --user --break-system-packages playwright
playwright install chromium  # ~200MB

# 2. 首次: 手动登录各平台
cd /path/to/geo-radar-cn__skillhub
python -m examples.legacy-v2.0-python-crawler.scripts.crawler.runner --login
# 浏览器自动打开,用户在每个 tab 登录,完成后按 Enter
# cookie 保存到 ~/.geo-radar-cn/browser-profile-{platform}/

# 3. 跑批
python -m examples.legacy-v2.0-python-crawler.scripts.crawler.runner \
  --brand "蜜雪冰城" \
  --auto-prompts \
  --category 奶茶 \
  --output json

# 4. 报告位置
ls ~/.geo-radar-cn/reports/
# → geo_report_蜜雪冰城_20260810-201200.json + .md
```

## 关键约束(同 v2.1)

- ✅ 必须登录目标平台(未登录 redirect 到 ?from_logout=1)
- ✅ 截图留档(每次问询 1 张)
- ✅ 反爬间隔 ≥ 3 秒
- ✅ 不支持文心/元宝/秘塔(只支持豆包/Kimi/通义)

## 已知限制

1. **selector 硬编码**:2026-08-10 实测验证 selector 是
   - 豆包输入框: `textarea[placeholder="发消息..."]`
   - 豆包发送: 按 Enter
   - Kimi/通义: 类似,但 LLM 自动检测更稳

2. **PEP 668 (externally-managed-environment)**:macOS Homebrew Python 装 playwright 需要 `--break-system-packages` 或用 `uv venv`

3. **chromium-1234 下载慢**:沙箱 187MB 卡在 0%。可改用系统 Chrome(已合并到 v2.1 的 `use_system_chrome=True` 参数,但 v2.0 的代码默认走 playwright 自带)

4. **登录必须 GUI**:CLI 服务器没 GUI,首次登录得在有 GUI 的机器上做,然后把 `~/.geo-radar-cn/browser-profile-*/` 同步过去

## 推荐: 升级到 v2.1

如果你不是必须用 CLI,推荐升级到 v2.1:
- 0 Python 依赖(WorkBuddy 自带)
- selector 自适应(LLM 找)
- 报告 LLM 自己写(质量更高)
- 跟 WorkBuddy 生态融合

v2.1 入口:`../SKILL.md` (主 SKILL.md)

## 历史背景

- v2.0 (2026-08-10): Playwright Python 爬虫首发
- v2.1 (2026-08-10): WorkBuddy + agent-browser 重构,本目录降为 CLI 备用
