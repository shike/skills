# 回答模板索引(qa-templates)

> **版本**:v0.3
> **覆盖范围**:17 个模板文件,85 个完整范例(5 物种 × 3 月龄 × 5 主题 + 5 物种 × 2 月龄 × 1 主题)
> **用途**:SKILL.md 主工作流根据用户输入加载对应模板

## 1. 模板总览

| 主题 | 模板 ID 前缀 | 文件 | 范例数 | 覆盖月龄 |
|---|---|---|---|---|
| 1 饮食 | `diet-` | [`diet-junior.md`](./qa-templates/diet-junior.md) [`diet-adult.md`](./qa-templates/diet-adult.md) [`diet-senior.md`](./qa-templates/diet-senior.md) | 15 | 幼/成/老 |
| 2 驱虫与疫苗 | `dv-` | [`dv-junior.md`](./qa-templates/dv-junior.md) [`dv-adult.md`](./qa-templates/dv-adult.md) [`dv-senior.md`](./qa-templates/dv-senior.md) | 15 | 幼/成/老 |
| 3 绝育与生育 | `neuter-` | [`neuter-junior.md`](./qa-templates/neuter-junior.md) [`neuter-adult.md`](./qa-templates/neuter-adult.md) [`neuter-senior.md`](./qa-templates/neuter-senior.md) | 15 | 幼/成/老 |
| 4 行为与训练 | `beh-` | [`beh-junior.md`](./qa-templates/beh-junior.md) [`beh-adult.md`](./qa-templates/beh-adult.md) [`beh-senior.md`](./qa-templates/beh-senior.md) | 15 | 幼/成/老 |
| 5 新宠到家 | `arrival-` | [`arrival-junior.md`](./qa-templates/arrival-junior.md) [`arrival-adult.md`](./qa-templates/arrival-adult.md) [`arrival-senior.md`](./qa-templates/arrival-senior.md) | 15 | 幼/成/老 |
| 6 老年照护 | `senior-care-` | [`senior-care-adult.md`](./qa-templates/senior-care-adult.md) [`senior-care-senior.md`](./qa-templates/senior-care-senior.md) | 10 | 仅成/老 |
| **合计** | | **17 文件** | **85 范例** | |

## 2. 调度规则

SKILL.md 收到用户输入后,按以下规则加载模板:

```
输入:{species, topic, age_stage}
↓
匹配模板:{topic}-{age_stage}.md
↓
加载对应物种章节:## {N}. {物种中文}({species英文})| {月龄}{主题名}
↓
套用 6 节输出结构
```

**特殊情况**:
- `topic=senior-care` 且 `age_stage=junior` → **返回**:「本主题不适用于幼龄阶段,可咨询其他 5 主题」
- 物种不在 5 类(猫/狗/兔/鸟/鼠)内 → **返回**:「本 skill v1 不支持该物种」

## 3. 6 节输出结构(全模板统一)

每个范例固定 6 节:

| 节 | 名称 | 长度 | 关键要求 |
|---|---|---|---|
| 1 | 场景定位 | 1 段 50-100 字 | 「你问的是 X 物种 Y 月龄的 Z 问题,核心是...」 |
| 2 | 核心建议 | 3-5 条编号 | 带粗体关键短语,直接可执行 |
| 3 | 关键参数 | Markdown 表格 | 数字具体(时间/剂量/频率/温度) |
| 4 | 常见误区 | 2-4 条 ❌ | 粗体错误做派 |
| 5 | 风险信号 | 5-7 条 | 急症标"立即就医"或"急症" |
| 6 | 兽医转介触发器 | 4-6 条 | 本回答的边界声明 |

**字数每范例**:600-1200 字(实际产出 1000-1500 字,因物种差异较大)

## 4. 跨模板硬约束(全 17 文件必须遵守)

1. **不诊断**:看到症状关键词,首段/风险信号必须转介兽医
2. **不开药**:不推荐任何商品名药物剂量,只给成分类别 + 建议就医
3. **不替代训练师/行为学家**:严重行为问题持续攻击/自残/严重破坏 → 转介
4. **不老调重弹**:基于 context 调整,不照抄模板
5. **不画大饼**:不预测"一定能治好",只给概率
6. **不遗忘隐私**:用户问题/宠物信息不写入永久记忆
7. **不渲染悲伤**:临终段落允许 1-2 句温和边界提示,不写"陪伴它走完最后一程"

## 5. 物种月龄特异表(全模板共用基线)

| 物种 | 幼(`junior`) | 成(`adult`) | 老(`senior`) |
|---|---|---|---|
| 猫(cat)| < 1 岁 | 1-10 岁 | > 10 岁 |
| 狗(dog,小型)| < 1 岁 | 1-10 岁 | > 10 岁 |
| 狗(dog,大型)| < 1.5 岁 | 1.5-7 岁 | > 7 岁 |
| 兔(rabbit)| < 6 月 | 6 月-5 岁 | > 5 岁 |
| 鸟(bird,中小型)| < 1 年 | 1-8 年 | > 8 年 |
| 鸟(bird,大型)| < 2 年 | 2-15 年 | > 15 年 |
| 仓鼠(rodent,仓鼠)| < 3 月 | 3-18 月 | > 18 月 |
| 豚鼠(rodent,豚鼠)| < 6 月 | 6 月-4 岁 | > 4 岁 |
| 花枝鼠(rodent,花枝鼠)| < 4 月 | 4-18 月 | > 18 月 |

> 详细物种差异见各模板的"月龄定义"标注。

## 6. 场景 ID 命名规范(全模板统一)

- **5 个 3 段主题**(diet/dv/neuter/beh/arrival):`{species}-{topic}-{age}-01`
  - 例:`cat-diet-junior-01`、`dog-neuter-senior-01`
- **1 个 4 段主题**(senior-care):`{species}-senior-care-{age}-01`
  - 例:`cat-senior-care-senior-01`

完整 90 场景索引见 [`topics-and-species.md`](./topics-and-species.md)

## 7. 模板版本

- **当前版本**:v0.3.1
- **下次更新触发**:v0.4(safe-boundary 落地)/ v0.5(SKILL.md 主体)/ v0.6(examples)
- **更新策略**:每范例头部标注 `> 模板版本:v0.3.1`,整体版本变更记录在 [CHANGELOG.md](../../CHANGELOG.md)

## 8. 已知边界与未覆盖

| 边界 | 处理 |
|---|---|
| 跨主题问题(如"我家猫不吃东西还呕吐") | 优先用 `diet` 模板,在"风险信号"中显式转介兽医 |
| 跨物种问题(同家庭多物种) | 按用户主诉的物种加载,其他物种在兽医转介段提示 |
| 鸟类/鼠类驱虫 | dv 模板已说明"鸟类不常规内驱""鼠类驱虫药不适用老年" |
| 鸟类/鼠类绝育 | neuter 模板已说明"鸟类不手术""鼠类不推荐" |
| 老年照护幼龄 | 直接返回"本主题不适用" |
| 临终/丧亲情感 | senior-care 模板已给共情 + 转介引导,不在本 skill 做心理辅导 |
| 商业产品推荐 | 全模板禁止推荐任何具体商品品牌(动物医院/药物/用品),由兽医/用户决定 |
| 地区差异(如中国/海外)| 多数建议为通用养宠共识;涉及法规(如狂犬)以"中国大部分城市"作限定 |

## 9. 调用示例

```markdown
用户输入:「我家 3 个月的英短幼猫刚到家,怎么照顾?」

SKILL.md 调度:
- species = cat
- topic = arrival(用户说"刚到家")
- age_stage = junior(3 个月)
- ↓
- 加载文件:references/qa-templates/arrival-junior.md
- ↓
- 加载章节:## 1. 猫(cat)| 幼龄驱虫与首免 → 注意:这里 species=cat 不是 first topic arrival
- 实际加载:## 1. 猫(cat)| 幼龄新宠到家
- ↓
- 套用 6 节结构,生成回答
- context:英短 + 3 月 → 在"核心建议"中加入"英短注意 HCM 筛查"(待 v0.5 完善 context 适配)
```

> context 适配(品种/体重/已确诊疾病)在 v0.5 SKILL.md 主体中实现,模板文件保持物种通用。
