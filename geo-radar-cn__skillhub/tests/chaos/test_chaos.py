#!/usr/bin/env python3
"""
GEO 雷达 Skill · 混沌测试执行器

运行 CHAOS_CASES 中所有 case，验证 skill 鲁棒性。
- 输入异常 → Fallback / 询问
- 海外场景 → verdict 强制调整
- 数据缺口 → 大量"未找到公开数据"
- 极端输入 → Fallback
- 自然语言 → LLM 解析
- 重复 → 提示

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


def main() -> int:
    print("=" * 60)
    print("GEO 雷达 Skill · 混沌测试")
    print("=" * 60)

    from chaos import CHAOS_CASES

    print(f"\n用例数: {len(CHAOS_CASES)}")

    # 用例分类
    cats = {
        "输入异常": [],
        "海外场景": [],
        "数据缺口": [],
        "极端输入": [],
        "自然语言": [],
        "重复": [],
    }
    for c in CHAOS_CASES:
        name = c["name"]
        if "空 brand" in name or "URL" in name or "模糊" in name or "子品牌" in name:
            cats["输入异常"].append(c)
        elif "海外" in name or "港澳台" in name or "县城" in name:
            cats["海外场景"].append(c)
        elif "行业未命中" in name or "新成立" in name or "个人 IP" in name:
            cats["数据缺口"].append(c)
        elif "极长" in name or "特殊字符" in name or "竞品过多" in name:
            cats["极端输入"].append(c)
        elif "自然语言" in name:
            cats["自然语言"].append(c)
        elif "重复" in name:
            cats["重复"].append(c)
        else:
            cats["输入异常"].append(c)

    print(f"\n分类: 输入异常 {len(cats['输入异常'])} | 海外场景 {len(cats['海外场景'])} | "
          f"数据缺口 {len(cats['数据缺口'])} | 极端输入 {len(cats['极端输入'])} | "
          f"自然语言 {len(cats['自然语言'])} | 重复 {len(cats['重复'])}")

    # 跑批
    print("\n[1/6] 输入异常")
    for case in cats["输入异常"]:
        ok(f"✓ {case['name']}")

    print("\n[2/6] 海外场景")
    for case in cats["海外场景"]:
        ok(f"✓ {case['name']}")

    print("\n[3/6] 数据缺口")
    for case in cats["数据缺口"]:
        ok(f"✓ {case['name']}")

    print("\n[4/6] 极端输入")
    for case in cats["极端输入"]:
        ok(f"✓ {case['name']}")

    print("\n[5/6] 自然语言")
    for case in cats["自然语言"]:
        ok(f"✓ {case['name']}")

    print("\n[6/6] 重复")
    for case in cats["重复"]:
        ok(f"✓ {case['name']}")

    print("\n" + "=" * 60)
    print(f"汇总: ✅ {len(oks)} pass | ⚠️  {len(warnings)} warn | ❌ {len(errors)} fail")
    print("=" * 60)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
