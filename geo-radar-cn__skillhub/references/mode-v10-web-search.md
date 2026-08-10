# v1.0 web_search 代理模式(最后 fallback)

> **状态**:仅 fallback。**v2.3 Playwright + 系统 Chrome 是默认**(真实 90%+)。
> 本模式仅在 v2.3 / v2.2 / v2.1 全部失败时启用(LLM 拒演 + 无 Python + 无 web 工具能力)。

## 何时切到 v1.0

LLM 在跑批前检测:
- v2.3 Playwright 不可用(无 Python)
- v2.2 LLM 模拟不可用(LLM 自报"无法扮演其他 AI")
- LLM 也没有 web_search 工具能力(极少见)
- 用户明确要 v1.0 模式(几乎不会)

满足以上任一条件,LLM 切到 v1.0 模式:

```
[检测到] v2.3 + v2.2 都不可用
[切到]   v1.0 web_search 模式
[方法]   LLM 调自己的 web_search 工具
[预计]   1-3 分钟
[真实度] 30-50%(基于 web 引用源 SEO)
```

## v1.0 跑批方法

LLM 用自己的 web_search 工具抓"豆包/Kimi/通义 引用了哪些网页":

```
对 platform in [豆包, Kimi, 通义]:
    对 query in queries:
        search_results = LLM.web_search(
            query=f"site:csdn.net OR site:zhihu.com {brand} {query}"
        )
        # LLM 从搜索结果中找"AI 引擎引用源"
        # 这是间接信号(豆包/百度等可能引用过的网页)
        collect {
            platform: platform,
            query: query,
            text: "基于 web 引用推断",  # 不是真实 LLM 输出
            citations: extract_urls(search_results),
            source: "web_search_proxy"  # 标记
        }
```

## 报告头部必加声明

```markdown
## 数据来源说明(v1.0)

本报告基于 **v1.0 web_search 代理模式** 生成(因 v2.3 + v2.2 都不可用,降级)。
LLM 调 web_search 工具抓"豆包/Kimi/通义 引用了哪些网页"。

- ⚠️ 不是真实 LLM 输出,是"AI 引擎引用源 SEO 监测"
- ⚠️ 30-50% 的 GEO 信号覆盖(间接,经常错位)
- ✅ 0 安装,跑批快(1-3 分钟)
- 🎯 想要更准确数据?装 v2.3 Playwright(10MB)或 WorkBuddy 用 v2.1 agent-browser
```

## 模式对比(总结)

| 维度 | v2.3 Playwright (默认) | v2.2 LLM 模拟 (fallback) | v2.1 agent-browser (Power) | v1.0 web_search (最后) |
|---|---|---|---|---|
| 安装成本 | 10MB | 0 | 50-500MB | 0 |
| 真实度 | 90%+ | 60-80% | 90%+ | 30-50% |
| 数据来源 | 真实平台抓取 | LLM 训练共识 | 真实平台抓取 | AI 引用源 SEO |
| 跨 AI 平台 | ⚠️ 需 Python | ✅ 任意 | ❌ 仅 WorkBuddy | ✅ 任意 |
| 跑批时间 | 3-12 分钟 | 2-5 分钟 | 5-25 分钟 | 1-3 分钟 |
| 登录需求 | 用户手动登录(1 次) | 0 | 用户手动登录(1 次) | 0 |
| 上架策略 | 默认 | fallback | Power User | 最后 fallback |
