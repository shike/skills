"""
豆包 (Doubao) 爬虫 - GEO 雷达 v2.0 核心模块

通过 Playwright 模拟用户在浏览器里打开豆包,输入 prompt,等回答,抓文本+截图+引用源。
不需要 API key,但需要用户先在浏览器登录豆包(cookie 持久化到 playwright profile)。

用法:
    from doubao import DoubaoCrawler
    crawler = DoubaoCrawler(headless=False)  # 第一次用建议 headless=False 手动登录
    result = crawler.ask("推荐 2025 平价奶茶品牌")
    print(result.text, result.citations)

环境要求:
    pip install playwright
    playwright install chromium
    首次运行: 浏览器会打开,用户手动登录豆包,cookie 持久化到 ~/.geo-radar-cn/browser-profile/

注意:
    - 豆包反爬: 每次问询间隔 ≥ 3 秒,避免触发限流
    - 单次问询超时: 60 秒
    - 登录态: 用 playwright persistent context(cookie 自动保留 30 天)
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CrawlResult:
    """单次问询的结果"""
    platform: str = "doubao"
    prompt: str = ""
    text: str = ""  # LLM 的回答文本
    citations: list = field(default_factory=list)  # 引用的网页/源
    screenshot_path: Optional[str] = None  # 截图路径(用于审计)
    timestamp: float = 0.0
    duration_sec: float = 0.0
    success: bool = False
    error: Optional[str] = None


class DoubaoCrawler:
    """豆包爬虫 — playwright 模拟用户问询"""

    PLATFORM_URL = "https://www.doubao.com/chat/"
    QUERY_INPUT_SELECTOR = 'textarea[data-testid="chat-input"]'  # 豆包输入框 selector
    SUBMIT_BUTTON_SELECTOR = 'button[data-testid="send-button"]'  # 发送按钮
    RESPONSE_CONTAINER_SELECTOR = 'div[data-message-role="assistant"]'  # 回答容器
    CITATION_LINK_SELECTOR = 'a[data-testid="citation-link"]'  # 引用源链接

    def __init__(self, headless: bool = False, profile_dir: Optional[Path] = None,
                 interval_sec: float = 3.0, timeout_sec: float = 60.0):
        """
        Args:
            headless: 是否无头模式。首次使用建议 False 以便手动登录
            profile_dir: 浏览器 profile 目录(cookie 持久化)
            interval_sec: 每次问询之间的间隔(避免反爬)
            timeout_sec: 单次问询超时时间
        """
        self.headless = headless
        self.profile_dir = profile_dir or Path.home() / ".geo-radar-cn" / "browser-profile"
        self.interval_sec = interval_sec
        self.timeout_sec = timeout_sec
        self._browser = None
        self._context = None
        self._page = None

    def _ensure_browser(self):
        """懒加载浏览器(persistent context,cookie 自动保留)"""
        if self._browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "playwright 未安装。请运行: pip install playwright && playwright install chromium"
            )

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        pw = sync_playwright().start()
        self._pw = pw  # 保留以备 __exit__

        # 用 persistent context,cookie 自动持久化
        self._context = pw.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        # launch_persistent_context 直接返回 context,没有 browser
        # 打开一个 page
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.timeout_sec * 1000)

    def login(self) -> bool:
        """打开豆包登录页,等用户手动登录,等登录态稳定后返回

        首次使用必须调用,后续可跳过(cookie 已持久化)
        """
        self._ensure_browser()
        self._page.goto(self.PLATFORM_URL)
        # 等用户登录(检测 URL 变化 或 检测登录后元素)
        print(f"[*] 请在浏览器中手动登录豆包。登录完成后,按 Enter 继续...")
        input()
        # 简单检查: 刷新页面看是否还在登录页
        self._page.reload()
        time.sleep(2)
        if "login" in self._page.url.lower():
            print("[!] 仍在登录页,请重试")
            return False
        print("[+] 登录成功,cookie 已保存到:", self.profile_dir)
        return True

    def ask(self, prompt: str, screenshot: bool = True) -> CrawlResult:
        """问豆包一个 prompt,返回 CrawlResult

        Args:
            prompt: 要问的问题(中文)
            screenshot: 是否截图(默认 True,用于审计)

        Returns:
            CrawlResult: 包含 text / citations / screenshot_path / duration
        """
        self._ensure_browser()
        result = CrawlResult(prompt=prompt, timestamp=time.time())
        start = time.time()

        try:
            # 1. 打开豆包 chat 页(如果还在登录页则提示)
            if "doubao.com/chat" not in self._page.url:
                self._page.goto(self.PLATFORM_URL)
                time.sleep(2)

            # 2. 输入 prompt
            input_box = self._page.locator(self.QUERY_INPUT_SELECTOR).first
            input_box.wait_for(state="visible", timeout=10000)
            input_box.fill("")  # 清空
            input_box.fill(prompt)
            time.sleep(0.5)

            # 3. 点击发送
            self._page.locator(self.SUBMIT_BUTTON_SELECTOR).first.click()
            time.sleep(1)

            # 4. 等回答(轮询检测回答容器出现 + 文本稳定)
            response = self._page.locator(self.RESPONSE_CONTAINER_SELECTOR).last
            response.wait_for(state="visible", timeout=self.timeout_sec * 1000)
            # 等回答完成(文本长度稳定 2 秒)
            prev_len = -1
            stable_count = 0
            for _ in range(30):  # 最多等 60 秒
                time.sleep(2)
                cur_text = response.inner_text()
                if len(cur_text) == prev_len and len(cur_text) > 10:
                    stable_count += 1
                    if stable_count >= 2:  # 稳定 2 次
                        break
                else:
                    stable_count = 0
                prev_len = len(cur_text)

            result.text = response.inner_text()

            # 5. 抓引用源
            citations = self._page.locator(self.CITATION_LINK_SELECTOR).all()
            result.citations = [
                {"title": c.inner_text().strip(), "url": c.get_attribute("href")}
                for c in citations if c.get_attribute("href")
            ]

            # 6. 截图(可选)
            if screenshot:
                screenshot_dir = self.profile_dir / "screenshots"
                screenshot_dir.mkdir(exist_ok=True)
                ts = int(time.time() * 1000)
                shot_path = screenshot_dir / f"doubao_{ts}.png"
                self._page.screenshot(path=str(shot_path), full_page=True)
                result.screenshot_path = str(shot_path)

            result.success = True

        except Exception as e:
            result.error = str(e)
            result.success = False

        finally:
            result.duration_sec = time.time() - start
            # 反爬: 间隔
            time.sleep(self.interval_sec)

        return result

    def close(self):
        """关闭浏览器"""
        if self._context is not None:
            self._context.close()
        if hasattr(self, "_pw") and self._pw is not None:
            self._pw.stop()
        self._context = None
        self._page = None
        self._pw = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# === CLI 测试入口 ===
if __name__ == "__main__":
    import sys

    crawler = DoubaoCrawler(headless=False)
    try:
        # 首次用: 登录
        crawler.login()

        # 测试
        prompt = sys.argv[1] if len(sys.argv) > 1 else "推荐 2025 平价奶茶品牌"
        result = crawler.ask(prompt)
        print(f"\n[+] prompt: {result.prompt}")
        print(f"[+] duration: {result.duration_sec:.1f}s")
        print(f"[+] success: {result.success}")
        print(f"[+] text: {result.text[:300]}{'...' if len(result.text) > 300 else ''}")
        print(f"[+] citations ({len(result.citations)}):")
        for c in result.citations[:5]:
            print(f"    - {c['title']}: {c['url']}")
        if result.screenshot_path:
            print(f"[+] screenshot: {result.screenshot_path}")

    finally:
        crawler.close()
