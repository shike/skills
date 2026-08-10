# agent-browser 安装与跑批指南（v2.1）

> v2.1 的核心：让 LLM 自身调用 agent-browser 模拟用户在浏览器里操作,问豆包/Kimi/通义。
> 本文件给 LLM(WorkBuddy) 看,告诉它怎么一步步调用 agent-browser。

## 1. 前置检查

LLM 在跑批前必须先做 3 个检查:

```bash
# 检查 1: agent-browser 是否已装
agent-browser --version
# 期望: 1.3.0+ (WorkBuddy v5.3.11+ 默认带)
# 失败: command not found → 进入第 2 步安装

# 检查 2: Node.js 是否可用
node --version
# 期望: 18+
# 注意: node -e "console.log('ok')" 必须能跑(不只是 print version)

# 检查 3: Chromium 是否已下(~500MB)
ls ~/.cache/ms-playwright/ 2>/dev/null | head -5
# 期望: 看到 chromium-xxxx 目录
# 失败: 空 → 进入第 2 步安装
```

## 2. 安装 agent-browser

**仅在第 1 步检查失败时执行**(用户已装就跳过):

```bash
# macOS / Linux
npm install -g agent-browser
agent-browser install    # 下载 Chromium ~500MB

# 装好后 WorkBuddy 重启,agent-browser skill 会被自动识别
# 检查: agent-browser --version 应该输出 1.3.0+
```

**故障排查** — 如果 `agent-browser install` 报 "SIGILL / exit 133" 类错误,通常是 Node.js 损坏:
```bash
# 检查
node -e "console.log('ok')"   # 必须输出 "ok"
which -a node                   # 查 node 路径

# 如果失败,显式指定 working node 的 PATH 跑
PATH="/path/to/working-node/bin:$PATH" agent-browser open <url>
```

## 3. 首次使用: 平台登录

**关键约束**:跑批需要用户在豆包/Kimi/通义已登录。LLM 不自动登录(避免风控)。

**步骤**:
1. LLM 用 agent-browser 打开平台:
   ```bash
   agent-browser open https://www.doubao.com/chat/
   ```
2. 浏览器打开后,LLM 检测登录态(看 snapshot 是否含"登录"按钮 + URL 是否含 `?from_logout=1`)
3. 未登录 → 提示用户: "请在打开的 WorkBuddy 浏览器窗口里手动登录豆包(扫码/手机验证),登录完告诉我"
4. 用户登录后 → cookie 通过 agent-browser daemon 持久化,后续免登录
5. 同样的方式登录 Kimi 和通义

**注意**:
- agent-browser daemon 在第一次 `open` 后启动,后续 `open` 同 URL 不会重新打开
- 多个平台共用一个 daemon,所以中途不要 close
- `agent-browser close` 仅在所有 platform 跑完后才调

## 4. 单次问询的标准调用序列

对每个 (platform, prompt) LLM 执行以下序列:

```bash
# 1. 打开 platform(如果已开,直接 navigate;不要重复 close)
agent-browser open https://www.doubao.com/chat/

# 2. 等首屏(用 --load load 而非 networkidle,SPA 永远不会 idle)
agent-browser wait --load load

# 3. 找输入框(用 snapshot -i 拿带 element ID 的页面,别硬编码 selector)
agent-browser snapshot -i
# LLM 从输出找 textarea 或 contenteditable div,记下 selector

# 4. 输入 prompt
agent-browser type "textarea[placeholder='发消息...']" "推荐 2025 奶茶品牌"

# 5. 按 Enter 发送(最稳,绕开按钮 class 动态变化)
# 用 agent-browser 执行键盘事件:
agent-browser press "Enter"   # 如果支持;或用 type 完后 LLM 模拟 Enter

# 6. 轮询等回答完成(LLM 自己做,不是 agent-browser 命令)
# LLM 内部循环:
#   for _ in range(20):
#     sleep(3)
#     text = agent-browser snapshot(过滤出最新 assistant message)
#     if text 长度稳定 2 次(连续 2 次 len 一致): break

# 7. 抓最终回答
agent-browser snapshot
# LLM 解析:从 snapshot 里提取最后一条 assistant 消息的完整文本

# 8. 提取引用源(snapshot 里所有 a[href*="//"] 的链接,过滤站内链接)
# LLM 自己解析,不需要额外命令

# 9. 截图留档(写到 ~/.geo-radar-cn/screenshots/<platform>_<n>.png)
agent-browser screenshot --path ~/.geo-radar-cn/screenshots/doubao_001.png

# 10. 反爬间隔
sleep(3)
```

**关键原则**:
- **不要在中间 close** daemon,只所有 platform 跑完才 close
- **selector 让 LLM 自己发现**,不要硬编码(平台 DOM 改 LLM 自己适应)
- **轮询等回答稳定**,不要假设 5 秒一定够(LLM 回答慢可能 30 秒)
- **截图留档**,方便用户审计"LLM 真的回答了"

## 5. 平台 URL 与参考 selector

| 平台 | URL | 输入框典型 selector | 备注 |
|---|---|---|---|
| 豆包 Doubao | `https://www.doubao.com/chat/` | `textarea[placeholder="发消息..."]` | 4.4 亿月活,数据最多 |
| Kimi 月之暗面 | `https://kimi.moonshot.cn/` | `div[contenteditable="true"]` | 长文本能力强 |
| 通义千问 | `https://tongyi.aliyun.com/qianwen/` | `textarea[placeholder*="输入"]` | 阿里系,商业覆盖 |

**selector 仅作参考**。LLM 实际跑时用 `snapshot -i` 看真实 DOM,自己适配。

## 6. 常见错误与恢复

| 错误 | 原因 | 恢复 |
|---|---|---|
| `agent-browser: command not found` | 没装 | 跑 `npm install -g agent-browser && agent-browser install` |
| `agent-browser open` 后没反应 | daemon 启动失败,Node 损坏 | 见第 2 步故障排查 |
| `snapshot` 一直空 | 没等加载完,或没登录被 redirect | 加 `wait --load load` 或让用户登录 |
| 输入框 selector 找不到 | DOM 改版 | LLM 重新 `snapshot -i`,看真实 DOM 找新 selector |
| 回答一直不出现(轮询超时) | LLM 思考慢 / 网络问题 | 增加轮询次数上限(20 → 30) |
| 平台报错"请登录" | 强制登录,cookie 失效 | 重新让用户登录,cookie 持久化到 daemon |
| 反爬验证码 | 触发风控 | 报告第 7 节明示,verdict 强制 🟡,停止跑批 |

## 7. 跑批完成后清理

所有 platform × prompt 跑完后:

```bash
# 1. 关闭 browser daemon
agent-browser close

# 2. 报告数据 LLM 自己整理(放 ~/.geo-radar-cn/reports/geo_report_<brand>_<date>.json)

# 3. 截图保留 7 天(LLM 自己 cron 清理)
find ~/.geo-radar-cn/screenshots/ -mtime +7 -delete
```

## 8. 跑批规模与时间预估

| 规模 | prompts | 平台数 | 问询数 | 时间 |
|---|---|---|---|---|
| 快速预览 | 5 | 1 | 5 | 2-5 分钟 |
| 标准 | 20 | 3 | 60 | 8-15 分钟 |
| 完整 | 30 | 3 | 90 | 12-25 分钟 |

**单次问询时间分布**(实测 2026-08):
- 打字/Enter: 1-2 秒
- LLM 思考: 5-30 秒(看 prompt 复杂度)
- snapshot 提取: 2-3 秒
- 反爬 sleep: 3 秒
- **小计**: 11-38 秒/次

## 9. 与其他模式的区别

| 模式 | 跑批方式 | LLM 角色 | 何时用 |
|---|---|---|---|
| **v2.1 agent-browser (推荐)** | LLM 自己调 agent-browser | 跑问询 + 抓数据 + 写报告 | WorkBuddy 桌面,默认 |
| v2.0 Python 爬虫 (CLI 备用) | 用户跑 Python 脚本,LLM 拿 JSON | 拿 JSON + 写报告 | 纯 CLI / 沙箱 / CI |
| v1.0 web_search (最后 fallback) | LLM 用 web_search 工具 | 拿间接信号 + 写报告 | 无浏览器 / 快速预览 |

v2.0 Python 爬虫代码在 `examples/legacy-v2.0-python-crawler/`,保留作 CLI 备用。
v1.0 web_search 模式在 LLM 直接调 web_search 工具,不需要额外代码。
