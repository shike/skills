"""
通义千问 (Tongyi Qianwen) 爬虫 - GEO 雷达 v2.0 核心模块

阿里云通义,商业覆盖强(电商/云服务场景)。
与 doubao.py / kimi.py 结构一致。

用法:
    from tongyi import TongyiCrawler
    crawler = TongyiCrawler(headless=False)
    result = crawler.ask("推荐 2025 平价奶茶品牌")

环境要求: 同 doubao.py
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CrawlResult:
    """单次问询的结果"""
    platform: str = "tongyi"
    prompt: str = ""
    text: str = ""
    citations: list = field(default_factory=list)
    screenshot_path: Optional[str] = None
    timestamp: float = 0.0
    duration_sec: float = 0.0
    success: bool = False
    error: Optional[str] = None


class TongyiCrawler:
    """通义千问爬虫"""

    PLATFORM_URL = "https://tongyi.aliyun.com/qianwen/"
    QUERY_INPUT_SELECTOR = 'textarea[placeholder*="输入"], textarea.ant-input'
    SUBMIT_BUTTON_SELECTOR = 'button[class*="send"], button[type="button"][aria-label*="发送"]'
    RESPONSE_CONTAINER_SELECTOR = 'div[class*="answer-content"], div[class*="markdown"]'
    CITATION_LINK_SELECTOR = 'a[href*="http"]'

    def __init__(self, headless: bool = False, profile_dir: Optional[Path] = None,
                 interval_sec: float = 3.0, timeout_sec: float = 60.0):
        self.headless = headless
        self.profile_dir = profile_dir or Path.home() / ".geo-radar-cn" / "browser-profile-tongyi"
        self.interval_sec = interval_sec
        self.timeout_sec = timeout_sec
        self._context = None
        self._page = None
        self._pw = None

    def _ensure_browser(self):
        if self._context is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "playwright 未安装。请运行: pip install playwright && playwright install chromium"
            )

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        pw = sync_playwright().start()
        self._pw = pw

        self._context = pw.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.timeout_sec * 1000)

    def login(self) -> bool:
        self._ensure_browser()
        self._page.goto(self.PLATFORM_URL)
        print(f"[*] 请在浏览器中手动登录通义千问。登录完成后,按 Enter 继续...")
        input()
        self._page.reload()
        time.sleep(2)
        if "login" in self._page.url.lower():
            print("[!] 仍在登录页,请重试")
            return False
        print("[+] 登录成功,cookie 已保存到:", self.profile_dir)
        return True

    def ask(self, prompt: str, screenshot: bool = True) -> CrawlResult:
        self._ensure_browser()
        result = CrawlResult(prompt=prompt, timestamp=time.time())
        start = time.time()

        try:
            if "tongyi.aliyun.com" not in self._page.url:
                self._page.goto(self.PLATFORM_URL)
                time.sleep(2)

            input_box = self._page.locator(self.QUERY_INPUT_SELECTOR).first
            input_box.wait_for(state="visible", timeout=10000)
            input_box.fill("")
            input_box.fill(prompt)
            time.sleep(0.5)

            try:
                self._page.locator(self.SUBMIT_BUTTON_SELECTOR).first.click(timeout=2000)
            except Exception:
                input_box.press("Enter")
            time.sleep(1)

            response = self._page.locator(self.RESPONSE_CONTAINER_SELECTOR).last
            response.wait_for(state="visible", timeout=self.timeout_sec * 1000)
            prev_len = -1
            stable_count = 0
            for _ in range(30):
                time.sleep(2)
                cur_text = response.inner_text()
                if len(cur_text) == prev_len and len(cur_text) > 10:
                    stable_count += 1
                    if stable_count >= 2:
                        break
                else:
                    stable_count = 0
                prev_len = len(cur_text)

            result.text = response.inner_text()

            citations = self._page.locator(self.CITATION_LINK_SELECTOR).all()
            seen_urls = set()
            result.citations = []
            for c in citations:
                href = c.get_attribute("href")
                if href and href.startswith("http") and href not in seen_urls:
                    seen_urls.add(href)
                    result.citations.append({"title": c.inner_text().strip()[:80], "url": href})

            if screenshot:
                screenshot_dir = self.profile_dir / "screenshots"
                screenshot_dir.mkdir(exist_ok=True)
                ts = int(time.time() * 1000)
                shot_path = screenshot_dir / f"tongyi_{ts}.png"
                self._page.screenshot(path=str(shot_path), full_page=True)
                result.screenshot_path = str(shot_path)

            result.success = True

        except Exception as e:
            result.error = str(e)
            result.success = False

        finally:
            result.duration_sec = time.time() - start
            time.sleep(self.interval_sec)

        return result

    def close(self):
        if self._context is not None:
            self._context.close()
        if self._pw is not None:
            self._pw.stop()
        self._context = None
        self._page = None
        self._pw = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    import sys

    crawler = TongyiCrawler(headless=False)
    try:
        crawler.login()
        prompt = sys.argv[1] if len(sys.argv) > 1 else "推荐 2025 平价奶茶品牌"
        result = crawler.ask(prompt)
        print(f"\n[+] prompt: {result.prompt}")
        print(f"[+] duration: {result.duration_sec:.1f}s")
        print(f"[+] text: {result.text[:300]}{'...' if len(result.text) > 300 else ''}")
        print(f"[+] citations ({len(result.citations)}):")
        for c in result.citations[:5]:
            print(f"    - {c['title']}: {c['url']}")
    finally:
        crawler.close()
