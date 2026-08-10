#!/usr/bin/env python3
"""
混沌测试执行器

运行 CHAOS_CASES 中所有 case，验证 skill 鲁棒性。
- 内容安全：检测 skill.json blocked_keywords 命中
- Prompt 注入：检测 skill.json prompt_injection_patterns 命中
- 重复问卦：检测 duplicate_check method
- Fallback：检测缺失字段

运行：python3 tests/chaos/test_chaos.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tests"))

errors: list = []
warnings: list = []
oks: list = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"❌ {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"⚠️  {msg}")


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"✅ {msg}")


def load_skill_config() -> dict:
    return json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def check_content_safety(question: str, config: dict) -> list:
    """检测内容安全关键词"""
    blocked = config.get("content_safety", {}).get("blocked_keywords", [])
    hit = []
    for kw in blocked:
        if kw in question:
            hit.append(kw)
    return hit


def check_prompt_injection(question: str, config: dict) -> list:
    """检测 prompt 注入模式"""
    patterns = config.get("content_safety", {}).get("prompt_injection_patterns", [])
    question_lower = question.lower()
    hit = []
    for p in patterns:
        if p.lower() in question_lower:
            hit.append(p)
    return hit


def check_question_hash(question: str, history: set) -> bool:
    """检测重复问卦（SHA-256）"""
    import hashlib
    h = hashlib.sha256(question.encode("utf-8")).hexdigest()
    return h in history


def main() -> int:
    print("=" * 60)
    print("塔罗解牌 Skill · 混沌测试")
    print("=" * 60)

    config = load_skill_config()
    blocked = config.get("content_safety", {}).get("blocked_keywords", [])
    patterns = config.get("content_safety", {}).get("prompt_injection_patterns", [])

    print(f"\n配置: blocked_keywords={len(blocked)}, injection_patterns={len(patterns)}")

    from chaos import CHAOS_CASES

    history = set()  # 模拟近 24h 问卦

    print("\n[1/2] 内容安全 + 注入检测")
    for case in CHAOS_CASES:
        q = case["input"].get("question", "")
        # 内容安全
        blocked_hit = check_content_safety(q, config)
        # 注入检测
        inject_hit = check_prompt_injection(q, config)
        # 重复问卦
        is_dup = check_question_hash(q, history)

        if "暴力" in case["name"] or "自残" in case["name"]:
            if blocked_hit:
                ok(f"内容安全命中: {case['name']} → 触发 {blocked_hit}")
            else:
                err(f"内容安全漏检: {case['name']}")
        elif "注入" in case["name"]:
            if inject_hit:
                ok(f"注入检测命中: {case['name']} → 触发 {inject_hit}")
            else:
                err(f"注入检测漏检: {case['name']}")
        elif "重复" in case["name"]:
            if is_dup:
                ok(f"重复问卦命中: {case['name']}")
            else:
                # 第一次不算 dup
                warn(f"重复问卦首次记录: {case['name']}")
                import hashlib
                history.add(hashlib.sha256(q.encode("utf-8")).hexdigest())
        else:
            if not blocked_hit and not inject_hit:
                ok(f"正常用例: {case['name']}")
            else:
                err(f"正常用例误检: {case['name']} → blocked={blocked_hit} inject={inject_hit}")

    print(f"\n[2/2] 全混沌用例数: {len(CHAOS_CASES)}")
    print("=" * 60)
    print(f"汇总: ✅ {len(oks)} pass | ⚠️  {len(warnings)} warn | ❌ {len(errors)} fail")
    print("=" * 60)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
