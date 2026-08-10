# v2.1 agent-browser 真实模式 (WorkBuddy Power User 高级玩法)

> **状态**:可选高级模式。**v2.3 Playwright + 系统 Chrome 是默认**(10MB 装 1 次,跨平台)。
> 本模式仅在 WorkBuddy 用户明确要"用 agent-browser"时启用,且只在 WorkBuddy + agent-browser 环境跑得通。

## 何时切到 v2.1

LLM 在跑批前检测:
- 用户说"用 agent-browser 模式" / "我要 agent-browser"
- AI 平台 = WorkBuddy
- `agent-browser --version` 通过

满足以上 3 个条件,LLM 切到 v2.1 模式并提示用户:

```
[检测到] 用户要 agent-browser 模式 + WorkBuddy 环境
[切到]   v2.1 agent-browser 模式
[需要]   npm install -g agent-browser (50MB) + agent-browser install (500MB Chromium)
[需要]   用户手动登录豆包/Kimi/通义
[预计]   5-25 分钟跑批
```

## agent-browser 安装

```bash
# macOS / Linux
npm install -g agent-browser
agent-browser install    # 下载 Chromium ~500MB
```

## 关键命令(给 LLM 看)

| 命令 | 用途 |
|---|---|
| `agent-browser open <url>` | 打开 URL(自动启 daemon) |
| `agent-browser wait --load load` | 等首屏(用 load 而非 networkidle) |
| `agent-browser snapshot -i` | 抓带 element ID 的页面 |
| `agent-browser type <selector> <text>` | 输入 |
| `agent-browser press <key>` | 按键(Enter 发送) |
| `agent-browser snapshot` | 抓页面文本 |
| `agent-browser screenshot --path <file>` | 截图 |
| `agent-browser close` | 关闭 daemon(所有任务完成后) |

## Session 模型

- daemon 启动后保持
- 中途 `open` 同 URL 不会重开
- 多步骤任务用同一 daemon,只在最后 `close`
- cookie/login state 跨命令保留

## 平台 URL 与 selector

| 平台 | URL | 输入框 selector |
|---|---|---|
| 豆包 Doubao | `https://www.doubao.com/chat/` | `textarea[placeholder="发消息..."]` |
| Kimi 月之暗面 | `https://kimi.moonshot.cn/` | `div[contenteditable="true"]` |
| 通义千问 | `https://tongyi.aliyun.com/qianwen/` | `textarea[placeholder*="输入"]` |

**不要硬编码 selector** — 用 `snapshot -i` 看到真实 DOM,自己提取。

## 单次问询序列

```bash
# 1. 打开 platform
agent-browser open https://www.doubao.com/chat/

# 2. 等首屏
agent-browser wait --load load

# 3. 找输入框
agent-browser snapshot -i
# LLM 从输出找 textarea 或 contenteditable div,记下 selector

# 4. 输入 prompt
agent-browser type "textarea[placeholder='发消息...']" "推荐 2025 奶茶品牌"

# 5. 按 Enter 发送
agent-browser press "Enter"

# 6. 轮询等回答完成(LLM 自己做,30 秒超时)
# 7. 抓最终回答
agent-browser snapshot

# 8. 截图留档
agent-browser screenshot --path ~/.geo-radar-cn/screenshots/doubao_001.png

# 9. 反爬间隔
sleep(3)
```

## 报告头部必加声明

```markdown
## 数据来源说明(v2.1)

本报告基于 **v2.1 agent-browser 真实模式** 生成。
LLM 调 agent-browser 真实打开豆包/Kimi/通义 网页,抓真实 LLM 输出。

- ✅ 100% 真实平台输出(豆包/Kimi/通义 实际回答)
- ⚠️ 需用户已登录目标平台(cookie 持久化到 agent-browser daemon)
- ⚠️ 跑批时间 5-25 分钟(看网络 + LLM 速度)
- 🎯 跑批需 ~500MB Chromium(agent-browser install)
```

## 模式对比(总结)

| 维度 | v2.3 Playwright + 系统 Chrome (默认) | v2.1 agent-browser (Power User) |
|---|---|---|
| 安装成本 | 10MB (复用系统 Chrome) | 50-500MB |
| 真实度 | 90%+ | 90%+ |
| 跨 AI 平台 | ⚠️ WorkBuddy/MiniMax Code/Cursor | ❌ 仅 WorkBuddy |
| 跑批时间 | 3-12 分钟 | 5-25 分钟 |
| 登录需求 | 用户手动登录(1 次) | 用户手动登录(1 次) |
| 上架策略 | 默认 | Power User 高级玩法 |
