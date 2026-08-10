# skillhub.cn 上架准备清单

> 本文件是 v1.0.0 上架到 skillhub.cn 的 step-by-step 清单。
> 跑通整个流程后，本文件可作为后续版本的复用模板。

---

## 一、上架前检查

### 1.1 skill 包完整性

```bash
# 1. 跑 pattern_checker
cd rider-waite-cn__skillhub
python3 tests/pattern_checker.py

# 期望输出：
# ✅ 98 pass | ⚠️ 0 warn | ❌ 0 fail
```

### 1.2 必需文件清单

| 文件 | 状态 | 备注 |
|---|---|---|
| SKILL.md | ✅ | 主入口 |
| skill.json | ✅ | 元数据 |
| README.md | ✅ | 介绍 |
| skill-card.md | ✅ | 商店展示卡 |
| CHANGELOG.md | ✅ | 版本变更 |
| _meta.json | ⏳ | 上架时由 skillhub 平台生成 |
| _skillhub_meta.json | ⏳ | 用户安装时由平台生成 |
| references/78-cards.md | ✅ | 78 张牌义库 |
| references/spreads.md | ✅ | 18 牌阵定义 |
| references/four-elements.md | ✅ | 四元素框架 |
| references/reading-framework.md | ✅ | 解读流程 |
| references/ethics.md | ✅ | 塔罗师诫命 |
| references/ai-prompt-template.md | ✅ | LLM prompt 模板 |
| assets/cards/major/*.webp | ✅ | 22 张大阿卡纳 |
| assets/cards/minor/*.webp | ✅ | 56 张小阿卡纳 |
| examples/case-001-*.md | ✅ | 单抽案例 |
| examples/case-002-*.md | ✅ | 凯尔特案例 |
| examples/case-003-*.md | ✅ | 时间流案例 |
| tests/pattern_checker.py | ✅ | 静态检查器 |
| icon.png | ⏳ | 商店封面图（需单独制作） |
| PUBLISH-CHECKLIST.md | ✅ | 本文件 |

### 1.3 包大小

```bash
# 期望总大小 < 5MB（78 张 webp 共 1MB + 文本 ~ 100KB）
du -sh rider-waite-cn__skillhub/
```

---

## 二、上架步骤

### 2.1 制作封面图

- **要求**: 1024×1024 PNG 或 JPG
- **风格**: 与 Liora Moon 视觉调性一致（暗色神秘）
- **元素**: 塔罗牌意象（不显示具体牌面，避免误解）
- **建议色系**: 深紫 / 靛蓝 / 黑
- **A/B 选项**:
  - A: 抽象几何（适合多场景）
  - B: 牌背纹理特写（增强塔罗调性）

### 2.2 打包成 zip

```bash
# 1. 进入 skill 目录
cd /Users/shike/Desktop/code/location-skill

# 2. 打包（注意：zip 内根目录必须是 rider-waite-cn__skillhub/）
zip -r rider-waite-cn__skillhub-v1.0.0.zip rider-waite-cn__skillhub/ \
  -x "*/.DS_Store" "*/._*" "*/.git/*"

# 3. 验证 zip 结构
unzip -l rider-waite-cn__skillhub-v1.0.0.zip | head -30
```

### 2.3 上传到 skillhub.cn

- 访问 https://skillhub.cn/publish
- 上传 zip
- 填写：
  - 标题: `塔罗解牌：韦特体系 78 牌 × 18 牌阵 × 中文解读框架`
  - 简介: 来自 `skill-card.md`
  - 标签: 来自 `skill.json` 的 `tags` 字段
  - 封面图: 步骤 2.1 制作的 1024×1024 图
- 提交审核

### 2.4 审核期间

skillhub 平台会进行：
- 安全审计（4 大维度）
- TRACE 评测（5 维度）
- 中文支持检查

**预审自查**：

| 自查项 | 通过条件 |
|---|---|
| 命名规范 | 主标 + 副标题，主标简洁，副标题说明范围 |
| 中文支持 | 全文中文，含中文 description |
| 安全风险 | 无网络请求 / 无文件写入 / 无命令执行 |
| 提示注入风险 | 14 条禁止项 + 塔罗师诫命明确 |
| 隐私保护 | 不存储用户数据明示 |

### 2.5 上架后

- 在 `_meta.json` 写入 `slug` + `version` + `publishedAt`（平台自动）
- 在 `_skillhub_meta.json` 写入安装信息（用户安装时自动）
- 通知用户：skillhub 商店页 + 站内信

---

## 三、上架后维护

### 3.1 反馈收集

- 监控商店页评分 / 评论
- 收集用户最常问的问题 / 报错
- 持续更新 `CHANGELOG.md`

### 3.2 v1.1 规划

- 英文版本（en）
- 越语版本（vi）— 配合 Liora Moon 主市场
- 24 节气牌阵
- 真实 LLM 跑批测试

### 3.3 v2.0 远期

- 马赛 / 托特体系
- 多牌阵组合
- 真人塔罗师协作
- 与 Liora Moon 商业产品的功能对标

---

## 四、风险与兜底

| 风险 | 兜底 |
|---|---|
| 商店审核不通过 | 退回修改（命名 / 安全 / 中文）|
| 用户把"AI 解读"当"算命" | SKILL.md 顶部诫命 + 解读结尾边界声明 |
| 牌图被未授权分发 | 商店页 + SKILL.md 双重声明 |
| 塔罗涉及命定论争议 | 14 条禁止项 + 拒绝服务清单 |
| 跨文化问题 | v1.0 限定中文；v1.1+ 视情况扩 |

---

## 五、联系

- 维护者: shike
- 反馈: 商店页 / GitHub issue
- 紧急: 邮件 / 站内信
