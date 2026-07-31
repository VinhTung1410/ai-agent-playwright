import logging
import os
from datetime import datetime

import config
from browser import PlaywrightBrowser

print("=== BẮT ĐẦU CHẠY SCRIPT ===")


def configure_logging():
    os.makedirs(config.LOG_PATH, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(config.LOG_PATH, config.LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
    )


def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Bắt đầu chạy script")
    print("1. Dang khoi tao PlaywrightBrowser...")
    app = PlaywrightBrowser()

    try:
        print("2. Dang mo trinh duyet Edge...")
        app.open_browser()

        print("3. Dang truy cap trang web...")
        app.open_page()
        title = app.get_title()
        print(f"-> Title trang: {title}")

        print("4. Dang chup hinh...")
        os.makedirs(config.SCREENSHOT_PATH, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(
            config.SCREENSHOT_PATH, f"facebook_screenshot_{timestamp}.png"
        )
        app.take_screenshot(screenshot_path)

    except Exception as e:
        logger.exception("Script gặp lỗi")
        print(f"XẢY RA LỖI: {e}")

    finally:
        print("5. Dang dong trinh duyet...")
        app.close()
        logger.info("Kết thúc script")


if __name__ == "__main__":
    main()