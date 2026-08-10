#!/usr/bin/env python3
"""
塔罗解牌 Skill · 静态模式检查器

验证 skill 包结构与核心内容完整性，不调用 LLM。
- 必需文件存在性
- YAML frontmatter 字段
- 78 张牌图 + 78 张牌义完整性
- 18 牌阵定义完整性
- 14 条禁止项完整性
- 塔罗师诫命 + 图版权声明
- references/ 子文件

运行：python3 tests/pattern_checker.py
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
errors: List[str] = []
warnings: List[str] = []
oks: List[str] = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"❌ {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"⚠️  {msg}")


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"✅ {msg}")


def read(path: Path) -> str:
    if not path.exists():
        err(f"文件不存在: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def check_required_files() -> None:
    """必需文件存在性"""
    print("\n[1/8] 必需文件存在性")
    required = [
        "SKILL.md",
        "skill.json",
        "README.md",
        "skill-card.md",
        "CHANGELOG.md",
        "references/78-cards.md",
        "references/spreads.md",
        "references/four-elements.md",
        "references/reading-framework.md",
        "references/ethics.md",
        "references/ai-prompt-template.md",
    ]
    for f in required:
        if (ROOT / f).exists():
            ok(f"{f}")
        else:
            err(f"{f} 缺失")


def check_skill_md_frontmatter() -> None:
    """SKILL.md YAML frontmatter"""
    print("\n[2/8] SKILL.md frontmatter")
    text = read(ROOT / "SKILL.md")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        err("SKILL.md 缺少 YAML frontmatter（必须以 --- 包裹）")
        return
    fm = m.group(1)
    required_fields = ["name", "version", "description", "entry", "runtime", "tags"]
    for f in required_fields:
        if re.search(rf"^{f}\s*:", fm, re.MULTILINE):
            ok(f"frontmatter.{f}")
        else:
            err(f"frontmatter.{f} 缺失")


def check_skill_md_ethics_and_copyright() -> None:
    """SKILL.md 顶部诫命 + 图版权"""
    print("\n[3/8] SKILL.md 顶部诫命 + 图版权")
    text = read(ROOT / "SKILL.md")
    if "图版权声明" in text or "Liora Moon" in text:
        ok("图版权声明存在")
    else:
        err("SKILL.md 缺少图版权声明")
    if "塔罗师诫命" in text and "不预测命定论" in text:
        ok("塔罗师诫命存在")
    else:
        err("SKILL.md 缺少塔罗师诫命")


def check_skill_md_prohibitions() -> None:
    """SKILL.md 14 条禁止项"""
    print("\n[4/8] SKILL.md 14 条禁止项")
    text = read(ROOT / "SKILL.md")
    expected_phrases = [
        "禁止 LLM 自动抽卡",
        "禁止跳过 [背] 占位符",
        "禁止不标位置名",
        "禁止不标元素 / 数字",
        "禁止不标正逆位",
        "禁止给绝对预测",
        "禁止医疗 / 法律 / 投资 / 命定论",
        "禁止 LLM 自由发挥",
        "禁止不基于牌阵定义",
        "禁止把\"AI 解读\"说成\"AI 算命\"",
        "禁止营销味",
        "禁止 AI 套路开场",
        "禁止\"如果换问题为 X\"",
        "禁止\"故事套路\"",
    ]
    for phrase in expected_phrases:
        if phrase in text:
            ok(f"禁止项: {phrase[:30]}...")
        else:
            warn(f"禁止项缺失或不完整: {phrase[:50]}")


def check_78_cards_completeness() -> None:
    """78 张牌义完整性"""
    print("\n[5/8] 78-cards.md 牌义完整性")
    text = read(ROOT / "references/78-cards.md")
    if not text:
        return
    # 22 大阿卡纳（中文名）
    major_names = [
        "愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人",
        "战车", "力量", "隐者", "命运之轮", "正义", "倒吊人", "死神",
        "节制", "恶魔", "塔", "星星", "月亮", "太阳", "审判", "世界",
    ]
    for name in major_names:
        if f"### {name}" in text or f"### 0." in text or f"### 1." in text:
            ok(f"大阿卡纳: {name}")
        else:
            warn(f"大阿卡纳 {name} 在 78-cards.md 中可能缺失")
    # 4 花色 × 14 张
    minor_check = [
        ("权杖", "权杖一", "权杖国王"),
        ("圣杯", "圣杯一", "圣杯国王"),
        ("宝剑", "宝剑一", "宝剑国王"),
        ("星币", "星币一", "星币国王"),
    ]
    for suit, first, last in minor_check:
        if first in text and last in text:
            ok(f"{suit} 14 张齐全")
        else:
            err(f"{suit} 小阿卡纳不完整（{first} / {last}）")
    # 速查表完整性
    if "## III. 牌面速查表" in text or "牌面速查表" in text:
        ok("速查表存在")
        # 检查 78 行
        rows = re.findall(r"\|\s*\d+\s*\|", text)
        if len(rows) >= 78:
            ok(f"速查表 {len(rows)} 行（≥ 78）")
        else:
            warn(f"速查表行数 {len(rows)} 不足 78")


def check_78_card_images() -> None:
    """78 张牌图完整性"""
    print("\n[6/8] assets/cards/ 牌图完整性")
    major_dir = ROOT / "assets/cards/major"
    minor_dir = ROOT / "assets/cards/minor"
    if not major_dir.exists():
        err("assets/cards/major 目录缺失")
        return
    if not minor_dir.exists():
        err("assets/cards/minor 目录缺失")
        return
    major_count = len(list(major_dir.glob("*.webp")))
    minor_count = len(list(minor_dir.glob("*.webp")))
    if major_count == 22:
        ok(f"大阿卡纳图 {major_count} 张（= 22）")
    else:
        err(f"大阿卡纳图 {major_count} 张（应为 22）")
    if minor_count == 56:
        ok(f"小阿卡纳图 {minor_count} 张（= 56）")
    else:
        err(f"小阿卡纳图 {minor_count} 张（应为 56）")


def check_spreads_completeness() -> None:
    """18 牌阵完整性"""
    print("\n[7/8] spreads.md 18 牌阵完整性")
    text = read(ROOT / "references/spreads.md")
    if not text:
        return
    expected_spreads = [
        "single", "three-cards", "time-flow", "holy-triangle", "four-elements",
        "celtic-cross", "hexagram", "horoscope", "tree-of-life", "weekly",
        "two-choices", "venus", "gypsy-cross", "lovers-reunion", "soulmate",
        "find-soulmate", "mind-body-spirit", "tree-of-wealth",
    ]
    for spread in expected_spreads:
        if spread in text:
            ok(f"牌阵: {spread}")
        else:
            err(f"牌阵缺失: {spread}")


def check_examples_completeness() -> None:
    """examples 完整性 + 含图"""
    print("\n[8/8] examples 完整性 + 含图")
    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        err("examples/ 目录缺失")
        return
    expected = [
        "case-001",  # 单抽
        "case-002",  # 凯尔特
        "case-003",  # 时间流
    ]
    files = list(examples_dir.glob("*.md"))
    for prefix in expected:
        if any(f.name.startswith(prefix) for f in files):
            ok(f"example: {prefix}")
        else:
            err(f"example 缺失: {prefix}")
    # 含图检查（每个 example 必须有 ![XX](assets/cards/...) 引用）
    expected_images = {
        "case-001": 1,  # 至少 1 张图（揭晓 + 单牌）
        "case-002": 20, # 揭晓 10 + 单牌 10
        "case-003": 6,  # 揭晓 3 + 单牌 3
    }
    for f in files:
        for prefix, min_count in expected_images.items():
            if f.name.startswith(prefix):
                text = f.read_text(encoding="utf-8")
                img_count = len(re.findall(r"!\[.*?\]\(assets/cards/", text))
                if img_count >= min_count:
                    ok(f"{prefix} 含图 {img_count} 张（≥ {min_count}）")
                else:
                    err(f"{prefix} 图数 {img_count}（应 ≥ {min_count}）")


def check_skill_json() -> None:
    """skill.json 完整性"""
    print("\n[extra] skill.json 字段完整性")
    path = ROOT / "skill.json"
    if not path.exists():
        err("skill.json 缺失")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"skill.json JSON 解析失败: {e}")
        return
    required = [
        "name", "version", "description", "license", "runtime", "entry",
        "tags", "keywords", "triggers", "input_schema", "spreads",
    ]
    for f in required:
        if f in data:
            ok(f"skill.json.{f}")
        else:
            err(f"skill.json.{f} 缺失")
    # input_schema 必填字段
    if "input_schema" in data:
        for f in ["question", "spread"]:
            if f in data["input_schema"]:
                ok(f"input_schema.{f}")
            else:
                err(f"input_schema.{f} 缺失")
    # spreads 数量
    if "spreads" in data:
        if len(data["spreads"]) >= 18:
            ok(f"spreads {len(data['spreads'])} 个（≥ 18）")
        else:
            err(f"spreads {len(data['spreads'])} 个（< 18）")


def main() -> int:
    print("=" * 60)
    print("塔罗解牌 Skill · 静态模式检查器")
    print("=" * 60)
    check_required_files()
    check_skill_md_frontmatter()
    check_skill_md_ethics_and_copyright()
    check_skill_md_prohibitions()
    check_78_cards_completeness()
    check_78_card_images()
    check_spreads_completeness()
    check_examples_completeness()
    check_skill_json()
    print("\n" + "=" * 60)
    print(f"汇总: ✅ {len(oks)}  pass | ⚠️  {len(warnings)}  warn | ❌ {len(errors)}  fail")
    print("=" * 60)
    if errors:
        print("\n错误列表:")
        for e in errors:
            print(f"  - {e}")
        return 1
    if warnings:
        print("\n警告列表（不阻塞，但建议补全）:")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
