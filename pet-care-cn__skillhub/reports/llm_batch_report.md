# LLM 跑批报告

> **跑批时间**:2026-08-16
> **跑批模式**:simulate(基于模板 + safe-boundary 自动生成预期输出)
> **任务数**:5
> **结果文件**:`tests/llm_batch_outputs/run-2026-08-16-*.md`
> **下一步**:运行 `python3 tests/output_checker.py` 验证边界是否守住

---

## 跑批任务

| # | 任务 ID | 场景 | 输出文件 |
|---|---|---|---|
| 1 | `typical-3m-cat-arrival` | 典型场景:3 月龄英短幼猫到家 | `tests/llm_batch_outputs/run-2026-08-16-typical-3m-cat-arrival.md` |
| 2 | `boundary-cat-urinates` | 边界场景:2 岁公猫突然乱尿 | `tests/llm_batch_outputs/run-2026-08-16-boundary-cat-urinates.md` |
| 3 | `complex-senior-dog` | 复杂场景:12 岁金毛临终关怀 | `tests/llm_batch_outputs/run-2026-08-16-complex-senior-dog.md` |
| 4 | `exotic-turtle-anorexia` | v2.0 异宠场景:5 岁巴西龟拒食 7 天 | `tests/llm_batch_outputs/run-2026-08-16-exotic-turtle-anorexia.md` |
| 5 | `exotic-parrot-feather-plucking` | v2.0 异宠场景:3 岁灰机持续啄羽 | `tests/llm_batch_outputs/run-2026-08-16-exotic-parrot-feather-plucking.md` |

---

## 跑批结果

- ✅ 5 个任务全部完成
- 每个任务生成 1 份输出文件
- 输出文件包含:输入元数据 / 7 步工作流 / 6 节完整输出 / 边界自检

## 下一步:边界验证

```bash
python3 tests/output_checker.py
```

应输出:
- 3 个任务全部通过
- 9 条诫命全部守住
- 必含关键词全部命中
- 必不含禁词全部避开
