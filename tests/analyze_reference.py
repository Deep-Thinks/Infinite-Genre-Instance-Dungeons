"""
分析参考网站的副本工作流设计
"""

import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "reference_analysis")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def analyze_reference():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        print("访问参考网站...")
        page.goto("https://wbmnbwl.vercel.app/creator", timeout=30000)
        page.wait_for_timeout(3000)

        # 截图1: 主页面
        print("1. 主页面...")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_main.png"))

        # 截图2: 点击预览
        print("2. 点击预览...")
        try:
            preview_btn = page.locator('button:has-text("预览"), button:has-text("▶")')
            if preview_btn.count() > 0:
                preview_btn.first.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_preview.png"))
        except Exception as e:
            print(f"  跳过: {e}")

        # 截图3: 点击回忆
        print("3. 点击回忆...")
        try:
            recall_btn = page.locator('button:has-text("回忆")')
            if recall_btn.count() > 0:
                recall_btn.first.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_recall.png"))
                # 关闭面板
                close_btn = page.locator('button:has-text("×"), button[aria-label="close"]')
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
        except Exception as e:
            print(f"  跳过: {e}")

        # 截图4: 点击存档
        print("4. 点击存档...")
        try:
            save_btn = page.locator('button:has-text("存档")')
            if save_btn.count() > 0:
                save_btn.first.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_save.png"))
        except Exception as e:
            print(f"  跳过: {e}")

        # 截图5: 点击设置
        print("5. 点击设置...")
        try:
            settings_btn = page.locator('button:has-text("设置")')
            if settings_btn.count() > 0:
                settings_btn.first.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_settings.png"))
        except Exception as e:
            print(f"  跳过: {e}")

        # 截图6: 回到主页面查看场景列表
        print("6. 场景列表...")
        try:
            # 关闭所有面板
            close_btns = page.locator('button:has-text("×")')
            for i in range(close_btns.count()):
                try:
                    close_btns.nth(i).click()
                    page.wait_for_timeout(300)
                except:
                    pass
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_scene_list.png"))
        except Exception as e:
            print(f"  跳过: {e}")

        browser.close()
        print(f"\n截图已保存到: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    analyze_reference()
