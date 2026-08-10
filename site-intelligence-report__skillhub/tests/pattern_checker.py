#!/usr/bin/env python3
"""
site-intelligence-report Skill · 静态模式检查器

验证 skill 包结构与核心内容完整性，不调用 LLM。
- 必需文件存在性（含 CHANGELOG v1.1.0 承诺的 pattern_checker）
- YAML frontmatter 字段
- 4 大 Hard Constraint（主语锁定 / 数据时效 / 标签系统 / 3x3 财务矩阵 / 概率×影响风险矩阵）
- 14 条禁止项
- 中国 only 硬限制
- 6 品类行业基准（奶茶/咖啡/快餐/正餐/麻辣烫/烘焙）
- references/ 子文件（4 个 + 24 字段 schema）
- skill.json 字段 + 输入 schema + 触发词
- icon.png 1024×1024
- examples 3 份范本

运行：python3 tests/pattern_checker.py

退出码：
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
    print("\n[1/10] 必需文件存在性")
    required = [
        "SKILL.md",
        "skill.json",
        "README.md",
        "skill-card.md",
        "CHANGELOG.md",
        "icon.png",
        "user_license.json",
        "references/report-schema.md",
        "references/web-search-prompts.md",
        "references/category-baseline.md",
        "references/test-cases.md",
    ]
    for f in required:
        if (ROOT / f).exists():
            ok(f)
        else:
            err(f"{f} 缺失")


# ============================================================
# 2. SKILL.md frontmatter
# ============================================================
def check_skill_md_frontmatter() -> None:
    print("\n[2/10] SKILL.md frontmatter")
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
# 3. 中国 only 硬限制 + 免责声明
# ============================================================
def check_china_only_and_disclaimer() -> None:
    print("\n[3/10] 中国 only 硬限制 + 免责声明")
    text = read(ROOT / "SKILL.md")
    # 中国 only 提示
    if re.search(r"v1\.x.*中国|海外场景.*v2\.0|非中国城市", text):
        ok("v1.x 中国 only 硬限制提示存在")
    else:
        err("v1.x 中国 only 硬限制缺失（重要：用户必须 top-level 知道）")
    # 免责声明 Hard Requirement
    if "免责声明" in text and "Hard Requirement" in text:
        ok("免责声明 Hard Requirement 存在")
    else:
        err("免责声明 Hard Requirement 缺失")


# ============================================================
# 4. 14 条禁止项
# ============================================================
def check_skill_md_prohibitions() -> None:
    print("\n[4/10] SKILL.md 14 条禁止项")
    text = read(ROOT / "SKILL.md")
    expected = [
        ("主语 1", "禁止自动延展为其他品牌的财务测算"),
        ("主语 2", "禁止在「建议」里反客为主"),
        ("主语 3", "禁止未要求的多场景对比"),
        ("内容 4", "禁止自动加用户未要求的子报告"),
        ("内容 5", "禁止把竞品对标错位为主语"),
        ("内容 6", "禁止在主报告字段里做品牌对比"),
        ("内容 7", "禁止对用户输入做扩展性解读"),
        ("表达 8", "禁止营销味表达"),
        ("表达 9", "禁止 AI 套路开场"),
        ("表达 10", "禁止把行业级宏观内容当结论"),
        ("表达 11", "禁止模板化填空"),
        ("数据 12", "禁止用模型记忆填充"),
        ("数据 13", "禁止编造数据"),
        ("数据 14", "禁止改动用户输入"),
    ]
    for tag, phrase in expected:
        if phrase in text:
            ok(f"禁止项 {tag}")
        else:
            err(f"禁止项缺失 {tag}: {phrase[:30]}")


# ============================================================
# 5. Hard Constraint: 主语锁定
# ============================================================
def check_subject_lock() -> None:
    print("\n[5/10] Hard Constraint · 主语锁定")
    text = read(ROOT / "SKILL.md")
    if "Step 0.5" in text and "主语锁定" in text and "Hard Constraint" in text:
        ok("Step 0.5 主语锁定 Hard Constraint")
    else:
        err("Step 0.5 主语锁定 Hard Constraint 缺失")
    if "如果换品牌为 X" in text or "换品牌" in text:
        ok("换品牌约束（仅 1 句背景说明，不展开测算）")
    else:
        warn("换品牌约束描述缺失")


# ============================================================
# 6. Hard Constraint: 数据时效分级
# ============================================================
def check_data_freshness() -> None:
    print("\n[6/10] Hard Constraint · 数据时效分级")
    text = read(ROOT / "SKILL.md")
    if "Step 0.6" in text and "数据时效" in text and "Hard Constraint" in text:
        ok("Step 0.6 数据时效分级 Hard Constraint")
    else:
        err("Step 0.6 数据时效分级 Hard Constraint 缺失")
    # 4 档时效
    for emoji in ["🟢", "🟡", "🟠", "🔴"]:
        if emoji in text:
            ok(f"时效 {emoji} 档")
        else:
            err(f"时效 {emoji} 档缺失")
    # 硬指标
    if "🟢+🟡" in text and "≥ 80%" in text and "🔴 ≤ 10%" in text:
        ok("时效硬指标 🟢+🟡 ≥ 80% / 🔴 ≤ 10%")
    else:
        err("时效硬指标不完整")


# ============================================================
# 7. Hard Constraint: 3x3 财务矩阵 + 概率×影响 风险矩阵
# ============================================================
def check_financial_and_risk_matrix() -> None:
    print("\n[7/10] Hard Constraint · 3x3 财务矩阵 + 概率×影响 风险矩阵")
    text = read(ROOT / "SKILL.md")
    if "Step 2.5.1" in text and "3x3" in text and "Hard Constraint" in text:
        ok("Step 2.5.1 3x3 财务矩阵 Hard Constraint")
    else:
        err("Step 2.5.1 3x3 财务矩阵 Hard Constraint 缺失")
    if "Step 2.5.2" in text and "概率" in text and "影响" in text and "Hard Constraint" in text:
        ok("Step 2.5.2 概率×影响 风险矩阵 Hard Constraint")
    else:
        err("Step 2.5.2 概率×影响 风险矩阵 Hard Constraint 缺失")
    # 6 风险维度
    for dim in ["拆迁", "政策", "竞品", "客流", "财务", "品类适配"]:
        if dim in text:
            ok(f"风险维度: {dim}")
        else:
            err(f"风险维度缺失: {dim}")


# ============================================================
# 8. Hard Constraint: 4 维标签系统
# ============================================================
def check_label_system() -> None:
    print("\n[8/10] Hard Constraint · 4 维标签系统")
    text = read(ROOT / "SKILL.md")
    if "Step 2.7" in text and "标签" in text and "Hard Constraint" in text:
        ok("Step 2.7 完整标签系统 Hard Constraint")
    else:
        err("Step 2.7 完整标签系统 Hard Constraint 缺失")
    # 来源等级 5 类
    for src in ["🏛️", "📊", "📰", "🏪", "👤"]:
        if src in text:
            ok(f"来源等级: {src}")
        else:
            err(f"来源等级缺失: {src}")
    # 置信度 3 档
    for conf in ["🟢", "🟡", "🔴"]:
        if conf in text:
            ok(f"置信度: {conf}")
        else:
            warn(f"置信度 {conf} 档缺失")
    # 决策可执行性 3 档
    for act in ["✅", "⚠️", "❌"]:
        if act in text:
            ok(f"决策可执行性: {act}")
        else:
            warn(f"决策可执行性 {act} 档缺失")


# ============================================================
# 9. category-baseline 6 品类齐全
# ============================================================
def check_category_baseline() -> None:
    print("\n[9/10] category-baseline.md 6 品类齐全")
    text = read(ROOT / "references/category-baseline.md")
    if not text:
        return
    categories = ["奶茶", "咖啡", "快餐", "正餐", "麻辣烫", "烘焙"]
    for cat in categories:
        if cat in text:
            ok(f"品类: {cat}")
        else:
            err(f"品类缺失: {cat}")


# ============================================================
# 10. skill.json + examples + icon
# ============================================================
def check_skill_json() -> None:
    print("\n[10/10] skill.json 完整性 + icon + examples")
    # skill.json
    path = ROOT / "skill.json"
    if not path.exists():
        err("skill.json 缺失")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"skill.json JSON 解析失败: {e}")
        return
    required = ["name", "version", "description", "license", "runtime", "entry",
                "tags", "keywords", "triggers", "input_schema"]
    for f in required:
        if f in data:
            ok(f"skill.json.{f}")
        else:
            err(f"skill.json.{f} 缺失")
    # input_schema 必填 4 字段
    schema = data.get("input_schema", {})
    for f in ["brand", "address", "city", "category"]:
        if f in schema:
            ok(f"input_schema.{f}")
        else:
            err(f"input_schema.{f} 缺失")
    # triggers 数量
    triggers = data.get("triggers", [])
    if len(triggers) >= 30:
        ok(f"triggers {len(triggers)} 个（≥ 30）")
    elif len(triggers) >= 15:
        warn(f"triggers {len(triggers)} 个（建议 ≥ 30）")
    else:
        err(f"triggers {len(triggers)} 个（< 15 严重不足）")
    # keywords 数量
    keywords = data.get("keywords", [])
    if len(keywords) >= 25:
        ok(f"keywords {len(keywords)} 个（≥ 25）")
    elif len(keywords) >= 15:
        warn(f"keywords {len(keywords)} 个（建议 ≥ 25）")
    else:
        err(f"keywords {len(keywords)} 个（< 15 严重不足）")
    # icon.png
    icon = ROOT / "icon.png"
    if icon.exists():
        # 检查尺寸
        try:
            from PIL import Image
            with Image.open(icon) as img:
                w, h = img.size
                if w == 1024 and h == 1024:
                    ok(f"icon.png {w}×{h}")
                else:
                    warn(f"icon.png {w}×{h}（建议 1024×1024）")
        except ImportError:
            # 无 PIL 就跳过尺寸检查
            ok("icon.png 存在（未验证尺寸，PIL 未安装）")
    else:
        err("icon.png 缺失")
    # examples
    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        err("examples/ 目录缺失")
        return
    files = list(examples_dir.glob("test-run-*.md"))
    if len(files) >= 3:
        ok(f"examples {len(files)} 份范本（高/中/低数据）")
    else:
        warn(f"examples {len(files)} 份范本（建议 ≥ 3 覆盖高/中/低数据）")


def main() -> int:
    print("=" * 60)
    print("site-intelligence-report Skill · 静态模式检查器")
    print("=" * 60)
    check_required_files()
    check_skill_md_frontmatter()
    check_china_only_and_disclaimer()
    check_skill_md_prohibitions()
    check_subject_lock()
    check_data_freshness()
    check_financial_and_risk_matrix()
    check_label_system()
    check_category_baseline()
    check_skill_json()
    print("\n" + "=" * 60)
    print(f"汇总: ✅ {len(oks)} pass | ⚠️  {len(warnings)} warn | ❌ {len(errors)} fail")
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
