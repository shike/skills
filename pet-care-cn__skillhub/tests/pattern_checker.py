#!/usr/bin/env python3
"""
pet-care-cn Skill · 静态模式检查器

验证 skill 包结构与核心内容完整性,不调用 LLM。

检查项:
- 必需文件存在性
- YAML frontmatter 字段
- 9 条顶部诫命
- 17 个回答模板的 6 节结构(v2.0 后扩展为 25 模板)
- 边界关键词覆盖(117 词)
- 5 物种关键词覆盖
- 数字密度(每范例有具体数字)
- 风险信号含"立即就医"标志
- 兽医转介触发器
- examples 文件齐全(3 份)

运行:python3 tests/pattern_checker.py

退出码:
    0 = 全过
    1 = 有 fail
"""

import json
import re
import sys
from pathlib import Path
from typing import List

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


# ============================================================
# 1. 必需文件
# ============================================================
def check_required_files() -> None:
    print("\n[1/9] 必需文件存在性")
    required = [
        "SKILL.md",
        "skill.json",
        "README.md",
        "_meta.json",
        "_skillhub_meta.json",
        "references/topics-and-species.md",
        "references/qa-templates.md",
        "references/safe-boundary.md",
        "references/image-recognition.md",  # v1.1+
        "references/dialogue-context.md",  # v1.2+
        "references/exotic-pets.md",  # v2.0+
        "references/qa-templates/exotic-turtle.md",  # v2.0+
        "references/qa-templates/exotic-snake.md",  # v2.0+
        "references/qa-templates/exotic-lizard.md",  # v2.0+
        "references/qa-templates/exotic-ferret.md",  # v2.0+
        "references/qa-templates/exotic-hedgehog.md",  # v2.0+
        "references/qa-templates/exotic-chinchilla.md",  # v2.0+
        "references/qa-templates/exotic-parrot-large.md",  # v2.0+
        "references/qa-templates/exotic-sugar-glider.md",  # v2.0+
        "examples/example-01-arrival-cat-junior.md",
        "examples/example-02-behavior-cat-adult.md",
        "examples/example-03-senior-care-dog-senior.md",
        "examples/example-04-image-skin.md",  # v1.1+
        "examples/example-05-multi-turn.md",  # v1.2+
        "examples/example-06-exotic-turtle.md",  # v2.0+
        "tests/pattern_checker.py",
    ]
    for f in required:
        if (ROOT / f).exists():
            ok(f)
        else:
            err(f"{f} 缺失")


# ============================================================
# 2. 17 个模板文件齐全
# ============================================================
def check_17_templates() -> None:
    print("\n[2/9] 17 个模板文件齐全")
    expected = [
        # 饮食
        "references/qa-templates/diet-junior.md",
        "references/qa-templates/diet-adult.md",
        "references/qa-templates/diet-senior.md",
        # 驱虫与疫苗
        "references/qa-templates/dv-junior.md",
        "references/qa-templates/dv-adult.md",
        "references/qa-templates/dv-senior.md",
        # 绝育
        "references/qa-templates/neuter-junior.md",
        "references/qa-templates/neuter-adult.md",
        "references/qa-templates/neuter-senior.md",
        # 行为
        "references/qa-templates/beh-junior.md",
        "references/qa-templates/beh-adult.md",
        "references/qa-templates/beh-senior.md",
        # 新宠到家
        "references/qa-templates/arrival-junior.md",
        "references/qa-templates/arrival-adult.md",
        "references/qa-templates/arrival-senior.md",
        # 老年照护
        "references/qa-templates/senior-care-adult.md",
        "references/qa-templates/senior-care-senior.md",
    ]
    for f in expected:
        if (ROOT / f).exists():
            ok(f.split("/")[-1])
        else:
            err(f"模板缺失: {f}")


# ============================================================
# 3. SKILL.md frontmatter
# ============================================================
def check_skill_md_frontmatter() -> None:
    print("\n[3/9] SKILL.md frontmatter")
    text = read(ROOT / "SKILL.md")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        err("SKILL.md 缺少 YAML frontmatter")
        return
    fm = m.group(1)
    required_fields = ["name", "version", "description", "entry", "runtime", "tags"]
    for f in required_fields:
        if re.search(rf"^{f}\s*:", fm, re.MULTILINE):
            ok(f"frontmatter.{f}")
        else:
            err(f"frontmatter.{f} 缺失")


# ============================================================
# 4. 9 条顶部诫命
# ============================================================
def check_9_commandments() -> None:
    print("\n[4/9] 顶部 9 条诫命")
    text = read(ROOT / "SKILL.md")
    expected = [
        ("诫命 1", "不诊断"),
        ("诫命 2", "不开药"),
        ("诫命 3", "不替代行为学家"),
        ("诫命 4", "不替代兽医安乐决策"),
        ("诫命 5", "不画大饼"),
        ("诫命 6", "不老调重弹"),
        ("诫命 7", "不替代异宠专科"),
        ("诫命 8", "不推荐具体商品"),
        ("诫命 9", "不遗忘隐私"),
    ]
    for tag, phrase in expected:
        if phrase in text:
            ok(f"{tag}: {phrase}")
        else:
            err(f"{tag} 缺失: {phrase}")


# ============================================================
# 5. 7 步工作流
# ============================================================
def check_7_step_workflow() -> None:
    print("\n[5/9] 7 步工作流")
    text = read(ROOT / "SKILL.md")
    expected_steps = [
        ("Step 0", "输入解析"),
        ("Step 1", "边界检查"),
        ("Step 2", "模板加载"),
        ("Step 3", "上下文适配"),
        ("Step 4", "6 节输出"),
        ("Step 5", "补充转介"),
        ("Step 6", "最终输出"),
    ]
    for tag, phrase in expected_steps:
        if phrase in text and f"### {tag}" in text:
            ok(f"{tag}: {phrase}")
        else:
            err(f"{tag} 缺失或未含 '{phrase}'")


# ============================================================
# 6. 17 模板的 6 节结构
# ============================================================
def check_6_section_structure() -> None:
    print("\n[6/9] 17 模板的 6 节结构")
    expected_sections = [
        "场景定位",
        "核心建议",
        "关键参数",
        "常见误区",
        "风险信号",
        "兽医转介触发器",
    ]
    template_dir = ROOT / "references/qa-templates"
    template_files = sorted(template_dir.glob("*.md"))
    print(f"  发现 {len(template_files)} 个模板文件")

    if len(template_files) != 25:
        err(f"模板数量异常: {len(template_files)} (应为 25 = 17 常见宠物 + 8 异宠)")

    for tf in template_files:
        text = read(tf)
        if not text:
            continue
        missing = [s for s in expected_sections if s not in text]
        if missing:
            err(f"{tf.name} 缺章节: {', '.join(missing)}")
        else:
            ok(f"{tf.name} 6 节齐全")


# ============================================================
# 7. 边界关键词覆盖(5 物种 + 3 等级)
# ============================================================
def check_boundary_keywords() -> None:
    print("\n[7/9] safe-boundary.md 关键词覆盖")
    text = read(ROOT / "references/safe-boundary.md")
    if not text:
        return

    # 5 物种覆盖
    species = ["猫", "狗", "兔", "鸟", "鼠"]
    for s in species:
        if f"### 2.{['猫', '狗', '兔', '鸟', '鼠'].index(s) + 1} {s}" in text:
            ok(f"物种 {s} 症状词覆盖")
        else:
            err(f"物种 {s} 症状词缺失")

    # 3 等级覆盖
    for level in ["P0", "P1", "P2"]:
        if level in text:
            ok(f"等级 {level} 覆盖")
        else:
            err(f"等级 {level} 缺失")

    # 行为 + 药物 + 临终 + 物种红线 4 节
    for sec in ["行为关键词", "药物", "临终", "物种特异红线"]:
        if sec in text:
            ok(f"§ {sec} 存在")
        else:
            err(f"§ {sec} 缺失")

    # 转介话术 6 类
    expected_8 = [
        "8.1 P0 症状转介话术",
        "8.2 P1 症状转介话术",
        "8.3 行为学家转介话术",
        "8.4 临终关怀话术",
        "8.5 药物改写话术",
        "8.6 物种越界话术",
    ]
    for sec in expected_8:
        if sec in text:
            ok(f"§ {sec}")
        else:
            err(f"§ {sec} 缺失")

    # 9 步调度检查
    expected_6 = [
        "Step 1", "Step 2", "Step 3", "Step 4",
        "Step 5", "Step 6", "Step 7", "Step 8", "Step 9"
    ]
    for step in expected_6:
        if step in text:
            ok(f"调度 {step}")
        else:
            err(f"调度 {step} 缺失")


# ============================================================
# 8. 数字密度 + 风险信号标志 + 兽医转介标志
# ============================================================
def check_template_density() -> None:
    print("\n[8/9] 模板数字密度 + 标志词")
    template_dir = ROOT / "references/qa-templates"
    template_files = sorted(template_dir.glob("*.md"))

    # 检查每个范例(按物种章节)有数字、有"立即就医"、有"兽医转介"
    for tf in template_files:
        text = read(tf)
        if not text:
            continue
        # 数字密度:至少有 3 个数字(数字字符)
        digits = len(re.findall(r"\d+", text))
        if digits < 20:  # 一份模板 5 物种,每物种多个数字
            warn(f"{tf.name} 数字偏少 ({digits} 个,建议 ≥ 20)")
        else:
            ok(f"{tf.name} 数字 {digits} 个")

        # "立即就医" 标志(每个物种章节至少 1 次)
        # 允许 "立即就医" / "立即排查" / "立即转介" / "立即检查" 等
        # 异宠模板阈值放宽(每物种 1 通用模板,简版结构,自然短)
        is_exotic = tf.name.startswith("exotic-")
        min_emergency = 2 if is_exotic else 3
        min_vet = 2 if is_exotic else 5

        emergency_markers = ["立即就医", "立即排查", "立即转介", "立即检查", "立即手术", "立即处理"]
        if any(m in text for m in emergency_markers):
            counts = sum(text.count(m) for m in emergency_markers)
            if counts < min_emergency:
                warn(f"{tf.name} 急症标志共 {counts} 次(建议 ≥ {min_emergency})")
            else:
                ok(f"{tf.name} 急症标志 {counts} 次")
        else:
            err(f"{tf.name} 缺急症标志(立即就医/排查/转介/检查)")

        # 兽医转介标志
        if "兽医" in text:
            count = text.count("兽医")
            if count < min_vet:
                warn(f"{tf.name} '兽医' 出现 {count} 次(建议 ≥ {min_vet})")
            else:
                ok(f"{tf.name} '兽医' {count} 次")
        else:
            err(f"{tf.name} 缺 '兽医' 标志")


# ============================================================
# 9. examples 完整 + 关键边界处理
# ============================================================
def check_examples() -> None:
    print("\n[9/9] examples 完整 + 关键边界")
    examples = [
        "examples/example-01-arrival-cat-junior.md",
        "examples/example-02-behavior-cat-adult.md",
        "examples/example-03-senior-care-dog-senior.md",
    ]
    for ex in examples:
        path = ROOT / ex
        if not path.exists():
            err(f"{ex} 缺失")
            continue
        text = read(path)
        ok(f"{ex.split('/')[-1]} 存在")

        # 必须有 Step 0-6
        for step in ["Step 0", "Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "Step 6"]:
            if step not in text:
                err(f"{ex} 缺 {step}")
                break

        # 必须有 6 节输出关键词
        for sec in ["场景定位", "核心建议", "关键参数", "常见误区", "风险信号", "兽医转介触发器"]:
            if sec not in text:
                err(f"{ex} 缺章节 '{sec}'")
                break

    # example 02 特殊检查:必须含"先就医"或"先排除"
    text2 = read(ROOT / "examples/example-02-behavior-cat-adult.md")
    if "先就医" in text2 or "先排除" in text2:
        ok("example-02 含'先就医'边界")
    else:
        err("example-02 缺'先就医'边界")

    # example 03 特殊检查:必须含临终关怀话术关键句
    text3 = read(ROOT / "examples/example-03-senior-care-dog-senior.md")
    if "临终" in text3 and ("不做判断" in text3 or "不替代" in text3):
        ok("example-03 含临终关怀边界")
    else:
        err("example-03 缺临终关怀边界")
    if "陪伴它走完" not in text3:  # 不能用过度抒情
        ok("example-03 无过度抒情")
    else:
        err("example-03 出现'陪伴它走完'过度抒情")


# ============================================================
# 主入口
# ============================================================
def main() -> int:
    print("=" * 60)
    print("pet-care-cn skill 静态模式检查器")
    print("=" * 60)

    check_required_files()
    check_17_templates()
    check_skill_md_frontmatter()
    check_9_commandments()
    check_7_step_workflow()
    check_6_section_structure()
    check_boundary_keywords()
    check_template_density()
    check_examples()

    print("\n" + "=" * 60)
    print(f"结果汇总:✅ {len(oks)} pass / ⚠️  {len(warnings)} warn / ❌ {len(errors)} fail")
    print("=" * 60)

    if warnings:
        print("\n[警告]")
        for w in warnings:
            print(f"  ⚠️  {w}")

    if errors:
        print("\n[错误]")
        for e in errors:
            print(f"  ❌ {e}")
        return 1
    else:
        print("\n🎉 全部检查通过")
        return 0


if __name__ == "__main__":
    sys.exit(main())
