#!/usr/bin/env python3
"""
GEO 雷达 Skill · LLM 输出静态检查器

对 LLM 跑完后的 GEO 报告做静态检查，验证：
- 8 节主体齐全
- 3 附录（立即可执行 3 步 / 数据局限 / 30 天行动清单）
- 数据来源 + 免责声明
- 数据时效分布表（头部，🟢+🟡 ≥ 80%, 🔴 ≤ 10%）
- 4 维品牌可见度分（被引用频次 / 推荐度 / 内容质量 / 平台覆盖）
- 4 维标签系统（来源等级 / 置信度 / 推算依据 / 决策可执行性）
- 14 禁止项
- 主语锁定
- 竞品对比（5-10 竞品）
- 行动清单 3 类 + 4 维评估
- 资金准备 3 大类 + 3-5 条红线

运行：
    python3 tests/output_checker.py --input examples/test-run-2026-08-10-蜜雪冰城-high.md
    python3 tests/output_checker.py --batch examples/

退出码：
    0 = 全过
    1 = 有 fail
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# 8 节标题
SECTION_HEADERS = [
    "摘要卡", "品牌可见度分", "查询词覆盖", "竞品对比",
    "AI 引擎引用源分析", "优化机会清单", "数据局限", "行动清单",
]

# 4 维品牌可见度
VISIBILITY_DIMENSIONS = ["被引用频次", "推荐度", "内容质量", "平台覆盖"]

# 6 维风险维度(GEO 雷达版,与 site-intelligence 不同,改成 GEO 风险)
RISK_DIMENSIONS = ["平台依赖", "数据时效", "竞品压力", "内容质量", "资源投入", "差异化定位"]

# 14 禁止项违规关键词
PROHIBITED_PHRASES = [
    # 主语 1-3
    "如果换品牌为 X",  # 应仅 1 句背景说明
    # 表达 8-11
    "必赚", "稳赚不赔", "保证赚钱",
    "震撼", "必看", "揭秘", "震惊", "惊呆",
    "今天分享", "我来聊聊", "我帮一个朋友", "你一定要听",
    "AI 速成", "保姆级", "震撼", "震撼来袭",
    # 数据 12-14（用模型记忆 / 编造 / 改动用户输入是 LLM 端行为,文本里不会直接出现）
]

# 4 维标签 - 来源等级 5 类
SOURCE_LABELS = ["🏛️", "📊", "📰", "🏪", "👤"]
# 置信度 3 档
CONFIDENCE_LABELS = ["🟢", "🟡", "🔴"]
# 决策可执行性 3 档
ACTIONABILITY_LABELS = ["✅", "⚠️", "❌"]


class OutputCheck:
    def __init__(self, text: str, main_brand: str = None):
        self.text = text
        self.main_brand = main_brand
        self.passes: List[str] = []
        self.fails: List[str] = []
        self.warns: List[str] = []

    def run(self) -> Tuple[int, int, int]:
        self.check_main_sections()
        self.check_appendix()
        self.check_data_freshness_table()
        self.check_visibility_dimensions()
        self.check_label_system()
        self.check_subject_lock()
        self.check_prohibitions()
        self.check_action_list()
        self.check_funding_breakdown()
        self.check_disclaimer()
        return len(self.passes), len(self.warns), len(self.fails)

    def check_main_sections(self) -> None:
        """8 节主体齐全"""
        for sec in SECTION_HEADERS:
            # 允许标题变体（"## 一 摘要卡" / "## 摘要卡" / "## 一、摘要卡"）
            if re.search(rf"^##.*{sec}", self.text, re.MULTILINE):
                self.passes.append(f"8 节: {sec} 存在")
            else:
                self.fails.append(f"8 节缺失: {sec}")

    def check_appendix(self) -> None:
        """3 附录齐全"""
        for app in ["附录 A", "附录 B", "附录 C"]:
            if re.search(rf"^##.*{app}", self.text, re.MULTILINE):
                self.passes.append(f"附录: {app}")
            else:
                self.fails.append(f"附录缺失: {app}")

    def check_data_freshness_table(self) -> None:
        """数据时效分布表"""
        if re.search(r"数据时效", self.text) and re.search(r"🟢.*🟡.*🟠.*🔴", self.text, re.DOTALL):
            self.passes.append("数据时效分布表存在")
        else:
            self.fails.append("数据时效分布表缺失")
        if re.search(r"🟢\+🟡.*≥ 80%|🟢\s*\+\s*🟡.*80", self.text):
            self.passes.append("🟢+🟡 ≥ 80% 硬指标")
        else:
            self.warns.append("🟢+🟡 ≥ 80% 硬指标描述缺失")
        if re.search(r"🔴.*≤ 10%|🔴\s*≤\s*10", self.text):
            self.passes.append("🔴 ≤ 10% 硬指标")
        else:
            self.warns.append("🔴 ≤ 10% 硬指标描述缺失")

    def check_visibility_dimensions(self) -> None:
        """4 维品牌可见度子分"""
        for dim in VISIBILITY_DIMENSIONS:
            if dim in self.text:
                self.passes.append(f"可见度维度: {dim}")
            else:
                self.fails.append(f"可见度维度缺失: {dim}")
        # 综合分
        if re.search(r"综合分|综合评分", self.text):
            self.passes.append("品牌可见度综合分")
        else:
            self.fails.append("品牌可见度综合分缺失")

    def check_label_system(self) -> None:
        """4 维标签系统"""
        src_count = sum(1 for s in SOURCE_LABELS if s in self.text)
        if src_count == 5:
            self.passes.append("来源等级 5 类齐全")
        elif src_count >= 3:
            self.warns.append(f"来源等级仅 {src_count}/5 类")
        else:
            self.fails.append(f"来源等级缺失严重: {src_count}/5")
        conf_count = sum(1 for c in CONFIDENCE_LABELS if c in self.text)
        if conf_count >= 2:
            self.passes.append(f"置信度 {conf_count}/3 档")
        else:
            self.warns.append(f"置信度仅 {conf_count}/3 档")
        act_count = sum(1 for a in ACTIONABILITY_LABELS if a in self.text)
        if act_count >= 2:
            self.passes.append(f"决策可执行性 {act_count}/3 档")
        else:
            self.warns.append(f"决策可执行性仅 {act_count}/3 档")

    def check_subject_lock(self) -> None:
        """主语锁定 — 主品牌在摘要卡"""
        if not self.main_brand:
            if "主品牌" in self.text or re.search(r"主语锁定", self.text):
                self.passes.append("主语锁定声明存在")
            else:
                self.warns.append("主语锁定声明缺失")
            return
        # 检查主品牌在摘要卡(兼容 "## 一 摘要卡" / "## 摘要卡" / "## 一、摘要卡" 等格式)
        summary_match = re.search(
            r"^##\s*[一二三四五六七八九十]?[、\s]*摘要卡(.*?)(?=^##\s*[一二三四五六七八九十][、\s])",
            self.text, re.MULTILINE | re.DOTALL
        )
        if summary_match:
            summary_text = summary_match.group(1)
            # 接受全名或前 2 字简称（如"蜜雪冰城" → "蜜雪"）
            short_name = self.main_brand[:2]
            if self.main_brand in summary_text or short_name in summary_text:
                self.passes.append(f"主品牌 {self.main_brand} 在摘要卡")
            else:
                self.fails.append(f"主品牌 {self.main_brand} 不在摘要卡")
        else:
            self.warns.append("摘要卡段落无法定位（标题格式可能变化）")

    def check_prohibitions(self) -> None:
        """14 禁止项违规检测"""
        for phrase in PROHIBITED_PHRASES:
            if phrase in self.text:
                self.fails.append(f"禁止项违规: 「{phrase}」")
            else:
                self.passes.append(f"无禁止项: 「{phrase}」")

    def check_action_list(self) -> None:
        """行动清单 3 类分 + 4 维评估"""
        # 3 类 - 兼容不同叫法
        action_3_categories = {
            "立即做": ["立即做", "立即可签", "必做", "0 成本"],
            "中期": ["中期", "中期投入", "需预算"],
            "长期": ["长期", "长期建设", "战略", "3-12 月"],
        }
        for cat, equivalents in action_3_categories.items():
            if any(eq in self.text for eq in equivalents):
                self.passes.append(f"行动清单: {cat}")
            else:
                self.fails.append(f"行动清单缺失: {cat}")
        # 4 维评估
        dims = ["成本", "收益", "风险", "决策可执行性"]
        dim_count = sum(1 for d in dims if d in self.text)
        if dim_count >= 3:
            self.passes.append(f"行动清单 4 维评估: {dim_count}/4")
        else:
            self.warns.append(f"行动清单 4 维评估仅 {dim_count}/4")
        # 红线
        if "红线" in self.text or "立即放弃" in self.text:
            self.passes.append("红线条款")
        else:
            self.warns.append("红线条款缺失")

    def check_funding_breakdown(self) -> None:
        """资金准备 3 大类"""
        funding_cats = ["立即执行", "中期投入", "长期建设", "开业", "爬坡", "突发"]
        funding_count = sum(1 for c in funding_cats if c in self.text)
        if funding_count >= 3:
            self.passes.append(f"资金准备: {funding_count} 类相关")
        else:
            self.warns.append(f"资金准备仅 {funding_count} 类相关")

    def check_disclaimer(self) -> None:
        """免责声明 4 部分齐全"""
        if re.search(r"##\s*免责声明", self.text):
            self.passes.append("免责声明章节存在")
        else:
            self.fails.append("免责声明章节缺失")
        for sec in ["数据来源说明", "使用限制", "重要提醒", "授权"]:
            if sec in self.text:
                self.passes.append(f"免责声明: {sec}")
            else:
                self.warns.append(f"免责声明缺失: {sec}")

    def report(self) -> None:
        print(f"\n=== 输出检查报告 ===")
        print(f"✅ {len(self.passes)} pass | ⚠️  {len(self.warns)} warn | ❌ {len(self.fails)} fail\n")
        for p in self.passes:
            print(f"✅ {p}")
        for w in self.warns:
            print(f"⚠️  {w}")
        for f in self.fails:
            print(f"❌ {f}")


def check_file(file_path: Path) -> int:
    """检查单个文件"""
    text = file_path.read_text(encoding="utf-8")
    # 从文件名推主品牌
    main_brand = None
    if "蜜雪冰城" in file_path.name:
        main_brand = "蜜雪冰城"
    elif "nihaovisit" in file_path.name:
        main_brand = "nihaovisit.com"
    elif "startupX" in file_path.name or "初创" in file_path.name:
        main_brand = "startupX"

    check = OutputCheck(text, main_brand=main_brand)
    p, w, f = check.run()
    check.report()
    return 0 if f == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="检查单个文件")
    parser.add_argument("--text", help="检查直接传入的文本")
    parser.add_argument("--brand", help="主品牌（用于主语锁定检查）")
    parser.add_argument("--batch", help="批量检查目录下所有 .md")
    args = parser.parse_args()

    if args.batch:
        batch_dir = Path(args.batch)
        files = list(batch_dir.glob("test-run-*.md")) + list(batch_dir.glob("*_output.md"))
        if not files:
            print(f"❌ 未在 {batch_dir} 找到 test-run-*.md 或 *_output.md 文件")
            return 1
        total_fail = 0
        for f in files:
            print(f"\n{'='*60}\n{f.name}\n{'='*60}")
            if check_file(f) != 0:
                total_fail += 1
        print(f"\n{'='*60}")
        print(f"批量结果: {len(files) - total_fail}/{len(files)} 全过")
        return 0 if total_fail == 0 else 1
    elif args.input:
        return check_file(Path(args.input))
    elif args.text:
        check = OutputCheck(args.text, main_brand=args.brand)
        p, w, f = check.run()
        check.report()
        return 0 if f == 0 else 1
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
