# 混沌测试用例

GEO 雷达的异常输入测试,验证 skill 鲁棒性。每个 case 给出预期响应模式。

---

## 用例分类(共 16 个)

| 分类 | 数量 | 用途 |
|---|---|---|
| 输入异常 | 4 | 缺/错 brand / URL 形式 / 模糊 brand |
| 海外场景 | 3 | 海外品牌 / 港澳台 / 县城 |
| 数据缺口 | 3 | 县城 / 县级市 / 行业未命中 |
| 极端输入 | 3 | 极长 brand / 特殊字符 / 竞品过多 |
| 自然语言 | 2 | 中文 / 英文 |
| 重复 | 1 | 同一品牌 24h 内重复查询 |

---

## 1. 输入异常(4 个)

### 1.1 空 brand

```yaml
input:
  brand: ""
  queries: null
expected_action: "必填字段,LLM 必须向用户询问 brand,不可静默继续"
```

### 1.2 URL 形式 brand

```yaml
input:
  brand: "https://nihaovisit.com"
  queries: null
expected_action: "URL → 解析为域名 'nihaovisit.com',报告按域名计算可见度"
```

### 1.3 模糊 brand(含义不清)

```yaml
input:
  brand: "那个奶茶"
  queries: null
expected_action: "模糊 brand → 询问用户明确'你说的"那个奶茶"是指哪一家?蜜雪/古茗/喜茶?'"
```

### 1.4 brand 是子品牌,需要明确主品牌

```yaml
input:
  brand: "古茗轻乳茶"
  queries: null
expected_action: "询问用户主品牌是'古茗'还是'古茗轻乳茶'(产品线),如产品线,verdict 强制 🟡"
```

---

## 2. 海外场景(3 个)

### 2.1 海外品牌(星巴克)

```yaml
input:
  brand: "Starbucks"
  category: "咖啡"
  queries: null
expected_action: "v1.x 仅支持中国大陆 → verdict 强制 🔴 + verdict_reason 写明'v1.x 不支持海外场景,Starbucks 中国除外'"
```

### 2.2 港澳台品牌

```yaml
input:
  brand: "美心 MX"
  queries: null
expected_action: "港澳台品牌 → verdict 🟡 + verdict_reason 写明'港澳台数据可参考大陆基准,但需额外验证政策差异'"
```

### 2.3 县城品牌

```yaml
input:
  brand: "张三炒鸡店"
  city_hint: "湖南省衡阳市衡东县城关镇"
expected_action: "县城品牌 → 数据稀缺警告 + verdict 🟡 + 报告第 7 节明示'三线及以下数据稀缺,品牌真实可见度被低估'"
```

---

## 3. 数据缺口(3 个)

### 3.1 行业未命中 8 行业

```yaml
input:
  brand: "某律师事务所"
  category: "法律"
  queries: null
expected_action: "法律行业不在 8 行业 baseline → 降级通用模板(20 个),verdict 强制 🟡(通用模板精度低)"
```

### 3.2 新成立品牌(2026-01 成立)

```yaml
input:
  brand: "新茶饮 startupX"
  category: "奶茶"
  queries: null
expected_action: "新品牌数据稀缺 → verdict 🔴(可见度几乎为 0)+ 给出'如何从 0 到 1 建立 GEO 基础'的具体建议"
```

### 3.3 个人 IP 品牌

```yaml
input:
  brand: "李教授讲 AI"
  queries: null
expected_action: "个人 IP 品牌 → 启动 web_search 跑批,如果数据稀缺,verdict 🟡,给出'个人 IP 在知乎/公众号发内容'的具体建议"
```

---

## 4. 极端输入(3 个)

### 4.1 极长 brand

```yaml
input:
  brand: "蜜雪冰城(中国)有限公司旗下品牌蜜雪冰城新茶饮子品牌蜜雪冰城轻乳茶系列"
expected_action: "极长 brand → LLM 识别为 '蜜雪冰城' + 提示'你给的 brand 过长,是否指 蜜雪冰城?'"
```

### 4.2 特殊字符

```yaml
input:
  brand: "蜜雪冰城!@#$%"
expected_action: "特殊字符 → LLM 提取核心 '蜜雪冰城',标'已清洗 brand'"
```

### 4.3 竞品过多

```yaml
input:
  brand: "蜜雪冰城"
  category: "奶茶"
  competitors: ["古茗", "喜茶", "益禾堂", "茶百道", "沪上阿姨", "霸王茶姬", "奈雪", "乐乐茶", "一点点", "CoCo", "快乐柠檬", "蜜雪冰城"]
expected_action: "竞品过多 → 提示'竞品超过 10 个,可能影响报告可读性,建议保留 5-10 个' + 默认保留前 10 个 + 自身作为竞品去重"
```

---

## 5. 自然语言(2 个)

### 5.1 中文自然语言

```yaml
input_text: "帮我看下蜜雪冰城在 AI 搜索里被提到多少"
expected_action: "LLM 解析为 {brand: '蜜雪冰城', category: '奶茶', queries: null} + 向用户确认 1 次(品牌已确定)+ 启动跑批"
```

### 5.2 英文自然语言

```yaml
input_text: "Check how many times Mixue appears in AI search"
expected_action: "v1.x 仅支持中文输入 → 提示'暂仅支持中文输入,Mixue → 蜜雪冰城' + 启动跑批"
```

---

## 6. 重复(1 个)

### 6.1 同品牌 24h 内重复

```yaml
input:
  brand: "蜜雪冰城"
  queries: null
history: "24h 内已查过蜜雪冰城"
expected_action: "检测到 24h 内重复 → 提示'近期已分析过,是否要更新数据?(数据可能 24h 变化 0-3%)'"
```

---

## 验证方式

每个 chaos case 跑完后,验证 3 个维度:

1. **行为正确**:LLM 行为符合 expected_action
2. **不崩溃**:无 stack trace / 无静默错误
3. **不编造**:无"未找到公开数据"的数据填充

```bash
# chaos test 跑批
python3 tests/chaos/test_chaos.py
# 期望：✅ 16 pass / 0 ❌
```
