# 塔罗解牌 Skill

> **版本**: v1.0.0
> **状态**: ✅ stable
> **简介**: 面向中文用户的结构化塔罗抽牌与解读框架

---

## 是什么

一个基于 **78 张韦特体系全牌 + 18 个经典牌阵** 的塔罗抽牌与解读 skill。LLM 引导用户完成"抽卡动作 + 牌义解读 + 综合叙事 + 行动建议 + 边界声明"全流程。

## 不是什么

- 不是 AI 算命 —— 全程"娱乐性质"定位
- 不是预测未来 —— 只呈现"趋势与可能"
- 不替代专业建议 —— 涉及医疗 / 法律 / 投资时拒绝并转介
- 不永久存储用户数据 —— 解读过程无状态

## 核心特点

- **抽卡动作由用户主动完成**（核心 UX 原则）
- **78 张牌义库**（22 大阿卡纳 + 56 小阿卡纳，×正逆位 = 156 个含义单元）
- **18 个牌阵**（单张 / 三张 / 时间流 / 凯尔特十字 / 六芒星 / 身心灵 / 维纳斯 / 生命之树 / 财富之树 等）
- **结构化解读**（7 节固定框架：抽卡确认 / 总览 / 揭晓 / 单牌 / 联动 / 叙事 / 行动 / 边界）
- **工具书式调性**（克制、专业、不营销、不夸张）
- **图来自 Liora Moon 项目**（详见 [SKILL.md §图版权声明](./SKILL.md)）

## 文件结构

```
rider-waite-cn__skillhub/
├── SKILL.md                    # 主入口（5 步工作流 + 14 禁止项）
├── skill.json                  # 元数据（18 spreads / 31 keywords / 13 triggers）
├── README.md                   # 本文件
├── skill-card.md               # 商店展示卡
├── CHANGELOG.md                # 版本变更
├── references/
│   ├── 78-cards.md             # 78 张牌义库
│   ├── spreads.md              # 18 牌阵定义
│   ├── four-elements.md        # 四元素框架
│   ├── reading-framework.md    # 7 节解读流程
│   ├── ethics.md               # 塔罗师诫命 + 拒绝服务清单
│   └── ai-prompt-template.md   # LLM 解牌 prompt 模板
├── assets/cards/
│   ├── major/*.webp            # 22 张大阿卡纳
│   └── minor/*.webp            # 56 张小阿卡纳
├── examples/
│   ├── case-001-单抽-感情-愚者.md
│   ├── case-002-凯尔特十字-事业.md
│   └── case-003-时间流-选择.md
└── tests/pattern_checker.py
```

## 适用场景

- 「抽一张牌看看今天的运势」
- 「我想用三张牌看看过去 / 现在 / 未来」
- 「帮我用凯尔特十字分析下我现在的问题」
- 「我在纠结 A 和 B，帮我抽一组」
- 「我想做一次深度自我探索」

## 快速开始

```bash
# 1. 验证 skill 包完整性
python3 tests/pattern_checker.py

# 2. 阅读核心文档
# - SKILL.md（必读，工作流 + 14 禁止项）
# - references/78-cards.md（牌义库）
# - references/spreads.md（牌阵定义）
# - references/ethics.md（伦理底线）

# 3. 触发 skill
# 在 Claude / Cursor / 任意 LLM agent 加载 SKILL.md 即可
```

## 适用范围

**v1.0 中文 only**：
- ✅ 简体中文输入 / 简体中文解读
- ✅ 18 个牌阵 + 78 张韦特体系全牌
- ⏳ 英文 / 其他语种：v1.1 规划
- ⏳ 马赛 / 托特等其他体系：v2.0 规划

## 伦理承诺

本 skill 严格遵守 [塔罗九戒](references/ethics.md)：

1. 客观慈悲
2. 协助引导
3. 专业合道
4. 收费透明（本 skill 免费）
5. 保密
6. 转介专业（医疗 / 法律 / 投资 → 转介）
7. 不信命定
8. 保守隐私（不存储用户数据）
9. 钻研正道

## 图版权

78 张中文塔罗牌图来自 [Liora Moon](https://lioramoon.com) 项目（仓库：github.com/shike/lotus-tarot）。

- 牌图所有权与设计版权归 Liora Moon 项目所有
- 本 skill 仅在框架内引用，**未经授权不得二次分发、转售或用于其他商业项目**
- skillhub 商店展示与下载时，沿用此声明
- 如发现牌图被未授权使用，联系 owner：shike

## 维护

- **当前版本**: v1.0.0
- **更新策略**: 牌义库持续完善，牌阵按需扩展
- **反馈渠道**: 商店页 / GitHub issue

## 许可

MIT License（牌义库 + 文本部分）
牌图所有权：Liora Moon 项目所有
