#!/usr/bin/env python3
"""
site-intelligence-report Skill · 真实 LLM 跑批测试

跑 3 个 case × 1 个 model（Mavis/MiniMax-M3）的端到端测试，输出 markdown 到
tests/llm_batch_outputs/，然后跑 output_checker 验证。

3 个 case 覆盖高/中/低数据丰富度（参考 references/test-cases.md）：
- 高数据：北京西单大悦城 · 蜜雪冰城
- 中数据：成都春熙路 · 咖啡店
- 低数据：衡阳解放路 · 张亮麻辣烫

前置：必须有可用的 LLM（当前默认是 Mavis 自身）
替代方案：用 mock 模式 + 已有 examples 验证 output_checker

运行：python3 tests/llm_runner.py [--mock] [--case beijing|chengdu|hengyang]
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
            "name": "beijing-西单大悦城-蜜雪冰城",
            "input": {
                "brand": "蜜雪冰城",
                "address": "北京市西城区西单大悦城 B1 层 A-12",
                "city": "北京",
                "category": "奶茶",
                "expected_rent": 30000,
                "expected_area": 30,
            },
            "data_richness": "high",
            "expected_verdict": "🟡",
            "expected_main_brand": "蜜雪冰城",
            "expected_section_count": 13,  # 10 + 3 附录
        },
        {
            "name": "chengdu-春熙路-咖啡店",
            "input": {
                "brand": "未指定",
                "address": "成都市锦江区春熙路西段 88 号",
                "city": "成都",
                "category": "咖啡",
                "expected_rent": 20000,
                "expected_area": 40,
            },
            "data_richness": "medium",
            "expected_verdict": "🟡",
            "expected_main_brand": None,  # 品类适配分析
            "expected_section_count": 13,
        },
        {
            "name": "hengyang-解放路-张亮麻辣烫",
            "input": {
                "brand": "张亮麻辣烫",
                "address": "湖南省衡阳市蒸湘区解放路 35 号",
                "city": "衡阳",
                "category": "快餐",
                "expected_rent": 8000,
                "expected_area": 50,
            },
            "data_richness": "low",
            "expected_verdict": "🟡",  # 低数据城市默认保守判断
            "expected_main_brand": "张亮麻辣烫",
            "expected_section_count": 13,
        },
    ]


def build_prompt(case_spec: dict) -> str:
    """构造 LLM prompt（模拟 skill 触发）"""
    skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    refs_schema = (ROOT / "references" / "report-schema.md").read_text(encoding="utf-8")
    refs_baseline = (ROOT / "references" / "category-baseline.md").read_text(encoding="utf-8")
    refs_prompts = (ROOT / "references" / "web-search-prompts.md").read_text(encoding="utf-8")

    prompt = f"""# System Role

你是一位选址分析 Skill。按照以下 SKILL.md + references 工作流执行选址尽调。

# SKILL.md

{skill_md[:8000]}

# references/report-schema.md（10 节 + 24 字段定义）

{refs_schema[:5000]}

# references/category-baseline.md（6 品类行业基准）

{refs_baseline[:4000]}

# references/web-search-prompts.md（24 字段 prompt 模板）

{refs_prompts[:3000]}

# User Input

请按工作流 + 5 块必加规则（数据时效/标签系统/3x3 矩阵/概率影响/行动清单+资金）输出选址分析报告：

```json
{json.dumps(case_spec['input'], ensure_ascii=False, indent=2)}
```

**输出要求**：
- 必须 10 节主体（摘要卡/点位信息/周边竞品/人流估算/客群画像/同类门店/风险评估/财务测算/谈判筹码/行动清单）
- 必须 3 附录（A 换品类 / B 数据局限 / C 决策深度 8 项）
- 必须 数据来源 + 免责声明
- 数据时效分布表：🟢+🟡 ≥ 80%，🔴 ≤ 10%
- 3x3 财务敏感性矩阵 + 概率×影响 风险矩阵（6 维）
- 4 维标签：来源等级（🏛️/📊/📰/🏪/👤）+ 置信度（🟢/🟡/🔴）+ 推算依据 + 决策可执行性（✅/⚠️/❌）
- 行动清单 3 类分（立即做/验证/否决）+ 4 维评估（成本/收益/风险/决策可执行性）
- 资金准备 3 大类（开业一次性 60-70% / 爬坡期 15-20% / 突发储备 10-15%）
- 主语锁定：主品牌在摘要卡 ≥1 次，财务模型基于主品牌

请输出完整报告：
"""
    return prompt


def run_mock_llm(case_spec: dict) -> tuple:
    """Mock 模式：从已有 examples 取输出
    返回 (output_text, has_baseline) — has_baseline=False 表示无范本,verify 跳过
    """
    # case 名称映射到 example 文件
    example_map = {
        "beijing-西单大悦城-蜜雪冰城": "test-run-2026-08-10-beijing-xidan.md",
        "chengdu-春熙路-咖啡店": "test-run-2026-08-07-chengdu-coffee.md",
        "hengyang-解放路-张亮麻辣烫": None,  # 暂无范本（低数据 case 留给 LLM 真实跑批）
    }
    example_name = example_map.get(case_spec["name"])
    if example_name:
        example_path = ROOT / "examples" / example_name
        if example_path.exists():
            return example_path.read_text(encoding="utf-8"), True
    placeholder = f"""# {case_spec['name']}

## 数据时效分布

| 等级 | 占比 | 说明 |
|---|---|---|
| 🟢 新鲜 | 0% | < 6 月 |
| 🟡 较新 | 0% | 6-12 月 |
| 🟠 偏旧 | 30% | 1-2 年（全国性数据）|
| 🔴 过期 | 0% | > 2 年 |

**本报告 🟢+🟡 占比 0%**（低数据城市，硬指标不达标，附录 B 已明示）

[mock 模式：此 case（衡阳）暂无范本，跳过 output_checker 验证]
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
    parser.add_argument("--case", help="只跑指定 case（beijing/chengdu/hengyang）")
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
            # 真实 LLM：构造 prompt + 调用（占位）
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

        # 验证（除非 --no-verify 或没有 baseline）
        if not args.no_verify and has_baseline:
            verify_result = verify_output(out_path, case)
            print(f"output_checker: {verify_result['pass']} pass / "
                  f"{verify_result['warn']} warn / {verify_result['fail']} fail"
                  f" {'✅' if verify_result['ok'] else '❌'}")
        elif not has_baseline:
            verify_result = {"ok": True, "skipped": True,
                             "reason": "无范本,跳过 verify（低数据 case 需 LLM 真实跑批）"}
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
