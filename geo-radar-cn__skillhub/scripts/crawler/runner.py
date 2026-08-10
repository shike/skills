"""
GEORunner - GEO 雷达 v2.0 批量跑批 + 报告生成

核心:
1. 接受 prompts + platforms
2. 逐个平台/逐个 prompt 跑爬虫
3. 收集所有 CrawlResult
4. 生成 JSON 报告(供 SKILL.md 的 8 节渲染调用)

注意:
- 实际跑一次: 20-30 prompts × 3 平台 = 60-90 次问询 ≈ 3-12 分钟
- 输出: JSON 报告 + 每平台单独 screenshots/

CLI 用法:
    python -m crawler.runner --brand "蜜雪冰城" --prompts prompts.json
    python -m crawler.runner --brand "蜜雪冰城" --auto-prompts --category 奶茶
"""

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .doubao import DoubaoCrawler, CrawlResult as DoubaoResult
from .kimi import KimiCrawler, CrawlResult as KimiResult
from .tongyi import TongyiCrawler, CrawlResult as TongyiResult


@dataclass
class ReportData:
    """GEO 跑批结果汇总"""
    brand: str = ""
    total_queries: int = 0
    total_platforms: int = 0
    total_success: int = 0
    total_fail: int = 0
    brand_mentions: int = 0  # 品牌在所有回答中出现的次数
    brand_first_position: int = 0  # 品牌首次出现位置(平均)
    brand_citation_count: int = 0
    results: List[dict] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class GEORunner:
    """批量跑批 + 报告生成"""

    # 支持的平台(platform_key: 平台 URL)
    PLATFORMS = {
        "doubao": "https://www.doubao.com/chat/",
        "kimi": "https://kimi.moonshot.cn/",
        "tongyi": "https://tongyi.aliyun.com/qianwen/",
    }

    def __init__(self, platforms: List[str] = None, profile_root: Optional[Path] = None,
                 output_dir: Optional[Path] = None):
        """
        Args:
            platforms: 要跑的平台列表,["doubao", "kimi", "tongyi"] 子集
            profile_root: 各平台 cookie profile 的根目录
            output_dir: 报告输出目录
        """
        self.platforms = platforms or ["doubao", "kimi", "tongyi"]
        self.profile_root = profile_root or Path.home() / ".geo-radar-cn"
        self.output_dir = output_dir or Path.home() / ".geo-radar-cn" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.crawlers = {}  # {platform: crawler_instance}

    def get_crawler(self, platform: str):
        """懒加载爬虫实例"""
        if platform in self.crawlers:
            return self.crawlers[platform]

        profile_dir = self.profile_root / f"browser-profile-{platform}"
        if platform == "doubao":
            self.crawlers[platform] = DoubaoCrawler(
                headless=True, profile_dir=profile_dir
            )
        elif platform == "kimi":
            self.crawlers[platform] = KimiCrawler(
                headless=True, profile_dir=profile_dir
            )
        elif platform == "tongyi":
            self.crawlers[platform] = TongyiCrawler(
                headless=True, profile_dir=profile_dir
            )
        else:
            raise ValueError(f"未知平台: {platform}")
        return self.crawlers[platform]

    def login_all(self):
        """首次使用:用户手动登录每个平台"""
        for platform in self.platforms:
            crawler = self.get_crawler(platform)
            print(f"\n=== 登录 {platform} ===")
            crawler.login()
        print("\n[+] 所有平台登录完成")

    def run_batch(self, prompts: List[str], brand: str,
                  screenshot: bool = True) -> ReportData:
        """
        跑批: 每个 platform × 每个 prompt
        Returns: ReportData
        """
        report = ReportData(
            brand=brand,
            total_queries=len(prompts),
            total_platforms=len(self.platforms),
            generated_at=datetime.now().isoformat(),
        )

        for platform in self.platforms:
            try:
                crawler = self.get_crawler(platform)
            except ValueError as e:
                print(f"[!] 跳过未知平台: {platform}")
                continue

            for prompt in prompts:
                print(f"[*] {platform} <- '{prompt[:50]}...'")
                result = crawler.ask(prompt, screenshot=screenshot)

                if result.success:
                    report.total_success += 1
                    # 检查品牌是否在回答中
                    if brand in result.text:
                        report.brand_mentions += 1
                        # 找品牌首次出现位置
                        pos = result.text.find(brand)
                        report.brand_first_position += pos
                    # 引用源里是否提到品牌
                    for cite in result.citations:
                        if brand in cite.get("title", "") or brand in cite.get("url", ""):
                            report.brand_citation_count += 1
                else:
                    report.total_fail += 1
                    print(f"[!] 失败: {result.error}")

                report.results.append(asdict(result))

        # 平均位置
        if report.brand_mentions > 0:
            report.brand_first_position = report.brand_first_position // report.brand_mentions

        return report

    def save_report(self, report: ReportData, format: str = "json") -> Path:
        """保存报告到文件"""
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_brand = report.brand.replace("/", "_").replace(" ", "_")
        base_name = f"geo_report_{safe_brand}_{ts}"

        if format == "json":
            path = self.output_dir / f"{base_name}.json"
            path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
                            encoding="utf-8")
        elif format == "markdown":
            path = self.output_dir / f"{base_name}.md"
            path.write_text(self._render_markdown(report), encoding="utf-8")
        else:
            raise ValueError(f"未知格式: {format}")

        print(f"[+] 报告已保存: {path}")
        return path

    def _render_markdown(self, report: ReportData) -> str:
        """渲染成 8 节 markdown(供 SKILL.md 8 节结构复用)"""
        md = f"""# GEO 雷达报告 · {report.brand}

**生成时间**: {report.generated_at}
**跑批**: {report.total_platforms} 平台 × {report.total_queries} prompts = {report.total_platforms * report.total_queries} 次问询
**成功**: {report.total_success} / {report.total_success + report.total_fail}

---

## 一、摘要卡

| 指标 | 值 |
|---|---|
| 品牌被提到次数 | **{report.brand_mentions} / {report.total_success}** ({(report.brand_mentions / max(report.total_success, 1) * 100):.0f}%) |
| 平均首次出现位置 | {report.brand_first_position} 字符 |
| 引用源中品牌出现 | {report.brand_citation_count} 次 |

## 二、详细结果(每个平台每个 prompt)

"""
        for r in report.results:
            md += f"\n### {r['platform']} <- {r['prompt'][:80]}\n"
            if r['success']:
                md += f"- **回答**: {r['text'][:200]}{'...' if len(r['text']) > 200 else ''}\n"
                md += f"- **引用源**: {len(r['citations'])} 个\n"
                if r.get('screenshot_path'):
                    md += f"- **截图**: `{r['screenshot_path']}`\n"
            else:
                md += f"- **失败**: {r['error']}\n"
        return md

    def close(self):
        """关闭所有爬虫"""
        for crawler in self.crawlers.values():
            crawler.close()
        self.crawlers = {}


# === CLI 入口 ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEO 雷达 v2.0 跑批")
    parser.add_argument("--brand", required=True, help="主品牌名")
    parser.add_argument("--platforms", default="doubao,kimi,tongyi",
                        help="平台列表(逗号分隔)")
    parser.add_argument("--prompts", help="prompts 文件(JSON 数组)")
    parser.add_argument("--auto-prompts", action="store_true",
                        help="从 references/query-templates.md 自动生成 20-30 个 prompts")
    parser.add_argument("--category", default="", help="自动生成 prompts 时需要的品类")
    parser.add_argument("--login", action="store_true", help="首次使用:手动登录各平台")
    parser.add_argument("--output", default="json", choices=["json", "markdown"])
    args = parser.parse_args()

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    runner = GEORunner(platforms=platforms)

    if args.login:
        runner.login_all()

    # 加载 prompts
    if args.prompts:
        prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8"))
    elif args.auto_prompts:
        # TODO: 从 query-templates.md 自动生成
        print("[!] --auto-prompts 暂未实现,请用 --prompts 指定文件")
        runner.close()
        exit(1)
    else:
        # 演示用:3 个手动 prompts
        prompts = [
            f"推荐 2025 {args.category} 品牌",
            f"{args.brand} 怎么样",
            f"{args.brand} 适合投资吗",
        ]
        print(f"[*] 使用演示 prompts(3 个): {prompts}")

    # 跑批
    print(f"\n[*] 开始跑批: {len(platforms)} 平台 × {len(prompts)} prompts = {len(platforms) * len(prompts)} 次问询")
    print(f"[*] 预计时间: {len(platforms) * len(prompts) * 4 // 60} 分 {len(platforms) * len(prompts) * 4 % 60} 秒\n")

    report = runner.run_batch(prompts, brand=args.brand)
    runner.save_report(report, format=args.output)
    runner.close()

    # 摘要
    print(f"\n=== 跑批完成 ===")
    print(f"品牌 '{args.brand}' 被提到: {report.brand_mentions}/{report.total_success} 次")
    print(f"成功: {report.total_success}, 失败: {report.total_fail}")
