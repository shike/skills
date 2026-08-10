"""
GEO 雷达 Skill · 混沌测试用例

针对品牌分析 skill 输入做异常测试，验证 skill 鲁棒性：
- 输入异常：空 brand / 模糊 brand / URL 形式 / 极长 brand
- 海外场景：海外品牌 / 港澳台 / 县城
- 数据缺口：县城 / 县级市 / 行业未命中 / 新品牌
- 极端输入：极长 / 特殊字符 / 竞品过多
- 自然语言：中文 / 英文
- 重复：24h 内同品牌重复

每个 case 给出预期响应模式，由 LLM 端到端执行后检查。
"""

# 混沌测试用例
CHAOS_CASES = [
    # ============ 输入异常 ============
    {
        "name": "空 brand",
        "input": {"brand": "", "queries": None, "category": None},
        "expected_action": "必填字段,LLM 必须向用户询问 brand,不可静默继续",
    },
    {
        "name": "URL 形式 brand",
        "input": {"brand": "https://nihaovisit.com", "queries": None, "category": "旅游"},
        "expected_action": "URL → 解析为域名 'nihaovisit.com',报告按域名计算可见度",
    },
    {
        "name": "模糊 brand（含义不清）",
        "input": {"brand": "那个奶茶", "queries": None, "category": None},
        "expected_action": "模糊 brand → 询问用户明确「你说的『那个奶茶』是指哪一家?蜜雪/古茗/喜茶?」",
    },
    {
        "name": "子品牌 brand（需要明确主品牌）",
        "input": {"brand": "古茗轻乳茶", "queries": None, "category": "奶茶"},
        "expected_action": "询问用户主品牌是'古茗'还是'古茗轻乳茶'(产品线)",
    },

    # ============ 海外场景 ============
    {
        "name": "海外品牌（Starbucks）",
        "input": {"brand": "Starbucks", "queries": None, "category": "咖啡"},
        "expected_action": "v1.x 仅支持中国大陆 → verdict 强制 🔴 + verdict_reason 写明'v1.x 不支持海外场景,Starbucks 中国除外'",
    },
    {
        "name": "港澳台品牌",
        "input": {"brand": "美心 MX", "queries": None, "category": "烘焙"},
        "expected_action": "港澳台品牌 → verdict 🟡 + verdict_reason 写明'港澳台数据可参考大陆基准,但需额外验证政策差异'",
    },
    {
        "name": "县城品牌",
        "input": {"brand": "张三炒鸡店", "queries": None, "category": "餐饮", "city_hint": "湖南省衡阳市衡东县城关镇"},
        "expected_action": "县城品牌 → 数据稀缺警告 + verdict 🟡 + 报告第 7 节明示'三线及以下数据稀缺,品牌真实可见度被低估'",
    },

    # ============ 数据缺口 ============
    {
        "name": "行业未命中 8 行业（法律）",
        "input": {"brand": "某律师事务所", "queries": None, "category": "法律"},
        "expected_action": "法律行业不在 8 行业 baseline → 降级通用模板(20 个),verdict 强制 🟡(通用模板精度低)",
    },
    {
        "name": "新成立品牌（2026-01 成立）",
        "input": {"brand": "新茶饮 startupX", "queries": None, "category": "奶茶"},
        "expected_action": "新品牌数据稀缺 → verdict 🔴(可见度几乎为 0)+ 给出'如何从 0 到 1 建立 GEO 基础'的具体建议",
    },
    {
        "name": "个人 IP 品牌",
        "input": {"brand": "李教授讲 AI", "queries": None, "category": None},
        "expected_action": "个人 IP 品牌 → 启动 web_search 跑批,如果数据稀缺,verdict 🟡,给出'个人 IP 在知乎/公众号发内容'的具体建议",
    },

    # ============ 极端输入 ============
    {
        "name": "极长 brand（300+ 字）",
        "input": {"brand": "蜜雪冰城(中国)有限公司旗下品牌蜜雪冰城新茶饮子品牌蜜雪冰城轻乳茶系列2026年新推出", "queries": None, "category": "奶茶"},
        "expected_action": "极长 brand → LLM 识别为 '蜜雪冰城' + 提示'你给的 brand 过长,是否指 蜜雪冰城?'",
    },
    {
        "name": "特殊字符 brand",
        "input": {"brand": "蜜雪冰城!@#$%", "queries": None, "category": "奶茶"},
        "expected_action": "特殊字符 → LLM 提取核心 '蜜雪冰城',标'已清洗 brand'",
    },
    {
        "name": "竞品过多（12 个，含自身）",
        "input": {"brand": "蜜雪冰城", "queries": None, "category": "奶茶", "competitors": ["古茗", "喜茶", "益禾堂", "茶百道", "沪上阿姨", "霸王茶姬", "奈雪", "乐乐茶", "一点点", "CoCo", "快乐柠檬", "蜜雪冰城"]},
        "expected_action": "竞品过多 → 提示'竞品超过 10 个,可能影响报告可读性,建议保留 5-10 个' + 默认保留前 10 个 + 自身作为竞品去重",
    },

    # ============ 自然语言 ============
    {
        "name": "中文自然语言",
        "input": {"input_text": "帮我看下蜜雪冰城在 AI 搜索里被提到多少"},
        "expected_action": "LLM 解析为 {brand: '蜜雪冰城', category: '奶茶', queries: null} + 向用户确认 1 次(品牌已确定)+ 启动跑批",
    },
    {
        "name": "英文自然语言",
        "input": {"input_text": "Check how many times Mixue appears in AI search"},
        "expected_action": "v1.x 仅支持中文输入 → 提示'暂仅支持中文输入,Mixue → 蜜雪冰城' + 启动跑批",
    },

    # ============ 重复 ============
    {
        "name": "同品牌 24h 内重复",
        "input": {"brand": "蜜雪冰城", "queries": None, "category": "奶茶", "history": "24h 内已查过蜜雪冰城"},
        "expected_action": "检测到 24h 内重复 → 提示'近期已分析过,是否要更新数据?(数据可能 24h 变化 0-3%)'",
    },
]
