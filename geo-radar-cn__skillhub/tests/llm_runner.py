#!/usr/bin/env python3
"""
GEO 雷达 Skill · 真实 LLM 跑批测试

跑 3 个 case × 1 个 model（Mavis/MiniMax-M3）的端到端测试，输出 markdown 到
tests/llm_batch_outputs/，然后跑 output_checker 验证。

3 个 case 覆盖高/中/低数据丰富度（参考 references/chaos-cases.md）：
- 高数据：蜜雪冰城（奶茶行业龙头）
- 中数据：nihaovisit.com（垂直旅游平台）
- 低数据：某初创品牌 startupX（数据必然稀缺）

前置：必须有可用的 LLM（当前默认是 Mavis 自身）
替代方案：用 mock 模式 + 已有 examples 验证 output_checker

运行：python3 tests/llm_runner.py [--mock] [--case mixue|nihaovisit|startupx]
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
    """3 个 case 的 input 规范（覆盖高/中/低数据）"""
    return [
        {
            "name": "mixue-蜜雪冰城",
            "input": {
                "brand": "蜜雪冰城",
                "queries": None,  # 自动生成
                "category": "奶茶",
                "competitors": None,
            },
            "data_richness": "high",
            "expected_verdict": "🟡",
            "expected_main_brand": "蜜雪冰城",
            "expected_section_count": 8,
        },
        {
            "name": "nihaovisit-入境游",
            "input": {
                "brand": "nihaovisit.com",
                "queries": ["北京旅游攻略", "中国签证", "外国人来华"],
                "category": "旅游",
                "competitors": None,
            },
            "data_richness": "medium",
            "expected_verdict": "🟠",  # 中数据时效偏旧
            "expected_main_brand": "nihaovisit.com",
            "expected_section_count": 8,
        },
        {
            "name": "startupx-初创AI",
            "input": {
                "brand": "startupX",
                "queries": None,
                "category": "AI 写作工具",
                "competitors": None,
            },
            "data_richness": "low",
            "expected_verdict": "🔴",  # 数据稀缺
            "expected_main_brand": "startupX",
            "expected_section_count": 8,
        },
    ]


def build_prompt(case_spec: dict) -> str:
    """构造 LLM prompt（模拟 skill 触发）"""
    skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    refs_schema = (ROOT / "references" / "report-schema.md").read_text(encoding="utf-8")
    refs_templates = (ROOT / "references" / "query-templates.md").read_text(encoding="utf-8")
    refs_prompts = (ROOT / "references" / "web-search-prompts.md").read_text(encoding="utf-8")

    prompt = f"""# System Role

你是一位 GEO 雷达 Skill。按照以下 SKILL.md + references 工作流执行 GEO 可见度诊断。

# SKILL.md

{skill_md[:8000]}

# references/report-schema.md（8 节 + 4 维可见度分 + 标签系统 + 资金分配）

{refs_schema[:5000]}

# references/query-templates.md（8 行业 × 4 类型查询词模板）

{refs_templates[:4000]}

# references/web-search-prompts.md（24 个 web_search prompt）

{refs_prompts[:3000]}

# User Input

请按 7 步工作流 + 4 大 Hard Constraint（主语锁定 / 数据时效 / 标签系统 / 8 节报告）输出 GEO 可见度诊断报告：

```json
{json.dumps(case_spec['input'], ensure_ascii=False, indent=2)}
```

**输出要求**：
- 必须 8 节主体（摘要卡 / 品牌可见度分 / 查询词覆盖 / 竞品对比 / AI 引擎引用源分析 / 优化机会清单 / 数据局限 / 行动清单）
- 必须 3 附录（A 立即可执行 3 步 / B 数据局限 / C 30 天行动清单）
- 数据来源 + 免责声明
- 数据时效分布表：🟢+🟡 ≥ 80%，🔴 ≤ 10%
- 4 维品牌可见度子分（被引用频次 / 推荐度 / 内容质量 / 平台覆盖）
- 4 维标签：来源等级（🏛️/📊/📰/🏪/👤）+ 置信度（🟢/🟡/🔴）+ 推算依据 + 决策可执行性（✅/⚠️/❌）
- 行动清单 3 类分（立即做 / 中期 / 长期）+ 4 维评估（成本/收益/风险/决策可执行性）
- 资金准备 3 大类（立即执行 / 中期投入 / 长期建设）+ 3-5 条红线
- 主语锁定：主品牌在摘要卡 ≥1 次，可见度分基于主品牌

**诚实声明**：报告第 7 节"数据局限"必须明示 v1.0 能力边界（web_search 抓不到国内 AI 引擎内容）

请输出完整报告：
"""
    return prompt


def run_mock_llm(case_spec: dict) -> tuple:
    """Mock 模式：从已有 examples 取输出
    返回 (output_text, has_baseline) — has_baseline=False 表示无范本,verify 跳过
    """
    example_map = {
        "mixue-蜜雪冰城": "test-run-2026-08-10-蜜雪冰城-high.md",
        "nihaovisit-入境游": "test-run-2026-08-10-nihaovisit-medium.md",
        "startupx-初创AI": "test-run-2026-08-10-某初创品牌-low.md",
    }
    example_name = example_map.get(case_spec["name"])
    if example_name:
        example_path = ROOT / "examples" / example_name
        if example_path.exists():
            return example_path.read_text(encoding="utf-8"), True
    placeholder = f"""# GEO 雷达报告 · {case_spec['input']['brand']} · 2026-08-10

[mock 模式：此 case 暂无完整范本，跳过 output_checker 验证]

## 数据时效分布
- 🟢 50% / 🟡 20% / 🟠 20% / 🔴 10%

## 一 摘要卡
🔴 数据稀缺

[placeholder - 需 LLM 真实跑批]
"""
    return placeholder, False


def verify_output(output_path: Path, case_spec: dict) -> dict:
    """跑 output_checker 验证单个输出"""
    try:
        sys.path.insert(0, str(ROOT / "tests"))
        from output_checker import OutputCheck
        text = output_path.read_text(encoding="utf-8")
        check = OutputCheck(text, main_brand=case_spec.get("expected_main_brand"))
        p, w, f = check.run()
        return {"pass": p, "warn": w, "fail": f, "ok": f == 0}
    except Exception as e:
        return {"pass": 0, "warn": 0, "fail": 1, "ok": False, "error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true",
                        help="Mock 模式：直接用已有 examples 作为 LLM 输出（用于验证 output_checker）")
    parser.add_argument("--case", help="只跑指定 case（mixue/nihaovisit/startupx）")
    parser.add_argument("--model", default="mavis",
                        help="LLM model（默认 mavis = 当前 agent）")
    parser.add_argument("--no-verify", action="store_true",
                        help="跳过 output_checker 验证")
    args = parser.parse_args()

    cases = get_case_specs()
    if args.case:
        cases = [c for c in cases if args.case.lower() in c["name"].lower()]

    print(f"模型: {args.model}")
    print(f"模式: {'mock' if args.mock else 'real LLM'}")
    print(f"用例数: {len(cases)}")
    richness_summary = ", ".join(f"{c['name']}={c['data_richness']}" for c in cases)
    print(f"数据丰富度: {richness_summary}")

    results = []
    for case in cases:
        print(f"\n{'='*60}\n{case['name']}（{case['data_richness']} 数据）\n{'='*60}")
        if args.mock:
            output, has_baseline = run_mock_llm(case)
        else:
            prompt = build_prompt(case)
            print(f"prompt 长度: {len(prompt)} 字符")
            output = "[真实 LLM 输出未实现，当前仅 mock 模式]"
            has_baseline = False

        # 保存输出（无 baseline 的 case 用 .placeholder 后缀,batch checker 跳过）
        suffix = "_output.placeholder" if not has_baseline else "_output.md"
        out_path = OUTPUTS_DIR / f"{case['name']}{suffix}"
        out_path.write_text(output, encoding="utf-8")
        print(f"输出保存: {out_path}")
        print(f"输出长度: {len(output)} 字符")

        # 验证
        if not args.no_verify and has_baseline:
            verify_result = verify_output(out_path, case)
            print(f"output_checker: {verify_result['pass']} pass / "
                  f"{verify_result['warn']} warn / {verify_result['fail']} fail"
                  f" {'✅' if verify_result['ok'] else '❌'}")
        elif not has_baseline:
            verify_result = {"ok": True, "skipped": True,
                             "reason": "无范本,跳过 verify"}
            print(f"⏭️  跳过 verify: {verify_result['reason']}")
        else:
            verify_result = {"ok": True, "skipped": True}

        results.append({
            "case": case["name"],
            "data_richness": case["data_richness"],
            "output_path": str(out_path),
            "has_baseline": has_baseline,
            "verify": verify_result,
        })

    # 汇总
    print(f"\n{'='*60}")
    total = len(results)
    real_count = sum(1 for r in results if r["verify"].get("ok") and not r["verify"].get("skipped"))
    skipped_count = sum(1 for r in results if r["verify"].get("skipped"))
    fail_count = sum(1 for r in results if not r["verify"].get("ok") and not r["verify"].get("skipped"))
    print(f"完成 {real_count}/{total - skipped_count} 真实 verify（{skipped_count} skipped）")
    if not args.no_verify:
        for r in results:
            v = r["verify"]
            if v.get("skipped"):
                status = "⏭️ "
                detail = "skipped"
            else:
                status = "✅" if v.get("ok") else "❌"
                detail = f"{v.get('pass', 0)} pass / {v.get('warn', 0)} warn / {v.get('fail', 0)} fail"
            print(f"  {status} {r['case']}（{r['data_richness']}）: {detail}")
    print("=" * 60)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
