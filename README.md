# skills

LLM skills 集合：商业尽调、生活咨询、培训教练三大方向的对话式 skill 仓库。

## Skill 总览

| Skill | 版本 | 状态 | 简介 |
|---|---|---|---|
| [site-intelligence-report](./site-intelligence-report__skillhub/) | 1.1.1 | ✅ stable | 拓店选址尽调：单地址深度评估 + 多地址对比，9 维度 + 财务三维评估 |
| [pet-care-cn](./pet-care-cn__skillhub/) | 2.0.0 | ✅ stable | 宠物照护咨询：6 主题 × 5 类常见宠物 + 8 类异宠，含强转诊边界 |
| [rider-waite-cn](./rider-waite-cn__skillhub/) | 1.0.1 | ✅ stable | 塔罗解牌：韦特体系 78 牌 × 18 牌阵中文解读（娱乐定位） |
| [fde-case-coach](./fde-case-coach/) | 1.0.0 | ✅ stable | FDE 实战营 WS1 案例教练：客户访谈 → 粗版 PRD → HTML 原型（20 轮保底交付） |
| [fde-codegen-coach](./fde-codegen-coach/) | 1.1.0 | ✅ stable | FDE 实战营 WS2 代码生成教练：PRD + 原型 → 可运行前后端应用（20 轮保底交付） |
| [fde-roadmap-coach](./fde-roadmap-coach/) | 2.0.0 | ✅ stable | FDE 实战营 WS3 产品化教练：单客户应用 → 标准化产品（15 轮保底交付） |
| [fde-self-assessment-coach](./fde-self-assessment-coach/) | 2.4.0 | ✅ stable | FDE 能力自评教练：1444 模型风格诊断，8 道情境题出六环画像与 90 天行动建议 |

## 两个系列

### 商业与生活 Skills（`*_skillhub/`）

统一的 skillhub 规范：`SKILL.md` 主入口 + `skill.json` 运行时元数据 + `_meta.json` /
`_skillhub_meta.json` + `references/` + `examples/` + `tests/`。

- **site-intelligence-report**：基于公开网络内容（web_search，零 API Key），输出 10 节结构化
  选址报告（24 字段 + 附录 A/B/C），内建 5 块必加规则与 10 场景鲁棒性设计。适用于中国大陆城市，
  海外场景在 v2.0 规划中。范本：苏州泰华·蜜雪冰城（#001）+ 成都春熙路·咖啡（#002）。
- **pet-care-cn**：面向养宠用户的结构化咨询框架，含图像识别辅助、对话上下文管理与安全边界
  （异常症状一律建议就医）。
- **rider-waite-cn**：抽卡由用户主动完成，LLM 按牌义库结构化解读，附伦理边界。

各 skill 的静态校验与 LLM 批量测试在其目录内：

```bash
python3 site-intelligence-report__skillhub/tests/pattern_checker.py
python3 pet-care-cn__skillhub/tests/pattern_checker.py
```

### FDE 实战营系列（`fde-*`）

FDE（Forward Deployed Engineer）团队实战营第一期配套教练 skill，统一规范：`SKILL.md` +
`README.md` + `CHANGELOG.md` + `metadata.json` + `assets/`。共同设计原则是**保底承诺**：
无论学员配合程度如何，轮次结束前必须交付完整产出。

- **WS1 案例教练**（`fde-case-coach`）：双角色编排——先扮演握有隐藏信息库的制造业客户接受
  访谈，再切换产品负责人产出粗版 PRD 与 HTML 原型。
- **WS2 代码生成教练**（`fde-codegen-coach`）：先冻结《方案确认单》，再逐功能生成
  FastAPI + SQLite + 原生前端的可运行应用，一条命令启动。
- **WS3 产品化教练**（`fde-roadmap-coach`）：Think Big 三步走（算市场 / 拆产品化 / 出原型图），
  内置"产品化三难"挑战；`assets/文档包/` 内含恒润精工模拟客户文档（D1–D6）。
- **能力自评教练**（`fde-self-assessment-coach`）：基于《AI-FDE 能力素养与评价体系白皮书
  （2026 版）》的风格测评，8 道情境四选一题，对话内直接出结果，不生成文件。

用法：把对应 `SKILL.md`（或 `assets/PROMPT_启动.md`）全文发给 LLM，按提示说"开始"即可。

## 适用范围与规划

- 选址 skill 主战场为中国大陆城市；海外场景在 v2.0 规划中
  （参见 [site-intelligence-report CHANGELOG Unreleased](./site-intelligence-report__skillhub/CHANGELOG.md)）。
- 后续方向：LLM 真实跑批的 CI 测试（当前仅有 pattern checker 静态分析 + 离线批量输出）、
  选址决策端到端自动化（输入地址 → 输出签约建议）。
