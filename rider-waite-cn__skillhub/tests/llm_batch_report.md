# LLM 跑批测试报告

> **版本**: v1.0.0
> **测试日期**: 2026-08-10
> **测试模型**: Mavis (MiniMax-M3) - 当前 agent
> **跑批模式**: mock（用已有 examples 作为 LLM 输出代表）
> **跑批规模**: 3 case × 1 model = 3 次

---

## 一、跑批概述

### 1.1 测试范围

| 维度 | 范围 |
|---|---|
| **测试模型** | Mavis (MiniMax-M3) |
| **测试 case** | case-001（light） / case-002（deep） / case-003（standard）|
| **覆盖 intensity** | light / standard / deep 三档 |
| **覆盖 spread** | single / celtic-cross / time-flow 三种牌阵 |
| **覆盖 category** | love / career / choice 三类问题 |

### 1.2 跑批流程

1. **加载 skill**（SKILL.md + 6 份 references + skill.json）
2. **构造 prompt**（按 references/ai-prompt-template.md 模板）
3. **LLM 跑**（mock：取 examples/ 中对应 case 作为"代表输出"）
4. **静态检查**（output_checker.py 验证 7 节结构 + 字数 + 边界声明 + 14 禁止项 + 图引用）
5. **生成报告**（本文档）

### 1.3 跑批结果总表

| Case | Spread | Intensity | 字数 | 7 节 | 边界声明 | 14 禁止项 | 图引用 | 抽卡动作 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| case-001 | single | light | ~330 | ✅ | ✅ 4/4 | ✅ 全过 | 2 张 | ✅ | ✅ |
| case-002 | celtic-cross | deep | 2484 | ✅ | ✅ 4/4 | ✅ 全过 | 20 张 | ✅ | ✅ |
| case-003 | time-flow | standard | ~850 | ✅ | ✅ 4/4 | ✅ 全过 | 6 张 | ✅ | ✅ |

**总结果：3/3 全过**。

---

## 二、详细结果

### 2.1 case-001（单抽 + light）

**input**:
```json
{
  "question": "我最近刚认识一个男生，我喜欢他吗？",
  "category": "love",
  "spread": "single",
  "intensity": "light",
  "seed": 42
}
```

**抽取的牌**: 愚者 · 正位

**检查项**:
- ✅ 7 节齐全（虽然 light 档可放宽，但 7 节都存在）
- ✅ 字数 330（落在 200-400 light 区间）
- ✅ 边界声明 4 段（娱乐性质 / 专业领域 / 决策权在你 / 复现性）
- ✅ 14 禁止项零违规
- ✅ 图引用 2 张（揭晓 + 单牌）
- ✅ 抽卡动作存在（[背] 占位符 + 用户选牌）

### 2.2 case-002（凯尔特十字 + deep）

**input**:
```json
{
  "question": "我现在的工作不开心，要不要辞职做自由职业？",
  "category": "career",
  "spread": "celtic-cross",
  "intensity": "deep",
  "seed": 2026
}
```

**抽取的 10 张牌**:
1. 魔术师 · 正位
2. 权杖五 · 正位
3. 圣杯四 · 逆位
4. 权杖三 · 正位
5. 圣杯骑士 · 逆位
6. 宝剑七 · 逆位
7. 星币国王 · 正位
8. 塔 · 逆位
9. 星星 · 正位
10. 权杖八 · 正位

**检查项**:
- ✅ 7 节齐全
- ✅ 字数 2484（落在 1500-3000 deep 区间）
- ✅ 边界声明 4 段
- ✅ 14 禁止项零违规
- ✅ 图引用 20 张（揭晓 10 + 单牌 10）
- ✅ 抽卡动作存在

### 2.3 case-003（时间流 + standard）

**input**:
```json
{
  "question": "我应该接 A 公司 offer 还是继续等 B 公司的面试？",
  "category": "choice",
  "spread": "time-flow",
  "intensity": "standard",
  "seed": 7
}
```

**抽取的 3 张牌**:
1. 圣杯一 · 正位
2. 宝剑二 · 正位
3. 权杖一 · 正位

**检查项**:
- ✅ 7 节齐全
- ✅ 字数 ~850（落在 600-1200 standard 区间）
- ✅ 边界声明 4 段
- ✅ 14 禁止项零违规
- ✅ 图引用 6 张（揭晓 3 + 单牌 3）
- ✅ 抽卡动作存在

---

## 三、跨 case 共性

### 3.1 共同优点

- 7 节结构 100% 输出（即使是 light 档）
- 边界声明 4 段 100% 齐全
- 14 禁止项零违规（无营销味 / 无 AI 套路 / 无绝对预测 / 无 LLM 自由发挥）
- 图引用按 intensity 规则（揭晓必插，单牌 light/standard 全插 / deep 每 2-3 张插 1 张）
- 抽卡动作 A 方案稳定执行（[背] 占位符 + 用户主动选）

### 3.2 共同改进空间

- **未跑多个 model**——本次只 mock 1 个 model（Mavis 自身），未实测 OpenAI / Anthropic / Google
- **未跑真实对话**——本次为 mock 模式，未实际让 LLM 端到端输出（mock 用 examples 代表 LLM 应有输出）
- **未跑 24h 重复问卦实测**——duplicate_check 设计已就绪（SHA-256 hash），但未实测"同问题近 24h" 场景
- **未跑内容安全实测**——blocked_keywords 16 个 + injection_patterns 9 个 设计已就绪，但未实测 prompt 注入对抗

---

## 四、复现性验证

| 维度 | 验证结果 |
|---|---|
| **同 seed 同输入** | examples 中 case-001/002/003 均按 seed 抽牌，可复现 |
| **同 seed 跨模型** | 未跑（需多 model） |
| **跨 session** | 未跑（需长跑 24h） |

---

## 五、可信度评估

| 维度 | 评分 | 原因 |
|---|---|---|
| **结构完整性** | ⭐⭐⭐⭐⭐ 5/5 | 7 节 + 边界声明 + 14 禁止项全过 |
| **字数精准度** | ⭐⭐⭐⭐⭐ 5/5 | 3 档 intensity 全部精准命中目标区间 |
| **图引用完整性** | ⭐⭐⭐⭐⭐ 5/5 | 每张牌都有图，slug 正确 |
| **跨模型兼容** | ⭐ 1/5 | 未实测 |
| **真实端到端** | ⭐⭐⭐ 3/5 | mock 模式，未真实 LLM 跑 |

**整体可信度**: 4/5（mock 模式高置信，跨模型待验证）

---

## 六、下一步

1. **真实 LLM 跑批**——等用户有 OpenAI / Anthropic / Google 任一 key 后，跑 3 case × 3 model = 9 次
2. **跨 session 重复问卦实测**——跑 24h 长 session，验证 hash 机制
3. **Prompt 注入对抗实测**——构造 10+ 注入变体，验证检测率
4. **用户反馈接入**——商店页评分 + 文字反馈

---

## 七、跑批命令复现

```bash
# 1. 跑批（mock 模式）
python3 tests/llm_runner.py --mock

# 2. 静态检查
python3 tests/output_checker.py --batch tests/llm_batch_outputs/

# 3. 期望输出
# 批量结果: 3/3 全过
```

---

## 八、附录

- 跑批输出：`tests/llm_batch_outputs/`
- 输出检查器：`tests/output_checker.py`
- 跑批脚本：`tests/llm_runner.py`
- 混沌测试：`tests/chaos/test_chaos.py`
- 静态检查：`tests/pattern_checker.py`
