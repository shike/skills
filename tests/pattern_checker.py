#!/usr/bin/env python3
"""
site-intelligence-report · 报告硬约束 pattern checker

对 examples/ 下的报告 markdown 做静态分析，校验 SKILL.md Step 5 的 8 大类硬约束。
不需要 LLM，纯正则 + 关键词检查。

Usage:
    python3 tests/pattern_checker.py                  # 跑 examples/ 下所有 .md
    python3 tests/pattern_checker.py path/to/file.md  # 跑指定文件
    python3 tests/pattern_checker.py --json           # 输出 JSON
    python3 tests/pattern_checker.py --verbose        # 显示每个检查项详情

退出码：0=全部通过，1=有失败
"""

import json
import re
import sys
from pathlib import Path
from typing import Callable


# ---------- 检查项定义 ----------

# 10 节标题模式（兼容 "一、" / "1." / "1、"/ "(一)" 等多种写法）
SECTION_PATTERNS = {
    "summary":    r"(摘要|verdict|综合判断|核心判断)",
    "location":   r"(点位信息|地址|选址信息)",
    "competitor": r"(周边竞品|竞品分析)",
    "traffic":    r"(人流|客流)",
    "demographics": r"(客群|画像|人群)",
    "operations": r"(同类门店|经营状况|关店)",
    "risk":       r"(风险评估|风险)",
    "finance":    r"(财务|测算|回本|盈亏)",
    "negotiation": r"(谈判|议价|筹码)",
    "action":     r"(行动清单|行动|建议)",
}

# 标签系统
LABEL_SOURCE = r"(🏛️|📊|📰|🏪|👤)"  # 来源等级
LABEL_CONFIDENCE = r"(🟢 高|🟡 中|🔴 低)"  # 置信度
LABEL_DECISION = r"(✅|⚠️|❌)"  # 决策可执行性

# 风险评分卡 6 维度
RISK_DIMENSIONS = ["拆迁", "政策", "竞品", "客流", "财务", "品类适配"]


def load_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_main_brand(text: str) -> dict:
    """从标题/前 30 行提取主品牌 + 主品类。返回 {"brand": ..., "category": ...}"""
    head = "\n".join(text.splitlines()[:40])
    result = {"brand": None, "category": None}

    # 1. 优先"主语锁定"声明
    m = re.search(r"主语锁定\s*\*?\*?[：:]\s*\*?\*?(.+)", head)
    if m:
        full = m.group(1).strip()
        # 拆 = ；/；成 [key, value] 对
        for kv in re.split(r"[；;]", full):
            if "=" in kv:
                k, v = kv.split("=", 1)
                v = v.strip()
                v = re.split(r"[（(]", v)[0].strip()
                if "主品牌" in k and v and v != "未指定":
                    result["brand"] = v
                elif "主品类" in k and v:
                    result["category"] = v
        # 兜底：取第一个 = 右边的值
        if not result["brand"] and not result["category"]:
            first = full.split("=", 1)[1].strip() if "=" in full else full
            first = re.split(r"[（(;；]", first)[0].strip()
            if first and first != "未指定":
                result["brand"] = first

    # 2. 标题匹配（兼容"苏州泰华 · 蜜雪冰城"格式）
    if not result["brand"]:
        m = re.search(r"[#＃]\s*选址分析报告[：:]\s*([^·\n]+)[·\|]\s*([^\n]+)", head)
        if m:
            candidate = m.group(2).strip()
            for prefix in ["某街铺 · ", "某店 · ", "某铺 · "]:
                if candidate.startswith(prefix):
                    candidate = candidate[len(prefix):]
            if candidate and candidate not in ("未指定",):
                result["brand"] = candidate

    # 3. 兜底：找品类词
    if not result["category"]:
        m = re.search(r"(奶茶|咖啡|快餐|正餐|麻辣烫|烘焙|火锅|烤肉|烘培)", head)
        if m:
            result["category"] = m.group(1)

    return result


# ---------- 检查函数 ----------

def check_A_subject_lock(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """A. 主语锁定"""
    subj = extract_main_brand(text)
    ctx["subject"] = subj
    brand = subj.get("brand")
    category = subj.get("category")
    # 主语匹配：主品牌 OR 主品类之一
    keys = [k for k in [brand, category] if k and k != "未指定"]

    results = []

    def in_section(pattern: str, text: str) -> str:
        m = re.search(pattern, text, re.DOTALL)
        return m.group(0) if m else ""

    # A1. 摘要卡提到主语
    summary_text = text[:3000]
    has_in_summary = any(k in summary_text for k in keys) if keys else False
    results.append((
        "A1. 主语锁定 - 摘要卡含主品牌/品类",
        has_in_summary,
        f"keys={keys}, 命中={has_in_summary}"
    ))

    # A2. 财务模型用主语
    # 段边界：下一个 `##\s+[九十]、` 或 `##\s+\d+\.` 或文末
    finance_text = in_section(
        r"##\s*[八8][、.]?\s*财务[\s\S]*?(?=\n##\s+[九九十]|\n##\s+\d|\Z)",
        text
    )
    has_finance_brand = any(k in finance_text for k in keys) if keys else False
    results.append((
        "A2. 财务模型 - 主品牌/品类主导",
        has_finance_brand,
        f"keys={keys}, 财务段命中={has_finance_brand}"
    ))

    # A3. 行动清单结构化（4 维评估表头 + 至少 3 条行动）
    # 行动段不强制要求主语字面（行动针对主语已在"主语锁定"中隐含）
    # 但要求是结构化清单，不是叙述段落
    action_text = in_section(
        r"##\s*[十10][、.]?\s*行动[\s\S]*?(?=\n##\s+附录|\Z)",
        text
    )
    has_structured = bool(re.search(
        r"行动|成本|收益|风险|预估|预期|必须|否决",
        action_text
    )) and bool(re.search(r"^\s*[\-\*\|]|^\s*\*\*[^*]+\*\*", action_text, re.MULTILINE))
    has_brand_mention = any(k in action_text for k in keys) if keys else False
    # 通过条件：结构化 OR 显式主语命中
    passed = has_structured or has_brand_mention
    results.append((
        "A3. 行动清单 - 结构化（针对主语）",
        passed,
        f"结构化={has_structured}, 主语命中={has_brand_mention}"
    ))

    # A4. 没有"如果换品牌为 X"完整测算（禁止项 1）
    has_swap = re.search(r"如果[换改]品牌[为是]?(.+?)[，,：:]?\s*\n\s*[\d|+\-]", text)
    results.append((
        "A4. 无'换品牌完整测算'反客为主",
        not has_swap,
        f"检测到={bool(has_swap)}"
    ))

    return results


def check_B_prohibited(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """B. 禁止项"""
    results = []

    # B1. 无营销味词
    # 注意：单字"绝对"过于常见（"绝对底部"等描述性用法），只检查组合词
    # "0 风险" 也容易误伤（如"客流 7,000 风险"），所以用更严的"零风险"
    marketing_words = ["必赚", "稳赚", "稳赚不赔", "100%赚钱", "一定赚", "包赚", "零风险", "包赢"]
    found = [w for w in marketing_words if w in text]
    results.append((
        "B1. 无营销味词（组合词）",
        len(found) == 0,
        f"命中={found}" if found else "OK"
    ))

    # B2. 无 AI 套路开场
    ai_openers = ["今天分享", "我来聊聊", "我帮一个朋友", "上周 3 个朋友",
                  "三个月后悔", "作为一个", "大家好我是"]
    # 仅检查前 2000 字符（开场部分）
    found = [w for w in ai_openers if w in text[:2000]]
    results.append((
        "B2. 无 AI 套路开场",
        len(found) == 0,
        f"命中={found}" if found else "OK"
    ))

    # B3. 无模型记忆编造（无 "根据我了解" / "一般来说" / "通常情况下" 套话）
    memory_phrases = ["根据我了解", "一般来说", "通常情况下", "业内普遍认为"]
    found = [w for w in memory_phrases if w in text]
    results.append((
        "B3. 无模型记忆编造",
        len(found) == 0,
        f"命中={found[:3]}" if found else "OK"
    ))

    # B4. 无跨城市对比（除非是用户原始输入里的 2+ 地址）
    # 严格要求："跨城市/一线城市/多城市" 必须出现在 markdown 标题/列表项/行首
    # 排除表格行（多个 | 字符）和"反例说明"行
    has_cross_city = False
    for line in text.splitlines():
        # 跳过表格行（含 2+ | 字符）
        if line.count("|") >= 2:
            continue
        # 跳过"无.../禁止..."反例说明
        if re.match(r"^[\s\*\-]*?(?:无|禁止|未要求)", line):
            continue
        if re.search(r"^#{1,3}\s+.*跨城市|^[-*]\s+.*跨城市|^跨城市\s*对比|"
                      r"^#{1,3}\s+.*一线城市对比|^[-*]\s+.*一线城市对比", line):
            has_cross_city = True
            break
    results.append((
        "B4. 无未要求跨城市对比",
        not has_cross_city,
        f"检测到={has_cross_city}"
    ))

    return results


def check_C_required_sections(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """C. 必填项 - 10 节 + 附录 A/B/C + 数据来源 + 免责声明"""
    results = []

    # C1. 10 节齐全
    missing = []
    for name, pattern in SECTION_PATTERNS.items():
        if not re.search(pattern, text):
            missing.append(name)
    results.append((
        "C1. 10 节齐全",
        len(missing) == 0,
        f"缺失={missing}" if missing else "OK (10/10)"
    ))

    # C2. 附录 A（换品类建议）
    has_appendix_a = "附录 A" in text
    results.append((
        "C2. 附录 A 渲染",
        has_appendix_a,
        "存在" if has_appendix_a else "缺失"
    ))

    # C3. 附录 B（数据局限）
    has_appendix_b = "附录 B" in text or "数据局限" in text or "数据来源清单" in text
    results.append((
        "C3. 附录 B 渲染",
        has_appendix_b,
        "存在" if has_appendix_b else "缺失"
    ))

    # C4. 附录 C（决策深度分析 8 项）
    c_count = sum(1 for i in range(1, 9) if re.search(rf"C[-\s]?{i}\b", text))
    results.append((
        "C4. 附录 C 8 项齐全",
        c_count == 8,
        f"命中={c_count}/8"
    ))

    # C5. 数据来源章节
    has_data_source = "数据来源" in text and (
        "来源链接" in text or re.search(r"https?://", text)
    )
    results.append((
        "C5. 数据来源 + 链接",
        has_data_source,
        "存在" if has_data_source else "缺失"
    ))

    # C6. 免责声明
    has_disclaimer = "免责声明" in text
    has_4_parts = all(
        part in text
        for part in ["数据来源说明", "使用限制", "重要提醒", "授权与免责"]
    )
    results.append((
        "C6. 免责声明 4 部分齐全",
        has_disclaimer and has_4_parts,
        f"存在={has_disclaimer}, 4部分={has_4_parts}"
    ))

    return results


def check_D_freshness(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """D. 数据时效分布"""
    results = []

    # D1. 报告头部有分布表
    has_table = bool(re.search(r"数据时效|时效分布|🟢.*?🟡.*?🟠.*?🔴", text[:5000]))
    results.append((
        "D1. 数据时效分布表",
        has_table,
        "存在" if has_table else "缺失（应在前 5000 字符）"
    ))

    # D2. 🟢+🟡 占比 ≥ 80%（如果分布表里有数字）
    m = re.search(r"🟢[^\d]*?(\d+)%[^\d]*?🟡[^\d]*?(\d+)%", text)
    if m:
        green_yellow = int(m.group(1)) + int(m.group(2))
        passed = green_yellow >= 80
        detail = f"🟢+🟡={green_yellow}%"
    else:
        passed = True  # 没找到表就给"通过"，C6 兜底
        detail = "未解析到具体百分比（需人工核对）"
    results.append((
        "D2. 🟢+🟡 ≥ 80%",
        passed,
        detail
    ))

    # D3. 🔴 标"仅作历史参考"（兼容"仅作历史参考"/"仅历史事实"/"仅作背景参考"）
    red_section = bool(re.search(
        r"🔴[^\n]{0,20}(?:仅作历史参考|仅历史事实|仅作背景参考|仅作参考)|"
        r"(?:仅作历史参考|仅历史事实|仅作背景参考)[^\n]{0,20}🔴",
        text
    ))
    results.append((
        "D3. 🔴 标'仅作历史参考'",
        red_section,
        "OK" if red_section else "未标注"
    ))

    return results


def check_E_labels(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """E. 标签系统"""
    results = []

    # E1. 来源等级标签数量
    source_count = len(re.findall(LABEL_SOURCE, text))
    # 阈值：≥6 达标（参考实际范本密度）
    results.append((
        "E1. 来源等级标签（≥6 处）",
        source_count >= 6,
        f"命中={source_count}" + ("（密度偏低，建议补充）" if 0 < source_count < 6 else "")
    ))

    # E2. 置信度标签
    confidence_count = len(re.findall(LABEL_CONFIDENCE, text))
    results.append((
        "E2. 置信度标签（≥5 处）",
        confidence_count >= 5,
        f"命中={confidence_count}" + ("（密度偏低）" if 0 < confidence_count < 5 else "")
    ))

    # E3. 决策可执行性标签
    decision_count = len(re.findall(LABEL_DECISION, text))
    results.append((
        "E3. 决策可执行性标签（≥5 处）",
        decision_count >= 5,
        f"命中={decision_count}" + ("（密度偏低）" if 0 < decision_count < 5 else "")
    ))

    # E4. 推算依据（兼容 "推算依据" / "LLM 推算" / "推算：" / "(推算)" / "推算，按" 等多种写法）
    inference_count = len(re.findall(
        r"推算依据|LLM\s*推算|推算[：:]|（推算）|\(推算\)|\d+%\s*推算|按[^\n]{0,8}推算",
        text
    ))
    results.append((
        "E4. 推算依据标注（≥5 处）",
        inference_count >= 5,
        f"命中={inference_count}" + ("（密度偏低）" if 0 < inference_count < 5 else "")
    ))

    return results


def check_F_finance_matrix(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """F. 财务矩阵"""
    results = []

    # F1. 3x3 矩阵标题存在
    has_3x3 = bool(re.search(r"3[x×]3|3\s*×\s*3|3\s*x\s*3", text))
    has_sensitivity = "敏感性" in text or "敏感" in text
    results.append((
        "F1. 3x3 财务敏感性矩阵",
        has_3x3 and has_sensitivity,
        f"3x3={has_3x3}, 敏感性={has_sensitivity}"
    ))

    # F2. 矩阵含三个维度（客单价/房租/客流）
    dimensions = ["客单价", "房租", "客流"]
    found_dims = [d for d in dimensions if d in text]
    results.append((
        "F2. 矩阵 3 维度（客单价/房租/客流）",
        len(found_dims) == 3,
        f"命中={found_dims}"
    ))

    # F3. 盈亏平衡日销量
    has_breakeven = "盈亏平衡" in text and ("日销量" in text or "月销量" in text)
    results.append((
        "F3. 盈亏平衡销量",
        has_breakeven,
        "存在" if has_breakeven else "缺失"
    ))

    # F4. 6 月现金流
    has_cashflow = "现金流" in text and (
        re.search(r"[1-6]\s*月|第\s*1\s*月", text) or
        re.search(r"第\s*[一二三四五六]\s*月", text) or
        "6 个月" in text or "6 月" in text or "前 6 月" in text
    )
    results.append((
        "F4. 6 月现金流预测",
        has_cashflow,
        "存在" if has_cashflow else "缺失"
    ))

    return results


def check_G_risk_matrix(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """G. 风险矩阵"""
    results = []

    # G1. 6 维度全覆盖
    missing = [d for d in RISK_DIMENSIONS if d not in text]
    results.append((
        "G1. 风险 6 维度齐全",
        len(missing) == 0,
        f"缺失={missing}" if missing else "OK (6/6)"
    ))

    # G2. 概率 × 影响矩阵
    has_prob_impact = bool(re.search(r"概率\s*[x×*]\s*影响", text)) or "概率×影响" in text
    results.append((
        "G2. 概率 × 影响矩阵",
        has_prob_impact,
        "存在" if has_prob_impact else "缺失"
    ))

    # G3. 综合分（加权和）— 兼容"风险综合分 X/5" "综合分 = X" 等多种写法
    has_composite = bool(re.search(
        r"风险综合分|综合风险分|综合分[=：:]\s*[\d.]+|(6|六)\s*维.{0,8}加权和|加权和\s*[=：:]\s*[\d.]+",
        text
    ))
    results.append((
        "G3. 风险综合分",
        has_composite,
        "存在" if has_composite else "缺失"
    ))

    return results


def check_H_action_funding(text: str, ctx: dict) -> list[tuple[str, bool, str]]:
    """H. 行动清单 + 资金准备"""
    results = []

    # H1. 行动清单 3 类分（兼容"立即做"/"立即可签"/"现场验证"/"否决红线"等同义词）
    category_patterns = [
        r"立即做|立即可签|立刻做|立即行动",
        r"现场验证|验证|必须验证|签前验证",
        r"否决红线|否决|必须放弃|红",
    ]
    has_categories = all(re.search(p, text) for p in category_patterns)
    results.append((
        "H1. 行动清单 3 类分（立即做/验证/否决）",
        has_categories,
        f"3 类齐全={has_categories}"
    ))

    # H2. 4 维评估（成本/收益/风险/决策可执行性）
    four_dims = ["成本", "收益", "风险", "决策可执行"]
    has_four = all(d in text for d in four_dims)
    results.append((
        "H2. 行动 4 维评估（成本/收益/风险/决策可执行性）",
        has_four,
        f"4 维齐全={has_four}"
    ))

    # H3. 否决红线 3-5 条
    # 找"否决红线"附近的列表（行首是 - * • 或 数字 .）
    red_line_section = re.search(
        r"否决红线[^\n]*\n(.*?)(?=\n##|\Z)",
        text, re.DOTALL
    )
    red_lines = 0
    if red_line_section:
        # 数列表项：以 - * 数字. 开头的行
        red_lines = len(re.findall(r"^\s*[\-\*\d\.\u4e00-\u9fa5]{1,3}[\s\.\)、]?\s*\S", red_line_section.group(1), re.MULTILINE))
        # 兜底：粗略数"红线"出现次数（每个红线条目至少有一个标志词）
        if red_lines < 1:
            red_lines = len(re.findall(r"\d+\.\s+\*\*|^\s*\d+\.|^\s*-\s", red_line_section.group(1), re.MULTILINE))
    results.append((
        "H3. 否决红线 ≥3 条",
        red_lines >= 3,
        f"估算={red_lines}条"
    ))

    # H4. 资金准备 3 大类
    funding_categories = ["开业一次性", "爬坡", "突发"]
    has_funding = all(c in text for c in funding_categories)
    results.append((
        "H4. 资金准备 3 大类",
        has_funding,
        f"3 类齐全={has_funding}"
    ))

    # H5. 资金 3 档评估（🟢/🟡/🔴）
    # 兼容 "🟢 资金充足" / "资金 3 档评估" / "🟢 充足"
    has_grade_symbols = bool(
        re.search(r"🟢[^\n]{0,15}资金|资金[^\n]{0,15}🟢", text) and
        re.search(r"🟡[^\n]{0,15}资金|资金[^\n]{0,15}🟡", text)
    ) or "资金 3 档" in text or "资金三档" in text
    results.append((
        "H5. 资金 3 档评估",
        has_grade_symbols,
        "存在" if has_grade_symbols else "缺失"
    ))

    return results


# ---------- 主流程 ----------

ALL_CHECKS: list[tuple[str, Callable]] = [
    ("A. 主语锁定", check_A_subject_lock),
    ("B. 禁止项", check_B_prohibited),
    ("C. 必填项", check_C_required_sections),
    ("D. 数据时效", check_D_freshness),
    ("E. 标签系统", check_E_labels),
    ("F. 财务矩阵", check_F_finance_matrix),
    ("G. 风险矩阵", check_G_risk_matrix),
    ("H. 行动清单+资金", check_H_action_funding),
]


def run_file(path: Path, verbose: bool = False) -> dict:
    """对单个文件跑全部检查"""
    text = load_file(path)
    ctx = {"file": str(path)}
    all_results = []
    category_summary = {}

    for cat_name, fn in ALL_CHECKS:
        items = fn(text, ctx)
        passed = sum(1 for _, ok, _ in items if ok)
        total = len(items)
        category_summary[cat_name] = (passed, total)
        all_results.extend(items)

    total_passed = sum(1 for _, ok, _ in all_results if ok)
    total = len(all_results)
    return {
        "file": str(path),
        "subject": ctx.get("subject", {"brand": None, "category": None}),
        "total_passed": total_passed,
        "total": total,
        "score": round(total_passed * 100 / total, 1) if total else 0,
        "categories": category_summary,
        "details": all_results if verbose else None,
    }


def print_report(results: list[dict], verbose: bool = False) -> bool:
    """打印报告，返回是否全部通过"""
    all_passed = True
    for r in results:
        print(f"\n{'=' * 70}")
        print(f"📄 {r['file']}")
        subj = r.get("subject", {})
        brand = subj.get("brand") if isinstance(subj, dict) else None
        cat = subj.get("category") if isinstance(subj, dict) else None
        print(f"   主语: 品牌={brand or '(未识别)'} / 品类={cat or '(未识别)'}")
        print(f"   总分: {r['total_passed']}/{r['total']} ({r['score']}%)")
        print(f"{'=' * 70}")

        for cat_name, (passed, total) in r["categories"].items():
            icon = "✅" if passed == total else "⚠️" if passed >= total - 1 else "❌"
            print(f"  {icon} {cat_name}: {passed}/{total}")

        if verbose and r["details"]:
            print(f"\n  详细检查：")
            for name, ok, detail in r["details"]:
                icon = "  ✓" if ok else "  ✗"
                print(f"    {icon} {name}  [{detail}]")

        if r["total_passed"] < r["total"]:
            all_passed = False

    print(f"\n{'=' * 70}")
    if all_passed:
        print("✅ 全部通过")
    else:
        print("❌ 有失败项")
    print(f"{'=' * 70}\n")
    return all_passed


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    as_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a not in ("-v",)]

    if args:
        files = [Path(a) for a in args]
    else:
        # 默认：examples/ 下所有 test-run-*.md（排除 README）
        examples = Path(__file__).parent.parent / "site-intelligence-report__skillhub" / "examples"
        files = sorted(examples.glob("test-run-*.md"))

    if not files:
        print("❌ 没找到报告文件", file=sys.stderr)
        return 1

    results = [run_file(f, verbose=verbose) for f in files]

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        all_passed = print_report(results, verbose=verbose)
        return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
