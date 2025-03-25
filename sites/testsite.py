from playwright.sync_api import sync_playwright
import os
import sys

# Load config from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def click_if_exists(page, selector, role=None, name=None):
    try:
        if role and name:
            page.wait_for_selector(f'role={role}[name="{name}"]', timeout=10000)
            page.get_by_role(role, name=name).click()
        else:
            page.wait_for_selector(selector, timeout=10000)
            page.locator(selector).click()
        return True
    except Exception:
        return False


def fill_input_range(page, min_selector, max_selector, min_val, max_val, apply_selector=None):
    page.wait_for_selector(min_selector, state="visible", timeout=10000)
    page.wait_for_selector(max_selector, state="visible", timeout=10000)

    page.locator(min_selector).fill(str(min_val))
    page.locator(min_selector).press("Enter")
    page.locator(max_selector).fill(str(max_val))
    page.locator(max_selector).press("Enter")

    if apply_selector:
        if not click_if_exists(page, apply_selector):
            page.locator(max_selector).press("Enter")


def apply_filters(page):
    print("[INFO] Manually applying filters...")

    # Price filter
    if click_if_exists(page, 'role=button', role="button", name="Montant loyer "):
        print("[INFO] Opened price filter dropdown")
        fill_input_range(page, "#min-price-range", "#max-price-range", 800, 1500)
        print(f"[INFO] Applied price filter")

    # Room filter
    if click_if_exists(page, 'role=button', role="button", name="Pièces "):
        print("[INFO] Opened rooms filter dropdown")
        fill_input_range(page, "#min-room-range", "#max-room-range", 2, 17, ".dropdown-room button:has-text('Appliquer')")
        print(f"[INFO] Applied rooms filter")

    # Final apply buttons
    if not click_if_exists(page, 'button:has-text("Filtrer")'):
        click_if_exists(page, "#btn-search")

    page.wait_for_timeout(2000)
    print("[INFO] Filters applied and UI updated")


def open_browser_with_criteria():
    base_url = f"https://www.immobilier.ch/fr/carte/louer/appartement-maison/{config.LIEU.lower()}/page-1?t=rent&c=1;2&p=s40&nb=false"
    print(f"[INFO] Opening browser with URL: {base_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        context.clear_cookies()
        print("[INFO] Cleared cookies")

        page = context.new_page()

        try:
            page.goto(base_url, timeout=60000)
            print(f"[INFO] Navigated to URL: {page.url}")
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            browser.close()
            return

        click_if_exists(page, 'role=button', role="button", name="Tout autoriser")

        try:
            apply_filters(page)
        except Exception as e:
            print(f"[ERROR] Filter application failed: {e}")
            page.screenshot(path="debug_filter_screenshot.png")
            with open("debug_filter_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())

        try:
            page.wait_for_selector("#map-search-results .filter-item", timeout=60000)
            print("[INFO] Listings loaded")
            page.wait_for_timeout(20000)

            try:
                page.wait_for_selector(".loading-spinner", state="detached", timeout=15000)
                print("[INFO] Spinner disappeared")
            except Exception:
                print("[INFO] Spinner not found or already gone")

            items = page.query_selector_all("#map-search-results .filter-item a:not([style*='display: none'])")
            print(f"[INFO] Found {len(items)} visible listings")
        except Exception as e:
            print(f"[ERROR] Failed to load listings: {e}")
            page.screenshot(path="debug_screenshot.png")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())

        input("[INFO] Press Enter to close the browser...")
        browser.close()


if __name__ == "__main__":
    open_browser_with_criteria()
