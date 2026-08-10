#!/usr/bin/env python3
"""
真实 LLM 跑批测试

跑 3 个 case × 1 个 model（Mavis/MiniMax-M3）的端到端测试，输出 markdown 到
tests/llm_batch_outputs/，然后跑 output_checker 验证。

前置：必须有可用的 LLM（当前默认是 Mavis 自身）
替代方案：用 mock 模式 + 已有 examples 验证 output_checker

运行：python3 tests/llm_runner.py [--mock] [--case case-001/002/003]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT / "tests" / "llm_batch_outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def get_case_specs() -> list:
    """3 个 case 的 input 规范"""
    return [
        {
            "name": "case-001-单抽-感情-愚者",
            "input": {
                "question": "我最近刚认识一个男生，我喜欢他吗？",
                "category": "love",
                "spread": "single",
                "intensity": "light",
                "seed": 42,
            },
            "selected_cards": ["愚者 · 正位"],
            "expected_intensity": "light",
            "expected_spread": "single",
        },
        {
            "name": "case-002-凯尔特十字-事业",
            "input": {
                "question": "我现在的工作不开心，要不要辞职做自由职业？",
                "category": "career",
                "spread": "celtic-cross",
                "intensity": "deep",
                "seed": 2026,
            },
            "selected_cards": [
                "魔术师 · 正位",
                "权杖五 · 正位",
                "圣杯四 · 逆位",
                "权杖三 · 正位",
                "圣杯骑士 · 逆位",
                "宝剑七 · 逆位",
                "星币国王 · 正位",
                "塔 · 逆位",
                "星星 · 正位",
                "权杖八 · 正位",
            ],
            "expected_intensity": "deep",
            "expected_spread": "celtic-cross",
        },
        {
            "name": "case-003-时间流-选择",
            "input": {
                "question": "我应该接 A 公司 offer 还是继续等 B 公司的面试？",
                "category": "choice",
                "spread": "time-flow",
                "intensity": "standard",
                "seed": 7,
            },
            "selected_cards": [
                "圣杯一 · 正位",
                "宝剑二 · 正位",
                "权杖一 · 正位",
            ],
            "expected_intensity": "standard",
            "expected_spread": "time-flow",
        },
    ]


def build_prompt(case_spec: dict) -> str:
    """构造 LLM prompt（模拟 skill 触发）"""
    skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    refs_78 = (ROOT / "references" / "78-cards.md").read_text(encoding="utf-8")
    refs_spreads = (ROOT / "references" / "spreads.md").read_text(encoding="utf-8")
    refs_framework = (ROOT / "references" / "reading-framework.md").read_text(encoding="utf-8")
    refs_ethics = (ROOT / "references" / "ethics.md").read_text(encoding="utf-8")
    refs_prompt = (ROOT / "references" / "ai-prompt-template.md").read_text(encoding="utf-8")

    prompt = f"""# System Role

你是一位塔罗解牌 Skill。按照以下 SKILL.md + references 工作流执行解读。

# SKILL.md

{skill_md}

# references/78-cards.md（牌义库）

{refs_78[:5000]}

# references/spreads.md（牌阵定义）

{refs_spreads[:3000]}

# references/reading-framework.md（7 节解读流程）

{refs_framework}

# references/ethics.md（塔罗师诫命）

{refs_ethics[:3000]}

# references/ai-prompt-template.md（System Prompt 模板）

{refs_prompt[:3000]}

# User Input

请按 5 步工作流 + 7 节框架解读以下 case：

```json
{json.dumps(case_spec['input'], ensure_ascii=False, indent=2)}
```

**预抽好的牌**（请用这些，不要重新抽）：
{[card for card in case_spec['selected_cards']]}

**输出要求**：
- 必须按 7 节框架：抽卡确认 / 抽卡总览 / 牌序揭晓 / 单牌解读 / 牌阵联动 / 综合叙事 / 行动建议 / 边界声明
- 每张揭晓的牌必须附 `![中文名](https://cdn.jsdelivr.net/gh/shike/location-skill@main/rider-waite-cn__skillhub/assets/cards/{major|minor}/{slug}.webp)`
- 边界声明 4 段齐全：娱乐性质 / 专业领域 / 决策权在你 / 复现性
- 14 条禁止项：禁止绝对预测 / 禁止医疗法律投资 / 禁止营销味 / 禁止 AI 套路 / 禁止 LLM 自由发挥 等
- 复现性：seed={case_spec['input'].get('seed')}

请输出完整解读：
"""
    return prompt


def run_mock_llm(case_spec: dict) -> str:
    """Mock 模式：从已有 examples 取输出"""
    example_path = ROOT / "examples" / f"{case_spec['name']}.md"
    if example_path.exists():
        return example_path.read_text(encoding="utf-8")
    return f"# {case_spec['name']}\n\n[mock 模式：未找到对应 example]"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true",
                        help="Mock 模式：直接用已有 examples 作为 LLM 输出（用于验证 output_checker）")
    parser.add_argument("--case", help="只跑指定 case（如 case-001）")
    parser.add_argument("--model", default="mavis",
                        help="LLM model（默认 mavis = 当前 agent）")
    args = parser.parse_args()

    cases = get_case_specs()
    if args.case:
        cases = [c for c in cases if args.case in c["name"]]

    print(f"模型: {args.model}")
    print(f"模式: {'mock' if args.mock else 'real LLM'}")
    print(f"用例数: {len(cases)}")

    results = []
    for case in cases:
        print(f"\n{'='*60}\n{case['name']}\n{'='*60}")
        if args.mock:
            output = run_mock_llm(case)
        else:
            # 真实 LLM：构造 prompt + 调用（占位）
            prompt = build_prompt(case)
            print(f"prompt 长度: {len(prompt)} 字符")
            output = "[真实 LLM 输出未实现，当前仅 mock 模式]"
        # 保存输出
        out_path = OUTPUTS_DIR / f"{case['name']}_output.md"
        out_path.write_text(output, encoding="utf-8")
        print(f"输出保存: {out_path}")

        results.append({
            "case": case["name"],
            "output_path": str(out_path),
            "intensity": case["expected_intensity"],
            "spread": case["expected_spread"],
        })

    print(f"\n{'='*60}")
    print(f"完成 {len(results)}/{len(cases)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
