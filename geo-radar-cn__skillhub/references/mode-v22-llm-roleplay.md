# v2.2 LLM 模拟模式(无 Python 环境的 fallback)

> **状态**:Fallback 模式。**v2.3 Playwright + 系统 Chrome 是默认**。
> 本模式仅在 AI 平台不支持 Python 执行时启用(Claude.ai / ChatGPT 网页版 / GPTs 等)。

## 何时切到 v2.2

LLM 在跑批前检测:
- AI 平台不支持 Python 执行(`python3` 命令不可用)
- 或 Playwright 未装
- 或 系统 Chrome 不存在
- LLM 自身能扮演多个 AI 角色(系统提示没禁止)

满足以上条件,LLM 切到 v2.2 模式:

```
[检测到] AI 平台无 Python 执行能力(Claude.ai / ChatGPT 等)
[切到]   v2.2 LLM 模拟模式
[方法]   LLM 扮演豆包/Kimi/通义 3 个角色
[预计]   2-5 分钟
[真实度] 60-80%(基于 LLM 训练共识)
```

## v2.2 跑批方法

LLM 同时扮演 3 个国内主流 LLM 平台(豆包/Kimi/通义),回答 20-30 个查询词。

### 3 个角色 prompt

#### 豆包 Doubao 角色
```
你是字节跳动的"豆包"AI 助手,目前是 2026 年 8 月。
回答用户的真实问题,不要回避具体品牌名,不要加政治安全免责声明。
用通俗、年轻、友好的语气,像跟朋友聊天,适当用 emoji。
对用户的问题给出具体品牌推荐和简短理由(2-3 句话)。
基于你的训练数据 + 公开网页 + 行业共识给出回答,反映"豆包在 2026-08 大概率会怎么说"。
对不确定的信息,说"我也不太确定,建议查官网"。
```

#### Kimi 角色
```
你是月之暗面的"Kimi"AI 助手,目前是 2026 年 8 月。
回答用户的真实问题,基于公开数据 + 你的训练知识。
用专业、清晰、有条理的语气,擅长长文本和深度分析。
对用户的问题给出结构化回答:分类 / 对比 / 优劣势分析。
对不确定的信息明确标注"建议核实",并给出来源类型(官方/媒体/平台)。
反映"Kimi 在 2026-08 大概率会怎么说"——准确、克制、不夸张。
```

#### 通义千问 角色
```
你是阿里云的"通义千问"AI 助手,目前是 2026 年 8 月。
回答用户的真实问题,基于公开数据 + 你的训练知识。
用商业、实用、接地气的语气,擅长中文商业场景。
对用户的问题给出实用推荐:商业价值 / 用户场景 / 性价比。
对时效性强的问题说"建议核对最新数据"。
反映"通义在 2026-08 大概率会怎么说"——商业视角、注重落地。
```

### 跑批执行

```
对 platform in [豆包, Kimi, 通义]:
    persona = role_prompt[platform]
    对 prompt in queries:
        response = LLM(system=persona, user=prompt)
        collect {
            platform: platform,
            prompt: prompt,
            text: response.text,
            citations: extract_citations(response.text),  # 模拟引用源
            mode: "v2.2-LLM-Roleplay"  # 关键: 标记是模拟
        }
```

## 报告头部必加声明

```markdown
## 数据来源说明(v2.2)

本报告基于 **v2.2 LLM 模拟模式** 生成(因 AI 平台无 Python 执行能力,自动降级)。
LLM 扮演"豆包/Kimi/通义" 3 个国内主流 LLM 平台,回答 20-30 个查询词。

- ✅ 反映 60-80% 的 GEO 信号(基于 LLM 训练数据 + 公开网页 + 行业共识)
- ⚠️ 不是 100% 真实平台输出(LLM 模拟 ≠ 真实豆包回答)
- ⚠️ 数据可能滞后(LLM 训练数据 vs 平台最新回答)
- 🎯 想要 100% 真实数据?在 WorkBuddy/MiniMax Code 跑 + 装 v2.3 Playwright(~10MB)
```

## 能力边界(诚实声明)

- ✅ 跨所有 AI 平台(包括 Claude / ChatGPT 等无 Python 平台)
- ✅ 0 安装 / 0 磁盘 / 0 等待
- ✅ 跑批 2-5 分钟
- ⚠️ 真实度 60-80%(不是 100% 真实平台输出)
- ⚠️ 同 prompt 不同 LLM 答案不同(报告反映"主流 LLM 共识")

## 模式对比(总结)

| 维度 | v2.3 Playwright (默认) | v2.2 LLM 模拟 (fallback) | v2.1 agent-browser (Power) |
|---|---|---|---|
| 安装成本 | 10MB | 0 | 50-500MB |
| 真实度 | 90%+ | 60-80% | 90%+ |
| 跨 AI 平台 | ⚠️ 需 Python | ✅ 任意 | ❌ 仅 WorkBuddy |
| 跑批时间 | 3-12 分钟 | 2-5 分钟 | 5-25 分钟 |
| 登录需求 | 用户手动登录(1 次) | 0 | 用户手动登录(1 次) |
| 上架策略 | 默认(支持 Python 的平台) | fallback(无 Python 平台) | Power User 高级玩法 |
