# skillhub.cn 上架准备清单

> 本文件是 v1.0.1 上架到 skillhub.cn 的 step-by-step 清单。
> v1.0.1 关键变更：**图引用从相对路径改为 jsdelivr CDN（skillhub 平台不接受二进制文件）**

---

## ⚠️ 重要前提（v1.0.1 必读）

**skillhub 平台只接受文本文件上传**（md / json / py / txt），**所有二进制（png / webp / pyc）都会被拒**。

v1.0.0 的设计 bug：
- `assets/cards/**/*.webp`（78 张牌图）+ `icon.png` 全部本地相对路径
- 打包上传时 100% 被平台拒
- 用户安装的 skill 完全看不到任何图

**v1.0.1 修复方案：jsdelivr CDN + GitHub public 仓库**
- 仓库 `shike/location-skill` 已设为 public
- 78 张牌图 + icon.png 通过 jsdelivr CDN 公开访问
- SKILL.md / references / examples 里的图引用全部改为 https URL
- assets/ 目录在 skill 包内仍保留（本地 dev / CI 用）

**图 URL 模板**：
```
https://cdn.jsdelivr.net/gh/shike/location-skill@main/rider-waite-cn__skillhub/assets/cards/{major|minor}/{slug}.webp
https://cdn.jsdelivr.net/gh/shike/location-skill@main/rider-waite-cn__skillhub/icon.png
```

---

## 一、上架前检查

### 1.1 skill 包完整性

```bash
# 1. 跑 pattern_checker
cd rider-waite-cn__skillhub
python3 tests/pattern_checker.py

# 期望输出：✅ 101 pass | ⚠️ 0 warn | ❌ 0 fail

# 2. 跑 chaos
python3 tests/chaos/test_chaos.py

# 期望输出：✅ 12 pass | ⚠️ 1 warn（重复问卦首次记录，预期） | ❌ 0 fail

# 3. 跑 output_checker
python3 tests/output_checker.py --batch examples/

# 期望输出：3/3 全过

# 4. 跑 llm_runner mock
python3 tests/llm_runner.py --mock

# 期望输出：3/3 全过
```

### 1.2 必需文件清单（v1.0.1 修订）

| 文件 | 状态 | 备注 |
|---|---|---|
| SKILL.md | ✅ | 主入口（v1.0.1 图引用改 URL） |
| skill.json | ✅ | 元数据（name 已改名 rider-waite-cn） |
| README.md | ✅ | 介绍 |
| skill-card.md | ✅ | 商店展示卡 |
| CHANGELOG.md | ✅ | 版本变更（v1.0.1 含 jsdelivr 改造记录） |
| _meta.json | ✅ | slug = "rider-waite-cn" |
| _skillhub_meta.json | ✅ | name = "塔罗解牌" |
| references/78-cards.md | ✅ | 78 张牌义库 |
| references/spreads.md | ✅ | 18 牌阵定义 |
| references/four-elements.md | ✅ | 四元素框架 |
| references/reading-framework.md | ✅ | 解读流程（图引用改 URL） |
| references/ethics.md | ✅ | 塔罗师诫命 |
| references/ai-prompt-template.md | ✅ | LLM prompt 模板（图引用改 URL） |
| **assets/cards/major/*.webp** | ⚠️ **本地保留**（dev/CI 用） | **生产环境走 jsdelivr URL** |
| **assets/cards/minor/*.webp** | ⚠️ **本地保留**（dev/CI 用） | **生产环境走 jsdelivr URL** |
| examples/case-001-*.md | ✅ | 单抽案例（图引用改 URL） |
| examples/case-002-*.md | ✅ | 凯尔特案例（图引用改 URL） |
| examples/case-003-*.md | ✅ | 时间流案例（图引用改 URL） |
| tests/pattern_checker.py | ✅ | 静态检查器（regex 兼容本地/URL） |
| tests/chaos/ | ✅ | 混沌测试（12 用例） |
| tests/output_checker.py | ✅ | 输出检查器（regex 兼容本地/URL） |
| tests/llm_runner.py | ✅ | 端到端跑批 |
| **icon.png** | ⚠️ **本地保留**（dev 用） | **生产环境走 jsdelivr URL** |
| PUBLISH-CHECKLIST.md | ✅ | 本文件 |

### 1.3 包大小

```bash
# 文本部分（实际打包内容，平台接受）
du -sh --exclude=assets --exclude=icon.png --exclude=__pycache__ rider-waite-cn__skillhub/

# 期望 < 500KB（纯 md/json/py 文本）

# 图资源（生产环境走 CDN，不打包）
du -sh rider-waite-cn__skillhub/assets rider-waite-cn__skillhub/icon.png

# 78 张 webp 共 6.1MB + icon.png 1.1MB = 7.2MB（托管在 GitHub）
```

---

## 二、上架步骤

### 2.0 ⚠️ 打包前清理（必做）

```bash
# 1. 清理 Python 缓存（已用 .gitignore 排除，但本地可能有）
find rider-waite-cn__skillhub -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 2. 清理跑批产物
rm -rf rider-waite-cn__skillhub/tests/llm_batch_outputs/

# 3. 确认 .DS_Store 不在
find rider-waite-cn__skillhub -name ".DS_Store" -delete
```

### 2.1 封面图（必走平台"封面图"独立字段）

**不要把 icon.png 打进 zip**。平台有独立"封面图"字段：
- 访问 https://skillhub.cn/publish 上传页
- 在"封面图"字段单独上传 `icon.png`（1024×1024 PNG）
- 这是 skillhub 平台的标准做法，二进制文件不进 zip

### 2.2 打包成 zip

```bash
# 1. 进入 skill 目录
cd /Users/shike/Desktop/code/location-skill

# 2. 打包（注意：zip 内根目录必须是 rider-waite-cn__skillhub/）
zip -r rider-waite-cn__skillhub-v1.0.1.zip rider-waite-cn__skillhub/ \
  -x "*/.DS_Store" "*/._*" "*/.git/*" \
     "*/__pycache__/*" "*/llm_batch_outputs/*" \
     "*/assets/cards/*" "*/icon.png"

# ↑ 关键：排除 assets/ 和 icon.png！这些走 jsdelivr CDN
# ↑ 排除 __pycache__ 和 llm_batch_outputs（dev 产物）

# 3. 验证 zip 结构（应该 < 500KB，纯文本）
unzip -l rider-waite-cn__skillhub-v1.0.1.zip
```

**预期 zip 内容**（只含文本）：
```
rider-waite-cn__skillhub/
├── SKILL.md
├── skill.json
├── skill-card.md
├── README.md
├── CHANGELOG.md
├── PUBLISH-CHECKLIST.md
├── _meta.json
├── _skillhub_meta.json
├── references/
│   ├── 78-cards.md
│   ├── spreads.md
│   ├── four-elements.md
│   ├── reading-framework.md
│   ├── ethics.md
│   └── ai-prompt-template.md
├── examples/
│   ├── case-001-单抽-感情-愚者.md
│   ├── case-002-凯尔特十字-事业.md
│   └── case-003-时间流-选择.md
└── tests/
    ├── pattern_checker.py
    ├── output_checker.py
    ├── llm_runner.py
    └── chaos/
        ├── __init__.py
        └── test_chaos.py
```

### 2.3 上传到 skillhub.cn

- 访问 https://skillhub.cn/publish
- 上传 zip（v1.0.1 < 500KB 的纯文本包）
- 填写：
  - **slug**: `rider-waite-cn`（不要用 `tarot-reading`，那是旧名字）
  - **标题**: `塔罗解牌：韦特体系 78 牌 × 18 牌阵 × 中文解读框架`
  - **简介**: 来自 `skill-card.md`
  - **标签**: 来自 `skill.json` 的 `tags` 字段
  - **封面图**: 单独上传 `icon.png`（1024×1024 PNG，1.1MB）
- 提交审核

### 2.4 验证图引用可访问

在审核前/后，可以用这个命令验证 jsdelivr URL 通不通：

```bash
# 1. 测 1 张图能 GET 200
curl -sI "https://cdn.jsdelivr.net/gh/shike/location-skill@main/rider-waite-cn__skillhub/assets/cards/major/the-fool.webp" | head -1
# 期望：HTTP/1.1 200 OK

# 2. 测 icon.png
curl -sI "https://cdn.jsdelivr.net/gh/shike/location-skill@main/rider-waite-cn__skillhub/icon.png" | head -1
# 期望：HTTP/1.1 200 OK
```

**如果 404**：
- 检查 GitHub 仓库 `shike/location-skill` 是否还是 public
- 检查 main branch 是否有该图（`git ls-tree origin/main`）

### 2.5 审核期间

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

### 2.6 上架后

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
| 牌图被未授权分发 | 商店页 + SKILL.md 双重声明（jsdelivr URL 公开可访问） |
| 塔罗涉及命定论争议 | 14 条禁止项 + 拒绝服务清单 |
| 跨文化问题 | v1.0 限定中文；v1.1+ 视情况扩 |
| **jsdelivr CDN 失效** | 备份方案：换 raw.githubusercontent.com（速度慢但稳定）/ 或换其他 CDN |
| **GitHub 仓库改回 private** | jsdelivr 立刻 404，必须保持 public 或迁到 OSS/七牛 |

---

## 五、联系

- 维护者: shike
- 反馈: 商店页 / GitHub issue
- 紧急: 邮件 / 站内信
