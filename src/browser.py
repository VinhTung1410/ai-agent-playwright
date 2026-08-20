import logging
import config
from playwright.sync_api import sync_playwright


class PlaywrightBrowser:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headless = config.HEADLESS
        self.timeout = config.TIMEOUT
        self.default_url = config.BASE_URL

        self._playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def open_browser(self):
        """Khởi tạo Chromium Browser"""
        self.logger.info("Đang khởi tạo Chromium Browser")
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(
            headless=self.headless
        )
        self.context = self.browser.new_context()
        self.context.set_default_timeout(self.timeout)
        self.logger.info("Đã mở Chromium Browser")

    def open_page(self, url: str = None):
        """1. page.goto()"""
        if not self.context:
            raise Exception("Browser chưa được mở!")

        target_url = url if url else self.default_url
        self.page = self.context.new_page()
        self.page.goto(target_url)
        title = self.page.title()
        print(f"-> 1. Đã truy cập: {target_url}")
        print(f"-> Title: {title}")
        self.logger.info("Đã truy cập %s | title=%s", target_url, title)
        return self.page

    def get_title(self):
        """Lấy title của trang hiện tại."""
        if not self.page:
            raise Exception("Chưa có Trang nào được mở để lấy title!")

        title = self.page.title()
        self.logger.info("Lấy title trang: %s", title)
        return title

    def take_screenshot(self, filepath: str = "screenshot.png"):
        """2. page.screenshot()"""
        if not self.page:
            raise Exception("Chưa có Trang nào được mở để chụp hình!")

        # full_page=True giúp chụp toàn bộ chiều dài trang web
        self.page.screenshot(path=filepath, full_page=True)
        print(f"-> 2. Đã chụp màn hình và lưu tại: {filepath}")
        self.logger.info("Đã chụp screenshot: %s", filepath)

    def close(self):
        """3. browser.close()"""
        self.logger.info("Đang đóng browser")
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()

        print("-> 3. Đã đóng Browser")
        self.logger.info("Đã đóng browser")