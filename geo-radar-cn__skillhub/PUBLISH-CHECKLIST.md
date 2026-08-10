# GEO 雷达 · 上架准备清单（v1.0.0）

> 本文件是 v1.0.0 上架到 skillhub.cn 的 step-by-step 清单。
> 跑通整个流程后,本文件可作为后续版本的复用模板。

---

## 一、上架前检查

### 1.1 skill 包完整性

```bash
cd geo-radar-cn__skillhub

# 1. 跑 pattern_checker
python3 tests/pattern_checker.py
# 期望：✅ 100+ pass / 0 ❌

# 2. 跑 chaos
python3 tests/chaos/test_chaos.py
# 期望：✅ 12+ pass / 0 ❌

# 3. 跑 output_checker
python3 tests/output_checker.py --batch examples/
# 期望：3/3 全过

# 4. 跑 llm_runner mock
python3 tests/llm_runner.py --mock
# 期望：3/3 全过
```

### 1.2 必需文件清单

| 文件 | 状态 | 备注 |
|---|---|---|
| SKILL.md | ✅ | 主入口 |
| skill.json | ✅ | 元数据 |
| skill-card.md | ✅ | 商店展示卡 |
| README.md | ✅ | skill 介绍 |
| CHANGELOG.md | ✅ | 版本变更 |
| _meta.json | ✅ | slug = "geo-radar-cn" |
| _skillhub_meta.json | ✅ | name = "GEO 雷达" |
| references/query-templates.md | ✅ | 8 行业 × 4 类型查询词 |
| references/report-schema.md | ✅ | 8 节字段定义 |
| references/web-search-prompts.md | ✅ | 24 个搜索 prompt |
| references/chaos-cases.md | ✅ | 16 个混沌用例 |
| examples/ | ✅ | 3 份范本(高/中/低数据) |
| tests/ | ✅ | CI 4 件套 |
| icon.png | ✅ | 封面图（走平台独立字段） |
| PUBLISH-CHECKLIST.md | ✅ | 本文件 |

### 1.3 ⚠️ 能力边界(必读)

v1.0 用 web_search 抓 AI 引用源,**不直连 LLM**:
- ✅ 覆盖:Google AI Overview + Perplexity 引用基础
- ❌ 不覆盖:豆包 / Kimi / 文心一言 / 腾讯元宝 / 秘塔(国内 AI 引擎是 SPA,抓不到)
- 报告第 7 节明示这一点
- 想覆盖国内原生 AI 引擎 → v2.0 接 LLM API key

---

## 二、上架步骤

### 2.0 ⚠️ 打包前清理

```bash
# 1. 清理 Python 缓存
find geo-radar-cn__skillhub -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 2. 清理跑批产物
rm -rf geo-radar-cn__skillhub/tests/llm_batch_outputs/

# 3. 确认 .DS_Store 不在
find geo-radar-cn__skillhub -name ".DS_Store" -delete
```

### 2.1 封面图(走平台独立字段)

**不要把 icon.png 打进 zip**。在 skillhub 上传页"封面图"字段单独上传。

### 2.2 打包成 zip

```bash
cd /Users/shike/Desktop/code/location-skill

zip -r geo-radar-cn__skillhub-v1.0.0.zip geo-radar-cn__skillhub/ \
  -x "*/.DS_Store" "*/._*" "*/.git/*" \
     "*/__pycache__/*" "*/llm_batch_outputs/*" \
     "*/icon.png"

# ↑ icon.png 走平台独立字段,排除
# ↑ 期望 < 200KB(纯文本)
```

### 2.3 上传到 skillhub.cn

- 访问 https://skillhub.cn/publish
- 上传 zip
- 填写:
  - **slug**: `geo-radar-cn`
  - **标题**: `GEO 雷达：基于公开数据的多 AI 引擎可见度诊断与优化指引`
  - **简介**: 来自 `skill-card.md`
  - **标签**: 来自 `skill.json` 的 `tags` 字段
  - **封面图**: 单独上传 `icon.png`(1024×1024 PNG)
- 提交审核

### 2.4 ⚠️ 审核期间(诚实声明)

skillhub 平台可能问"为什么不接 LLM API":
- 答:v1.0 走 web_search 代理信号,覆盖 Google AI Overview + Perplexity 引用
- 国内 AI 引擎(豆包/Kimi/文心)是 SPA,web_search 抓不到
- v2.0 接 API key 模式

---

## 三、上架后维护

### 3.1 反馈收集

- 监控商店页评分 / 评论
- 收集用户最常问的问题 / 报错
- 持续更新 `CHANGELOG.md`

### 3.2 v1.1 规划

- 接 LLM API key 模式(豆包 / Kimi / 文心真实跑批)
- 增加更多行业模板
- A/B test 框架

### 3.3 v2.0 远期

- 海外市场(英文 + 多语言)
- AI 引擎引用情感分析(正/负/中性)
- 自动生成 GEO 优化文章(基于 6 步操作框架)

---

## 四、风险与兜底

| 风险 | 兜底 |
|---|---|
| 商店审核不通过 | 退回修改(命名 / 安全 / 中文) |
| web_search 失效 | 降级为"LLM 提示用户自行测试"模式 |
| 8 行业不覆盖 | 通用模板兜底,用户手动输入 category 触发 |
| 用户输入海外品牌 | verdict 强制 🔴 + "v1.0 仅支持中国大陆"提示 |
| 县城及以下品牌数据稀缺 | 大量标"未找到公开数据"+ 附录 B 明示局限 |

---

## 五、联系

- 维护者: shike
- 反馈: 商店页 / GitHub issue
- 紧急: 邮件 / 站内信
