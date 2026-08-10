# Changelog

本 skill 的所有重要变更都记录在此文件。

---

## v1.0.1 — 2026-08-10

### 🔄 改名（与 skillhub 平台原 `tarot-reading` id 冲突，重命名）

- **新名字**：`塔罗解牌：韦特体系 78 牌 × 18 牌阵 × 中文解读框架`
- **新 slug（stable id）**：`rider-waite-cn`
  - 避开 `tarot-reading` 通用 id 池
  - 体现"韦特体系"差异化（vs 通用塔罗）
  - 英文 + 区域后缀，跨平台 slug 兼容性好
- **新 folder**：`rider-waite-cn__skillhub/`（旧 `tarot-reading__skillhub/` 已废弃，需手动删除）
- **受影响文件**（共 13 个）：
  - `_meta.json` / `_skillhub_meta.json`（slug + name）
  - `SKILL.md`（frontmatter name + # 标题）
  - `skill.json`（name + tags）
  - `skill-card.md`（主标 + 标题）
  - `README.md`（标题 + folder 路径）
  - `PUBLISH-CHECKLIST.md`（folder 路径 + zip 命令 + 标题校验）
  - `references/ai-prompt-template.md`（"塔罗解读师"→"塔罗解牌师"）
  - `tests/pattern_checker.py`（描述文案）
  - `tests/chaos/chaos_tests.py` / `test_chaos.py`（描述文案）
  - `tests/llm_runner.py`（system prompt 角色描述）

### 不变
- 78 牌义库、18 牌阵、伦理底线、图版权、抽牌动作、7 节结构、CI 套件
- `pattern_checker.py` 仍 101 ✅ / 0 ❌
- `chaos test` 仍 12 ✅ / 0 ❌
- 文件结构、版本号（v1.0.0 → v1.0.1 PATCH bump）

### 验证
- `python3 tests/pattern_checker.py` → 101 ✅ / 0 ❌
- `python3 tests/chaos/test_chaos.py` → 12 ✅ / 0 ❌
- 残留旧名扫描：`grep -rn "tarot-reading\|塔罗解读" .` → 0 命中

### ⚠️ 待办
- **手动删除旧 folder**：`rm -rf /Users/shike/Desktop/code/location-skill/tarot-reading__skillhub/`
  （Mavis 沙箱不允许删除/移动已存在 folder，已 cp 新 folder 代替 mv）
- 重新打 zip 包：`zip -r rider-waite-cn__skillhub-v1.0.1.zip rider-waite-cn__skillhub/`
- 上架时用新 slug `rider-waite-cn`

---

## v1.0.0 — 2026-08-10

### 🎉 首发版本

#### ✨ 核心功能

- **78 张韦特体系全牌义库**（22 大阿卡纳 + 56 小阿卡纳，×正逆位 = 156 含义单元）
- **18 个经典牌阵**（5 通用 + 5 深度 + 6 感情 + 2 自我 + 1 事业 + 1 运势 + 1 抉择）
- **抽卡动作**（用户主动翻牌，LLM 不替用户做选择）
- **7 节结构化解读**（抽卡确认 / 总览 / 揭晓 / 单牌 / 联动 / 叙事 / 行动 / 边界）
- **3 档解读深度**（light / standard / deep）
- **4 元素 + 数字 + 宫廷牌速查框架**

#### 🛡️ 伦理底线

- **塔罗九戒完整遵守**（9 条戒律）
- **塔罗师诫命 SKILL.md 顶部硬约束**
- **14 条禁止项**（违反则解读作废）
- **拒绝服务清单**（医疗 / 法律 / 投资 / 命定论 → 拒绝并转介）
- **不永久存储用户数据**

#### 📚 文档

- `SKILL.md`（5 步工作流 + 14 禁止项 + 鲁棒性 + 适用范围）
- `references/78-cards.md`（78 张牌义库，30KB）
- `references/spreads.md`（18 牌阵定义，11KB）
- `references/four-elements.md`（四元素框架，4KB）
- `references/reading-framework.md`（7 节解读流程，5KB）
- `references/ethics.md`（塔罗师诫命 + 拒绝服务清单，6KB）
- `references/ai-prompt-template.md`（LLM 解牌 prompt 模板，8KB）
- 3 个完整 example（单抽 / 凯尔特 / 时间流）

#### 🎨 视觉资源

- **78 张中文牌图**（来自 Liora Moon 项目，515×768 webp，1MB）

#### 🧪 测试

- `tests/pattern_checker.py`（90+ 静态检查项）
  - 必需文件存在性
  - YAML frontmatter
  - 顶部诫命 + 图版权
  - 14 条禁止项完整性
  - 78 张牌义完整性
  - 78 张牌图完整性
  - 18 牌阵完整性
  - 3 个 example 完整性
  - skill.json 字段完整性

#### 📦 上架目标

- skillhub.cn 公开（中文用户 + 腾讯生态）

---

## v1.1.0 — 计划

### 计划功能

- [ ] 英文版本（en）
- [ ] 越语版本（vi）— 配合 Liora Moon 主市场
- [ ] 24 节气牌阵
- [ ] 历史牌阵扩展（圣甲虫形 / 七行星 / 二择一等）
- [ ] 与 Liora Moon 项目的 6 语言内容联动

### 计划改进

- [ ] 真实 LLM 跑批测试（v1.0 仅有静态检查）
- [ ] 用户反馈收集
- [ ] 牌义库持续完善
- [ ] 调性校对（邀请塔罗师 review）

---

## v2.0.0 — 远期

### 计划功能

- [ ] 马赛体系 / 托特体系
- [ ] 多牌阵组合（一次抽多组）
- [ ] 真人塔罗师协作
- [ ] 占卜历史档案（用户本地存储）
- [ ] 与 Liora Moon 商业产品的功能对标

---

## 维护说明

- **当前维护者**: shike
- **反馈渠道**: skillhub 商店页 / GitHub issue
- **更新策略**: minor 版本（v1.x）持续完善；major 版本（v2.x）体系级扩展
