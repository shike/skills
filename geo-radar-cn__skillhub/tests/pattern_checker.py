#!/usr/bin/env python3
"""
GEO 雷达 Skill · 静态模式检查器 (v2.3)

验证 skill 包结构与核心内容完整性,不调用 LLM。
- 必需文件存在性（v2.3 Playwright + 系统 Chrome 真实模式）
- YAML frontmatter 字段
- 4 大 Hard Constraint（主语锁定 / 数据时效 / 标签系统 / 8 节报告）
- 14 条禁止项
- 中国 only 硬限制
- 8 行业 × 4 类型查询词模板
- references/ 子文件（含 3 个 mode 文档）
- skill.json 字段 + 输入 schema + 触发词
- icon.png 1024×1024
- examples 范本 + run_mixue_demo.sh
- v2.3 真实模式 + v2.2 LLM 模拟 fallback + v2.1 Power User 集成检查
- v2.3 主路径 Playwright 爬虫代码完整性

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
# 1. 必需文件（v2.3）
# ============================================================
def check_required_files() -> None:
    print("\n[1/12] 必需文件存在性")
    required = [
        "SKILL.md",
        "skill.json",
        "README.md",
        "skill-card.md",
        "CHANGELOG.md",
        "icon.png",
        "_meta.json",
        "_skillhub_meta.json",
        "references/query-templates.md",
        "references/report-schema.md",
        "references/web-search-prompts.md",
        "references/chaos-cases.md",
        "references/llm-test-prompts.md",
        "references/mode-v22-llm-roleplay.md",  # v2.2 fallback
        "references/mode-v21-agent-browser.md",  # v2.1 Power User
        "references/mode-v10-web-search.md",  # v1.0 最后 fallback
    ]
    for f in required:
        if (ROOT / f).exists():
            ok(f)
        else:
            err(f"{f} 缺失")
    # v2.3 爬虫主路径
    v23_files = [
        "scripts/crawler/__init__.py",
        "scripts/crawler/doubao.py",
        "scripts/crawler/kimi.py",
        "scripts/crawler/tongyi.py",
        "scripts/crawler/runner.py",
        "scripts/run_mixue_demo.sh",
        "examples/run_mixue_demo.sh",
    ]
    for f in v23_files:
        if (ROOT / f).exists():
            ok(f"v2.3: {f}")
        else:
            err(f"v2.3 缺失: {f}")


# ============================================================
# 2. SKILL.md frontmatter
# ============================================================
def check_skill_md_frontmatter() -> None:
    print("\n[2/12] SKILL.md frontmatter")
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
    # version 应是 2.3.0+
    m_ver = re.search(r"^version\s*:\s*([\d.]+)", fm, re.MULTILINE)
    if m_ver:
        ver = m_ver.group(1)
        if ver.startswith("2.3"):
            ok(f"version: {ver}")
        else:
            warn(f"version {ver} (期望 2.3.x)")


# ============================================================
# 3. 中国 only 硬限制 + 免责声明
# ============================================================
def check_china_only_and_disclaimer() -> None:
    print("\n[3/12] 中国 only 硬限制 + 免责声明")
    text = read(ROOT / "SKILL.md")
    if re.search(r"v1\.x.*中国|海外场景.*v2\.4|非中国城市", text):
        ok("中国 only 硬限制提示存在")
    else:
        err("中国 only 硬限制缺失")
    if "免责声明" in text and "Hard Requirement" in text:
        ok("免责声明 Hard Requirement 存在")
    else:
        err("免责声明 Hard Requirement 缺失")
    # 数据局限章节
    if "数据局限" in text and ("豆包" in text or "Kimi" in text or "通义" in text):
        ok("数据局限章节提到主流 LLM 平台")
    else:
        err("数据局限章节缺失或不完整")


# ============================================================
# 4. 14 条禁止项
# ============================================================
def check_skill_md_prohibitions() -> None:
    print("\n[4/12] SKILL.md 14 条禁止项")
    text = read(ROOT / "SKILL.md")
    expected = [
        ("主语 1", "禁止自动延展为其他品牌的可见度测算"),
        ("主语 2", "禁止在「建议」里反客为主"),
        ("主语 3", "禁止未要求的多品牌对比"),
        ("内容 4", "禁止自动加用户未要求的子报告"),
        ("内容 5", "禁止把竞品对标错位为主语"),
        ("内容 6", "禁止在主报告字段里做品牌替换"),
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
# 5. Hard Constraint: 主语锁定 + 查询词自动生成
# ============================================================
def check_subject_lock_and_query_gen() -> None:
    print("\n[5/12] Hard Constraint · 主语锁定 + 查询词自动生成")
    text = read(ROOT / "SKILL.md")
    if "Step 0.5" in text and "主语锁定" in text and "Hard Constraint" in text:
        ok("Step 0.5 主语锁定 Hard Constraint")
    else:
        err("Step 0.5 主语锁定 Hard Constraint 缺失")
    if "Step 0.7" in text and "查询词自动生成" in text:
        ok("Step 0.7 查询词自动生成")
    else:
        err("Step 0.7 查询词自动生成缺失")
    if "brand" in text and "必填" in text:
        ok("brand 必填约束")
    else:
        err("brand 必填约束缺失")
    if "queries" in text and "可选" in text:
        ok("queries 可选约束")
    else:
        err("queries 可选约束缺失")


# ============================================================
# 6. Hard Constraint: 数据时效分级
# ============================================================
def check_data_freshness() -> None:
    print("\n[6/12] Hard Constraint · 数据时效分级")
    text = read(ROOT / "SKILL.md")
    if "Step 0.6" in text and "数据时效" in text and "Hard Constraint" in text:
        ok("Step 0.6 数据时效分级 Hard Constraint")
    else:
        err("Step 0.6 数据时效分级 Hard Constraint 缺失")
    for emoji in ["🟢", "🟡", "🟠", "🔴"]:
        if emoji in text:
            ok(f"时效 {emoji} 档")
        else:
            err(f"时效 {emoji} 档缺失")
    if "🟢+🟡" in text and "≥ 80%" in text and "🔴 ≤ 10%" in text:
        ok("时效硬指标 🟢+🟡 ≥ 80% / 🔴 ≤ 10%")
    else:
        err("时效硬指标不完整")


# ============================================================
# 7. 8 节报告 + 3 附录
# ============================================================
def check_report_sections() -> None:
    print("\n[7/12] 8 节报告 + 3 附录")
    text = read(ROOT / "references" / "report-schema.md")
    if not text:
        return
    sections = [
        "摘要卡", "品牌可见度分", "查询词覆盖", "竞品对比",
        "AI 引擎引用源分析", "优化机会清单", "数据局限", "行动清单",
    ]
    for sec in sections:
        if sec in text:
            ok(f"8 节: {sec}")
        else:
            err(f"8 节缺失: {sec}")
    for app in ["附录 A", "附录 B", "附录 C"]:
        if app in text:
            ok(f"附录: {app}")
        else:
            err(f"附录缺失: {app}")


# ============================================================
# 8. Hard Constraint: 4 维标签系统
# ============================================================
def check_label_system() -> None:
    print("\n[8/12] Hard Constraint · 4 维标签系统")
    text = read(ROOT / "SKILL.md")
    if "Step 3.7" in text and "标签" in text and "Hard Constraint" in text:
        ok("Step 3.7 完整标签系统 Hard Constraint")
    else:
        err("Step 3.7 完整标签系统 Hard Constraint 缺失")
    for src in ["🏛️", "📊", "📰", "🏪", "👤"]:
        if src in text:
            ok(f"来源等级: {src}")
        else:
            err(f"来源等级缺失: {src}")
    for conf in ["🟢", "🟡", "🔴"]:
        if conf in text:
            ok(f"置信度: {conf}")
        else:
            warn(f"置信度 {conf} 档缺失")
    for act in ["✅", "⚠️", "❌"]:
        if act in text:
            ok(f"决策可执行性: {act}")
        else:
            warn(f"决策可执行性 {act} 档缺失")


# ============================================================
# 9. 8 行业查询词模板
# ============================================================
def check_query_templates() -> None:
    print("\n[9/12] 8 行业查询词模板")
    text = read(ROOT / "references" / "query-templates.md")
    if not text:
        return
    categories = ["奶茶", "咖啡", "餐饮", "SaaS", "教育", "旅游", "电商", "金融"]
    for cat in categories:
        if cat in text:
            ok(f"行业: {cat}")
        else:
            err(f"行业缺失: {cat}")
    types = ["推荐型", "对比型", "痛点型", "决策型"]
    for t in types:
        if t in text:
            ok(f"查询词类型: {t}")
        else:
            err(f"查询词类型缺失: {t}")


# ============================================================
# 10. skill.json + icon + examples
# ============================================================
def check_skill_json() -> None:
    print("\n[10/12] skill.json 完整性 + icon + examples")
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
    # input_schema 必填 brand
    schema = data.get("input_schema", {})
    if "brand" in schema:
        ok("input_schema.brand 必填")
    else:
        err("input_schema.brand 必填缺失")
    if "queries" in schema:
        ok("input_schema.queries 可选")
    else:
        warn("input_schema.queries 可选缺失")
    # triggers 数量
    triggers = data.get("triggers", [])
    if len(triggers) >= 20:
        ok(f"triggers {len(triggers)} 个（≥ 20）")
    elif len(triggers) >= 10:
        warn(f"triggers {len(triggers)} 个（建议 ≥ 20）")
    else:
        err(f"triggers {len(triggers)} 个（< 10 严重不足）")
    # keywords 数量
    keywords = data.get("keywords", [])
    if len(keywords) >= 15:
        ok(f"keywords {len(keywords)} 个（≥ 15）")
    elif len(keywords) >= 10:
        warn(f"keywords {len(keywords)} 个（建议 ≥ 15）")
    else:
        err(f"keywords {len(keywords)} 个（< 10 严重不足）")
    # icon.png
    icon = ROOT / "icon.png"
    if icon.exists():
        try:
            from PIL import Image
            with Image.open(icon) as img:
                w, h = img.size
                if w == 1024 and h == 1024:
                    ok(f"icon.png {w}×{h}")
                else:
                    warn(f"icon.png {w}×{h}（建议 1024×1024）")
        except ImportError:
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


# ============================================================
# 11. v2.3 Playwright + 系统 Chrome 真实模式 + 3 mode 集成
# ============================================================
def check_v23_integration() -> None:
    """v2.3 Playwright + 系统 Chrome + 3 mode 集成检查"""
    print("\n[11/12] v2.3 Playwright + 系统 Chrome + 3 mode 集成")
    # 1. SKILL.md 提到 v2.3 + Playwright + 系统 Chrome
    skill_text = read(ROOT / "SKILL.md")
    must_have_in_skill = [
        "v2.3",
        "Playwright",
        "playwright",
        "系统 Chrome",
        "10MB",
        "use-system-chrome",
        "agent-browser",  # 提到 v2.1 备选
        "LLM 模拟",  # 提到 v2.2 fallback
    ]
    for needle in must_have_in_skill:
        if needle in skill_text:
            ok(f"SKILL.md 包含: {needle}")
        else:
            err(f"SKILL.md 缺: {needle}")
    # 2. Step 2 改 v2.3 Playwright
    if "Step 2:v2.3 Python 爬虫" in skill_text or "Step 2: v2.3" in skill_text or "v2.3 Python 爬虫" in skill_text:
        ok("Step 2 改 v2.3 Playwright 模式")
    else:
        err("Step 2 未改 v2.3 Playwright 模式")
    # 3. mode-v22 文档关键内容
    v22_text = read(ROOT / "references" / "mode-v22-llm-roleplay.md")
    if v22_text:
        must_have = [
            "LLM 模拟",
            "豆包",
            "Kimi",
            "通义",
            "60-80%",
        ]
        for needle in must_have:
            if needle in v22_text:
                ok(f"mode-v22 包含: {needle}")
            else:
                err(f"mode-v22 缺: {needle}")
    # 4. mode-v21 文档关键内容
    v21_text = read(ROOT / "references" / "mode-v21-agent-browser.md")
    if v21_text:
        for needle in ["agent-browser", "50-500MB", "WorkBuddy"]:
            if needle in v21_text:
                ok(f"mode-v21 包含: {needle}")
            else:
                err(f"mode-v21 缺: {needle}")
    # 5. 平台 URL 出现
    urls = ["doubao.com", "kimi.moonshot.cn", "tongyi.aliyun.com"]
    for url in urls:
        if url in skill_text or url in read(ROOT / "references" / "mode-v22-llm-roleplay.md"):
            ok(f"平台 URL: {url}")
        else:
            warn(f"平台 URL 不在文档: {url}")
    # 6. CHANGELOG 提到 v2.3
    changelog = read(ROOT / "CHANGELOG.md")
    if "[2.3" in changelog:
        ok("CHANGELOG 记录 v2.3 重构")
    else:
        err("CHANGELOG 应记录 v2.3 重构")


# ============================================================
# 12. v2.3 爬虫主路径代码完整性
# ============================================================
def check_v23_crawler_code() -> None:
    """v2.3 Playwright 爬虫代码完整性（主路径 scripts/crawler/）"""
    print("\n[12/12] v2.3 爬虫主路径代码完整性")
    crawler_dir = ROOT / "scripts" / "crawler"
    if not crawler_dir.exists():
        err("scripts/crawler/ 缺失（v2.3 主路径）")
        return
    # 关键类名存在
    class_checks = {
        "doubao.py": ["class DoubaoCrawler", "def ask", "def login", "use_system_chrome"],
        "kimi.py": ["class KimiCrawler", "def ask", "def login", "use_system_chrome"],
        "tongyi.py": ["class TongyiCrawler", "def ask", "def login", "use_system_chrome"],
        "runner.py": ["class GEORunner", "def run_batch", "def save_report"],
    }
    for file, needles in class_checks.items():
        text = read(crawler_dir / file)
        if not text:
            warn(f"v2.3 {file} 无法读取")
            continue
        for needle in needles:
            if needle in text:
                ok(f"v2.3 {file}: {needle}")
            else:
                warn(f"v2.3 {file} 缺: {needle}")
    # run_mixue_demo.sh 应支持 use_system_chrome
    demo_sh = read(ROOT / "examples" / "run_mixue_demo.sh")
    if demo_sh and "USE_SYSTEM_CHROME" in demo_sh:
        ok("examples/run_mixue_demo.sh 支持 USE_SYSTEM_CHROME=1")
    else:
        warn("examples/run_mixue_demo.sh 应支持 USE_SYSTEM_CHROME=1")


def main() -> int:
    print("=" * 60)
    print("GEO 雷达 Skill · 静态模式检查器 (v2.3)")
    print("=" * 60)
    check_required_files()
    check_skill_md_frontmatter()
    check_china_only_and_disclaimer()
    check_skill_md_prohibitions()
    check_subject_lock_and_query_gen()
    check_data_freshness()
    check_report_sections()
    check_label_system()
    check_query_templates()
    check_skill_json()
    check_v23_integration()
    check_v23_crawler_code()
    print("\n" + "=" * 60)
    print(f"汇总: ✅ {len(oks)} pass | ⚠️  {len(warnings)}  warn | ❌ {len(errors)} fail")
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
