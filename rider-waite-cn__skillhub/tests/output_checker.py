#!/usr/bin/env python3
"""
LLM 输出静态检查器

对 LLM 跑完后的解读输出做静态检查，验证 7 节结构、字数、14 禁止项、边界声明、图引用齐全。

运行：
    python3 tests/output_checker.py --input examples/case-001-单抽-感情-愚者.md
    python3 tests/output_checker.py --text "<LLM 输出文本>" --intensity light
    python3 tests/output_checker.py --batch examples/

退出码：
    0 = 全过
    1 = 有 fail
    2 = 有 warn 但无 fail
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# 7 节标题
SECTION_HEADERS = [
    "抽卡确认", "抽卡总览", "牌序揭晓", "单牌解读", "牌阵联动",
    "综合叙事", "行动建议", "边界声明"
]

# 边界声明 4 段
BOUNDARY_KEYWORDS = [
    "娱乐性质", "专业领域", "决策权在你", "复现性"
]

# 14 禁止项违规关键词
PROHIBITED_PHRASES = [
    "一定会", "一定不会", "命中注定", "天意如此",
    "震撼", "必看", "揭秘", "震惊",
    "今天分享", "我来聊聊", "我帮一个朋友",
    "一定发财", "你一定会中", "保证 100%"
]

# intensity 字数范围
INTENSITY_WORD_RANGE = {
    "very-light": (30, 100),
    "light": (200, 400),
    "standard": (600, 1200),
    "deep": (1500, 3000),
    "very-deep": (3000, 50000),
}

# intensity 行动建议数
INTENSITY_ACTION_RANGE = {
    "very-light": (0, 0),
    "light": (0, 1),
    "standard": (1, 1),
    "deep": (1, 2),
    "very-deep": (2, 3),
}


class OutputCheck:
    def __init__(self, text: str, intensity: str = "standard", expected_spread: str = None):
        self.text = text
        self.intensity = intensity
        self.expected_spread = expected_spread
        self.passes: List[str] = []
        self.fails: List[str] = []
        self.warns: List[str] = []

    def run(self) -> Tuple[int, int, int]:
        self.check_sections()
        self.check_word_count()
        self.check_boundary()
        self.check_prohibitions()
        self.check_images()
        self.check_spread_specific()
        return len(self.passes), len(self.warns), len(self.fails)

    def check_sections(self) -> None:
        """7 节齐全检查"""
        for sec in SECTION_HEADERS:
            # 允许标题变体（如"## 抽卡确认" 或 "## Step 1a 抽卡确认"）
            if re.search(rf"^##.*{sec}", self.text, re.MULTILINE):
                self.passes.append(f"7 节: {sec} 存在")
            else:
                # very-light 可能只输出关键段，不是必须 7 节齐全
                if self.intensity == "very-light":
                    self.warns.append(f"7 节: {sec} 缺失（very-light 可放宽）")
                else:
                    self.fails.append(f"7 节: {sec} 缺失")

    def check_word_count(self) -> None:
        """字数检查"""
        # 中文按字符计算（不含 markdown 标记）
        clean = re.sub(r"[#*\-\[\]\(\)\|>`]", "", self.text)
        # 中文字符 + 英文单词
        cn_count = len(re.findall(r"[\u4e00-\u9fff]", clean))
        en_words = len(re.findall(r"[a-zA-Z]+", clean))
        total = cn_count + en_words

        low, high = INTENSITY_WORD_RANGE.get(self.intensity, (600, 1200))
        if low <= total <= high:
            self.passes.append(f"字数 {total}（{low}-{high} {self.intensity}）")
        else:
            if total < low:
                self.warns.append(f"字数 {total} < {low}（{self.intensity} 下限）")
            else:
                self.warns.append(f"字数 {total} > {high}（{self.intensity} 上限）")

    def check_boundary(self) -> None:
        """边界声明 4 段齐全"""
        for kw in BOUNDARY_KEYWORDS:
            if kw in self.text:
                self.passes.append(f"边界声明: {kw}")
            else:
                self.fails.append(f"边界声明缺失: {kw}")

    def check_prohibitions(self) -> None:
        """14 禁止项违规检测"""
        for phrase in PROHIBITED_PHRASES:
            if phrase in self.text:
                self.fails.append(f"禁止项违规: 「{phrase}」")
            else:
                self.passes.append(f"无禁止项: 「{phrase}」")

    def check_images(self) -> None:
        """图引用检查
        兼容两种格式：
        - 本地路径：![XX](assets/cards/major/the-fool.webp)
        - jsdelivr URL：![XX](https://cdn.jsdelivr.net/.../assets/cards/major/the-fool.webp)
        """
        # 兼容两种格式的"assets/cards/"子串匹配
        img_count = len(re.findall(r"!\[.*?\]\([^)]*assets/cards/", self.text))
        if img_count > 0:
            self.passes.append(f"图引用 {img_count} 张（本地/URL 都兼容）")
        else:
            self.warns.append("未发现图引用（assets/cards/... 本地或 URL）")

    def check_spread_specific(self) -> None:
        """特定 spread 检查"""
        if not self.expected_spread:
            return
        # single 必须是 1 张牌
        if self.expected_spread == "single":
            if re.search(r"位置 1", self.text):
                self.passes.append("single: 位置 1 存在")
            else:
                self.fails.append("single: 位置 1 缺失")
        # 抽卡动作（[背] 占位符或用户选牌）
        if "[背" in self.text or "我选" in self.text or "你选的是" in self.text:
            self.passes.append("抽卡动作存在")
        else:
            self.fails.append("抽卡动作缺失（无 [背] / 我选 / 你选的是）")

    def report(self) -> None:
        print(f"\n=== 输出检查报告（intensity={self.intensity}）===")
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
    # 从文件名推 intensity
    intensity = "standard"
    if "凯尔特" in file_path.name or "celtic" in file_path.name.lower():
        intensity = "deep"
    elif "单抽" in file_path.name or "单张" in file_path.name:
        intensity = "light"
    elif "时间流" in file_path.name:
        intensity = "standard"
    spread = None
    if "单抽" in file_path.name or "单张" in file_path.name:
        spread = "single"
    elif "凯尔特" in file_path.name:
        spread = "celtic-cross"
    elif "时间流" in file_path.name:
        spread = "time-flow"

    check = OutputCheck(text, intensity=intensity, expected_spread=spread)
    p, w, f = check.run()
    check.report()
    return 0 if f == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="检查单个文件")
    parser.add_argument("--text", help="检查直接传入的文本")
    parser.add_argument("--intensity", default="standard",
                        choices=list(INTENSITY_WORD_RANGE.keys()))
    parser.add_argument("--spread", help="期望的 spread（如 single）")
    parser.add_argument("--batch", help="批量检查目录下所有 .md")
    args = parser.parse_args()

    if args.batch:
        batch_dir = Path(args.batch)
        files = list(batch_dir.glob("*.md"))
        if not files:
            print(f"❌ 未在 {batch_dir} 找到 .md 文件")
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
        check = OutputCheck(args.text, intensity=args.intensity, expected_spread=args.spread)
        p, w, f = check.run()
        check.report()
        return 0 if f == 0 else 1
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
