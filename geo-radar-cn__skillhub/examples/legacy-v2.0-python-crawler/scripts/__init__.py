"""
GEO 雷达 v2.0 - LLM 平台爬虫模块

通过 Playwright 模拟用户在浏览器里问豆包/Kimi/通义,直接拿真实 LLM 输出。
不需要 API key,需要用户先在浏览器登录各平台(cookie 持久化到 playwright profile)。

平台支持:
    - 豆包 (Doubao)         - 用户量最大,4.4 亿月活
    - Kimi (Moonshot)        - 技术向用户覆盖
    - 通义千问 (Tongyi)      - 阿里系,商业/电商覆盖强

CLI 用法:
    python -m crawler.doubao "推荐 2025 平价奶茶品牌"
    python -m crawler.kimi "..."
    python -m crawler.tongyi "..."

Python API:
    from crawler import DoubaoCrawler, KimiCrawler, TongyiCrawler
    from crawler.runner import GEORunner

    runner = GEORunner(platforms=["doubao", "kimi"])
    runner.login_all()  # 首次:用户手动登录各平台
    results = runner.run_batch(prompts=[
        "推荐 2025 平价奶茶品牌",
        "蜜雪冰城 vs 古茗 哪个好",
        ...
    ])
    report = runner.generate_report(results, brand="蜜雪冰城")
"""

from .doubao import DoubaoCrawler, CrawlResult as DoubaoResult
from .kimi import KimiCrawler, CrawlResult as KimiResult
from .tongyi import TongyiCrawler, CrawlResult as TongyiResult
from .runner import GEORunner

__all__ = [
    "DoubaoCrawler",
    "KimiCrawler",
    "TongyiCrawler",
    "GEORunner",
]
