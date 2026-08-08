# 联网搜索 Prompt 模板

每个字段对应一个独立 prompt。LLM 根据 schema 中的字段触发对应搜索，收集公开数据填充字段。平台能力边界（web_search 拿不到的内容）见 `SKILL.md` Step 2。

## 共享变量

所有 prompt 共享：

- `{brand}` / `{address}` / `{city}` / `{category}` — 用户输入
- `{expected_rent}` / `{expected_area}` — 用户输入（可选）
- `{address_type}` / `{area}` — LLM 推断
- `{category_defaults}` — 行业基准（客单价/食材成本率/装修单价）
- `{labor_per_sqm}` — 城市+品类基准
- `{traffic_estimate}` — 字段 6 人流估算结果

---

## 字段 1：summary.verdict（综合判断）

```
# 任务
对 {brand} 在 {address} 开店给出综合判断（🟢/🟡/🔴）。

# 关键词
"{address} 客流"、"{address} {category} 经营状况"、"{商圈} {category} 失败案例"

# 输出
- verdict: 🟢/🟡/🔴
- verdict_reason: 1 句话（≤ 50 字）
```

## 字段 2：summary.conclusion_3sentences（3 句话结论）

```
# 任务
3 句话总结：现状 + 财务 + 行动建议。每句 ≤ 60 字，必须有数据支撑。

# 输出
- 3 句话数组
```

## 字段 3：location.business_district（商圈名）

```
# 任务
识别 {address} 所在商圈。

# 关键词
"{address} 商圈"、"{address} 属于哪个商圈"

# 输出
- business_district: 字符串
```

## 字段 4：location.location_history（同位置历史门店）

```
# 任务
收集 {address} 历史经营门店（品牌/业态/开业-关店时间/原因）。

# 关键词
"{address} 原门店"、"{address} 商铺历史"、"{address} 之前是什么店"

# 输出
- previous_tenants: 数组（名称/品牌/业态/存活时间/关店原因）
- 至少 1 条
```

## 字段 5：competitor.top_5（Top 5 竞品）

```
# 任务
列出 {address} 周边 500m 内 {category} 同品类门店。

# 关键词
"{address} 周边 {category}"、"{商圈} {category} 排名"

# 输出
- 至少 3 家，最多 5 家
- 排序：评分或知名度
- 字段：名称/距离/评分/客单价/经营时长
```

## 字段 6：traffic.daily_traffic_estimate（日均人流）

```
# 任务
估算 {address} 日均人流量（工作日/周末/节假日）。

# 关键词
"{address} 客流"、"{商场名} 客流 报告"、"{商圈} 周末人流量"

# 输出
- 工作日：区间估算
- 周末：区间估算
- 节假日：区间估算
- 找不到写「未找到公开人流数据」
```

## 字段 7：traffic.peak_hours（高峰时段）

```
# 任务
确定 {address} 客流高峰时段。

# 关键词
"{商场名} 高峰时段"、"{地址} 周边 午高峰"、"{品类} 高峰时段"

# 输出
- 数组：["工作日 12:00-13:30", "周末 14:00-21:00"]
- 至少 1 个时段
```

## 字段 8：operations.closed_stories（关店案例）

```
# 任务
收集 {city} {category} 品类 2024-2026 年关店案例。

# 硬约束
- 时间：2024 年 1 月之后
- 品类：必须直接与 {category} 相关
- 城市：必须发生在 {city}

# 关键词
"{category} {city} 关店 2024"、"{category} {city} 关店 2025"、"{商场名} {category} 关闭"、"{品牌} 收缩 2024-2026"

# 输出
- 至少 1 条，最好 3 条
- 字段：品牌/位置/关店时间/原因（原文摘录 ≤ 100 字）/来源链接
- 找不到写「未找到该品类在该城市 2024-2026 年公开关店案例」
```

## 字段 9：risk.demolition_risk（拆迁风险）

```
# 任务
评估 {address} 拆迁风险。

# 关键词
"{address} 拆迁"、"{city} {address} 规划"、"{商场名} 拆迁"

# 输出
- demolition_risk: 低/中/高
- 依据 + 来源
```

## 字段 10：risk.policy_risk（政策风险）

```
# 任务
评估 {address} 餐饮政策风险（监管/油烟/食品安全）。

# 关键词
"{city} 餐饮管理办法"、"{city} 油烟排放标准"、"{city} {category} 新规"

# 输出
- policy_risk: 低/中/高
- 依据 + 来源
```

## 字段 11：finance.rent_estimate（租金估算）

```
# 任务
基于 {address} 同商圈公开房源估算合理月租。

# 关键词
"{address} 商铺出租"、"{商圈} 30㎡ 商铺 月租"、"{商圈} 临街商铺 价格"

# 输出
- rent_estimate: {min_yuan, max_yuan} 月租
- 中位数 + P25/P75
- 至少 5 个房源样本
```

## 字段 12：finance.breakeven_months_estimate（回本周期）

```
# 任务
基于字段 11 租金 + 行业基准计算回本周期。

# 内部计算
- 客单价 = {category_defaults.price}
- 食材成本率 = {category_defaults.food_cost_ratio}
- 月营收 = 客单价 × 日均杯数 × 30
- 月净利 = 月营收 - 月成本（房租 + 人工 + 食材 + 水电）
- 回本月数 = 总投资 / 月净利

# 输出
- breakeven_months: 整数
```

## 字段 13：negotiation.rent_benchmark（同商圈租金行情）

复用字段 11 输出（已包含中位数/P25/P75），本字段无需独立搜索。如字段 11 数据不足，补充搜索以下关键词。

```
# 任务
统计 {address} 同商圈租金行情（中位数/P25/P75），用于谈判对标。

# 关键词（仅当字段 11 数据不足时使用）
"{商圈} 商铺租金 行情"、"{商圈} 临街 30㎡ 商铺"

# 输出
- median, p25, p75 月租（与字段 11 一致）
- 数据来源
```

## 字段 14：negotiation.rent_negotiation_room（压价空间）

```
# 任务
基于关店案例 + 公开房源评估压价空间。

# 关键词
"{address} 周边 商铺 转让"、"{address} 空置商铺"、"{商场名} 餐饮 关店"

# 输出
- 压价空间：当前报价 → 目标价
- 依据
```

## 字段 15：action.must_verify_on_site（必须现场验证）

```
# 任务
列出 {address} 签约前必须现场验证的事项。

# 输出
- 8 项硬约束核查（参考 schema 附录 C-3）
- 3-5 条否决红线
- 行动按 3 类分（立即做 / 验证 / 否决）
- 每条 4 维评估（成本/收益/风险/决策可执行性）
```

## 字段 16：action.can_negotiate（可谈判点）

```
# 任务
列出 {address} 可谈判点（租金/免租期/装修期/转让费）。

# 关键词
"{address} 商铺 议价空间"、"{商场名} 餐饮 装修期"

# 输出
- 4-6 个可谈判点
- 字段：项目/目标/依据
```

## 字段 17：alternatives.recommend_category_swap（verdict = 🔴 且原因为财务时触发）

```
# 任务
基于 {address} 特征推断 Top 3 替代品类。

# 输出
- top_3_categories: 3 个
- 字段：品类/适配理由/预期月净利变化/数据来源
```

## 字段 18：finance.breakeven_volume（盈亏平衡日销量）

```
# 任务
计算盈亏平衡日销量 + 3x3 敏感性矩阵。

# 内部计算
盈亏平衡月销量 = 固定成本 / (客单价 - 单位变动成本)

# 3x3 矩阵
至少 1 个客单价档位的 3x3 矩阵（房租 × 客流 9 场景）
每个格子标"月净利润数字"
标亏损/临界/健康场景数

# 输出
- breakeven_daily_volume, breakeven_monthly_volume
- breakeven_assumptions: 固定成本+变动成本+客单价
- 3x3 矩阵
- 关键发现：盈亏平衡日销量
```

## 字段 19：finance.cashflow_6months（前 6 月现金流）

```
# 任务
预测前 6 月现金流（爬坡假设 30% → 100%）。

# 输出
- 6 行表格：月份/月营收/月成本/净现金流/累计现金流
- 关键提示：开业一次性投入/月固定成本/现金流回正月/准备资金建议
```

## 字段 20：data.rent_listings_58（58 同城/安居客公开房源）

```
# 任务
收集 {address} 同商圈 5-10 个公开房源。

# 关键词
"{address} 商铺出租 58同城"、"{商圈} 临街商铺 安居客"

# 输出
- 至少 5-10 个房源
- 字段：地址/面积/月租/单价（元/㎡/天）/来源链接/类型（临街/商场内/社区底商）
```

## 字段 21：data.delivery_volume（外卖月销）

```
# 任务
收集 {address} 周边同品类竞品外卖月销。

# 关键词
"{address} 周边 {category} 美团"、"{品牌} {address} 饿了么"

# 输出
- 至少 1 个竞品
- 字段：品牌/地址/美团月销/饿了么月销/起送价/来源
```

## 字段 22：risk.risk_score_card（风险评分卡）

```
# 任务
基于 6 维度用概率 × 影响矩阵评估风险。

# 6 维度
拆迁/政策/竞品/客流/财务/品类适配

# 输出
- 6 行表格：维度/概率/影响/风险分/主要依据
- 风险综合分 = 6 维加权和
- 关键高风险维度标注
```

## 字段 23：data.seasonality_index（季节性 + 生命周期）

```
# 任务
基于品类行业基准给出 12 月季节性曲线 + 开业 12 月生命周期。

# 行业基准
见 `report-schema.md` 字段 23（单一来源，避免重复维护）。

# 输出
- seasonality_curve: 12 月系数
- peak_months / low_months
- lifecycle_curve: 1-12 月爬坡/稳定
- critical_months: [3, 6]
```

## 字段 24：negotiation.talking_points（谈判话术）

```
# 任务
基于字段 20 公开房源 + 字段 8 关店案例生成 ≥ 3 条谈判话术。

# 话术结构
- point: 谈判要点
- script: 实际话术
- evidence: 依据链接
- expected_outcome: 成功/部分成功/被拒

# 必含话术类型
1. 基于公开房源压租金
2. 基于关店案例压租金
3. 争取免租期
4. （可选）基于季节性争取
```

---

## 多地址对比 prompt

触发：`addresses.length > 1`。

```
# 任务
对 N 个候选地址横向对比，输出 1 张对比矩阵 + 1 份综合推荐 + N 份精简报告。

# 流程
1. 对每个地址并行调用字段 1-24 搜索（复用相同品类搜索结果）
2. 汇总关键指标
3. 生成对比矩阵
4. 基于综合分排序输出最终推荐
5. 每个地址生成精简报告（仅 摘要卡 + 财务 + 风险 + 行动清单）

# 对比矩阵字段
月租 / 周边竞品数 / 日均人流 / 关店案例 / 财务回本 / 风险综合分 / 谈判空间 / 综合推荐度

# 推荐逻辑权重
- 财务回本 25%
- 风险综合分 20%
- 客流 15%
- 竞品密度 15%
- 谈判空间 10%
- 租金 10%
- 关店案例 5%
```
