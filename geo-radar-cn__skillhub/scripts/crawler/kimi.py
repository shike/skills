"""
Kimi (Moonshot) 爬虫 - GEO 雷达 v2.0 核心模块

通过 Playwright 模拟用户在浏览器里打开 Kimi,输入 prompt,等回答,抓文本+截图+引用源。
与 doubao.py 结构一致,只换 selector 和 URL。

用法:
    from kimi import KimiCrawler
    crawler = KimiCrawler(headless=False)
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
    platform: str = "kimi"
    prompt: str = ""
    text: str = ""
    citations: list = field(default_factory=list)
    screenshot_path: Optional[str] = None
    timestamp: float = 0.0
    duration_sec: float = 0.0
    success: bool = False
    error: Optional[str] = None


class KimiCrawler:
    """Kimi 爬虫"""

    PLATFORM_URL = "https://kimi.moonshot.cn/"
    QUERY_INPUT_SELECTOR = 'div[contenteditable="true"]'  # Kimi 用 contenteditable div
    SUBMIT_BUTTON_SELECTOR = 'div.send-button, button[type="submit"]'
    RESPONSE_CONTAINER_SELECTOR = 'div.markdown-body, div[class*="message-content"]'
    CITATION_LINK_SELECTOR = 'a[href*="http"][target="_blank"]'  # Kimi 引用通常是新窗口打开

    SYSTEM_CHROME_PATHS = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]

    def __init__(self, headless: bool = False, profile_dir: Optional[Path] = None,
                 interval_sec: float = 3.0, timeout_sec: float = 60.0,
                 use_system_chrome: bool = False):
        self.headless = headless
        self.profile_dir = profile_dir or Path.home() / ".geo-radar-cn" / "browser-profile-kimi"
        self.interval_sec = interval_sec
        self.timeout_sec = timeout_sec
        self.use_system_chrome = use_system_chrome
        self._context = None
        self._page = None
        self._pw = None

    def _find_system_chrome(self) -> Optional[str]:
        for p in self.SYSTEM_CHROME_PATHS:
            if Path(p).exists():
                return p
        return None

    def _ensure_browser(self):
        if self._context is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "playwright 未安装。请运行: pip install playwright"
            )

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        pw = sync_playwright().start()
        self._pw = pw

        launch_kwargs = dict(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        if self.use_system_chrome:
            sys_chrome = self._find_system_chrome()
            if sys_chrome:
                launch_kwargs["executable_path"] = sys_chrome
                print(f"[*] 使用系统 Chrome: {sys_chrome}")
            else:
                print("[!] 系统 Chrome 未找到,fallback 到 playwright 默认 chromium")

        self._context = pw.chromium.launch_persistent_context(**launch_kwargs)
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.timeout_sec * 1000)

    def login(self) -> bool:
        self._ensure_browser()
        self._page.goto(self.PLATFORM_URL)
        print(f"[*] 请在浏览器中手动登录 Kimi。登录完成后,按 Enter 继续...")
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
            if "kimi.moonshot.cn" not in self._page.url:
                self._page.goto(self.PLATFORM_URL)
                time.sleep(2)

            # Kimi 用 contenteditable div
            input_box = self._page.locator(self.QUERY_INPUT_SELECTOR).first
            input_box.wait_for(state="visible", timeout=10000)
            input_box.fill("")
            input_box.fill(prompt)
            time.sleep(0.5)

            # 找发送按钮(可能图标按钮,fallback 用 Enter)
            try:
                self._page.locator(self.SUBMIT_BUTTON_SELECTOR).first.click(timeout=2000)
            except Exception:
                input_box.press("Enter")
            time.sleep(1)

            # 等回答
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

            # 抓引用源
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
                shot_path = screenshot_dir / f"kimi_{ts}.png"
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

    crawler = KimiCrawler(headless=False)
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
