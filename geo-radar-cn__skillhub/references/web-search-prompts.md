# web_search Prompt 模板库

GEO 雷达的 web_search 调用 prompt 模板。每个模板针对不同查询词类型,确保 LLM 输出格式一致。

---

## 通用结构

每个 prompt 包含 4 部分:
1. **角色定位**:LLM 在本次搜索中扮演什么
2. **查询词**:要搜什么
3. **输出格式**:JSON / 自然语言 / 特定字段
4. **质量约束**:不编造、标时效、标来源

---

## 1. 推荐型查询词 prompt

```yaml
role: "你是一个 web_search 助手,任务是为品牌 '{brand}' 调研 AI 搜索推荐情况"
query: "{query}"
output_format:
  results: "top 5-10 个搜索结果"
  fields:
    - url: "完整 URL"
    - title: "网页标题"
    - snippet: "前 200 字摘要"
    - published_at: "发布时间(YYYY-MM)"
    - domain: "域名"
    - platform: "平台类型(知乎/小红书/官网/媒体/...)"
  brand_appearance:
    mentioned: "true/false"
    position: "在 snippet 中出现的位置(1=标题,2=前 100 字,3=中段,4=末尾,5=未出现)"
    context: "上下文(被怎么提及:推荐/对比/介绍/批判)"
quality_constraints:
  - "数据时效必须标 🟢/🟡/🟠/🔴"
  - "URL 必须可访问,无来源 URL 的结果丢弃"
  - "snippet 中确实出现 {brand} 字符串才算 mentioned=true"
```

---

## 2. 对比型查询词 prompt

```yaml
role: "你是一个 web_search 助手,任务是对比 '{brand}' 和 '{competitor}' 在 AI 搜索中的表现"
query: "{query}"
output_format:
  results: "top 5-10 个搜索结果,优先排序(包含两品牌的 > 只包含一品牌的)"
  fields:
    - url: "完整 URL"
    - title: "网页标题"
    - snippet: "前 200 字摘要"
    - published_at: "发布时间(YYYY-MM)"
    - domain: "域名"
    - platform: "平台类型"
  brand_comparison:
    - main_brand_mentioned: "true/false(指 {brand})"
    - competitor_mentioned: "true/false(指 {competitor})"
    - comparison_focus: "对比维度(价格/口味/服务/...)"
    - winner: "哪方被推荐为更优"
quality_constraints:
  - "对比内容必须明确说出两方优缺点,不算 winner 的丢弃"
  - "主观偏好不算(只统计事实性对比)"
```

---

## 3. 痛点型查询词 prompt

```yaml
role: "你是一个 web_search 助手,任务是为 '{brand}' 调研用户痛点和解决方案被引用的频次"
query: "{query}"
output_format:
  results: "top 5-10 个搜索结果"
  fields:
    - url: "完整 URL"
    - title: "网页标题"
    - snippet: "前 200 字摘要"
    - published_at: "发布时间(YYYY-MM)"
    - domain: "域名"
    - platform: "平台类型"
  brand_appearance:
    mentioned: "true/false"
    position: "1-5(同推荐型)"
    context: "是否作为'解决方案'被引用(而不是被批判)"
quality_constraints:
  - "优先找'解决方案'型内容(攻略/教程/对比),不找'避雷'型"
  - "品牌作为'解决方案'被引用 = 强信号;作为'问题'被引用 = 弱信号"
```

---

## 4. 决策型查询词 prompt

```yaml
role: "你是一个 web_search 助手,任务是为 '{brand}' 调研在 '{scenario}' 场景下被推荐的频次"
query: "{query}"
output_format:
  results: "top 5-10 个搜索结果,优先排序(场景匹配的 > 不匹配的)"
  fields:
    - url: "完整 URL"
    - title: "网页标题"
    - snippet: "前 200 字摘要"
    - published_at: "发布时间(YYYY-MM)"
    - domain: "域名"
    - platform: "平台类型"
  brand_appearance:
    mentioned: "true/false"
    position: "1-5(同推荐型)"
    context: "在该场景下被推荐的程度"
quality_constraints:
  - "场景不匹配的内容(如'学生党'场景下出现'商务'内容)不算"
  - "品牌在该场景下被强推荐(标题或前 100 字)才算 mentioned=true"
```

---

## 5. 行业资讯型查询词 prompt(补充)

```yaml
role: "你是一个 web_search 助手,任务是为 '{brand}' 调研行业相关报道和讨论"
query: "{query}"
output_format:
  results: "top 5-10 个搜索结果,优先媒体/行业研究"
  fields:
    - url
    - title
    - snippet
    - published_at
    - domain
    - platform
    - source_level: "🏛️ 官方 / 📊 行业 / 📰 媒体 / 🏪 平台 / 👤 UGC"
  brand_appearance:
    mentioned: "true/false"
    context: "品牌在行业中的地位/排名/趋势"
quality_constraints:
  - "优先 🏛️ 官方 / 📊 行业 来源"
  - "数据时效优先 🟢 6 月内"
```

---

## 6. 竞品对标查询词 prompt

```yaml
role: "你是一个 web_search 助手,任务是对比 '{brand}' 与行业前 10 品牌的可见度"
query: "{competitor_name} 怎么样 {category}"
output_format:
  results: "top 5-10 个搜索结果"
  fields: "(同推荐型)"
  brand_appearance:
    main_brand_mentioned: "true/false(指 {brand})"
    competitor_mentioned: "true/false(指 {competitor_name})"
    position_diff: "main_brand 与 competitor 在结果中的位置差"
quality_constraints:
  - "同一结果同时包含两品牌,才算'对比';否则分开统计"
```

---

## 输出 JSON Schema

每次 web_search 调用的标准输出格式:

```json
{
  "query": "原始查询词",
  "query_type": "推荐型/对比型/痛点型/决策型/行业资讯型",
  "results": [
    {
      "url": "https://...",
      "title": "...",
      "snippet": "...",
      "published_at": "YYYY-MM",
      "domain": "...",
      "platform": "...",
      "source_level": "🏛️/📊/📰/🏪/👤",
      "freshness": "🟢/🟡/🟠/🔴",
      "brand_appearance": {
        "mentioned": true,
        "position": 2,
        "context": "..."
      }
    }
  ],
  "summary": {
    "total_results": 8,
    "main_brand_mentions": 3,
    "main_brand_hit_rate": "37.5%",
    "main_brand_avg_position": 2.3
  }
}
```

---

## 单次跑批成本估算

| 查询词类型 | 数量 | 单次 cost | 总 cost |
|---|---|---|---|
| 推荐型 | 5-7 | ~5 results | 25-35 results |
| 对比型 | 5-7 | ~5 results × 5 个竞品 | 125-175 results |
| 痛点型 | 5-7 | ~5 results | 25-35 results |
| 决策型 | 5-7 | ~5 results | 25-35 results |
| 行业资讯型 | 0-5 | ~5 results | 0-25 results |
| **合计** | **20-30** | — | **200-300 results** |

每次 web_search 调用 ~2-5 秒,单次跑批 8-25 分钟。
