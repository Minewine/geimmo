import sys
import os
import re
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


async def run():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.immoscout24.ch/fr", timeout=60000)

        # Accept cookies
        try:
            await page.get_by_role("button", name="I Accept").click(timeout=3000)
        except:
            print("⚠️ No cookie banner found")

        print("🔧 Applying filters on immoscout24...")
        await page.locator("[data-test=\"extendFiltersButton\"]").click()

        # Location input
        await page.locator("[data-test=\"searchBarModal\"] div").filter(
            has_text=re.compile(r"^Localit\u00e9, NPA, canton, r\u00e9gion$")).click()
        await page.get_by_role("textbox", name="Localité, NPA, canton, région").fill(config.LIEU)
        await page.get_by_text("GenèveLieu").click()

        # Price filters
        await page.get_by_label("CHF de indiff.500 CHF600").select_option(str(config.MIN_PRICE))
        await page.locator("[data-test=\"searchBarModal\"]").get_by_label("Prix à indiff.500 CHF600").select_option(str(config.MAX_PRICE))
        await page.locator("span").filter(has_text="Seulement annonces avec prix").nth(1).click()

        # Room filters
        await page.locator("[data-test=\"searchBarModal\"]").get_by_label("Pièces de indiff.11.522.533.").select_option(str(config.MIN_PIECES))
        await page.get_by_label("Pièces à indiff.11.522.533.").select_option(str(config.MAX_PIECES))

        # Submit filters
        await page.locator("[data-test=\"searchBarModal\"]").get_by_role("button").nth(3).click()

        # Click "objets" to see listings
        await page.get_by_role("button", name="objets").click()

        await page.wait_for_timeout(5000)
        html = await page.content()
        Path("/tmp/immoscout_filtered.html").write_text(html, encoding="utf-8")
        print("✅ Page saved to /tmp/immoscout_filtered.html")

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("[data-test='result-list-item']")
        print(f"📦 Found {len(cards)} listings\n")

        for i, card in enumerate(cards, start=1):
            try:
                rooms_el = card.select_one("strong")
                surface_el = card.select_one("strong[title='surface habitable']")
                price_el = card.select_one(".HgListingRoomsLivingSpacePrice_price_u9Vee")
                address_el = card.select_one(".HgListingCard_address_JGiFv")
                url_el = card.select_one("a")

                rooms = rooms_el.text.strip() if rooms_el else "N/A"
                surface = surface_el.text.strip() if surface_el else "N/A"
                price = price_el.text.strip() if price_el else "N/A"
                address = address_el.text.strip() if address_el else "N/A"

                href = url_el["href"] if url_el and url_el.has_attr("href") else "#"
                full_url = f"https://www.immoscout24.ch{href}" if href.startswith("/") else href

                title = f"{rooms}, {surface}"

                print(f"{i:02d}. 🏠 {title}\n   💵 {price}\n   📍 {address}\n   🔗 {full_url}\n")

                results.append({
                    "title": title,
                    "price": price,
                    "address": address,
                    "url": full_url
                })

            except Exception as e:
                print(f"❌ Error parsing listing {i}: {e}")


        await context.close()
        await browser.close()
        return results

if __name__ == "__main__":
    listings = asyncio.run(run())
    print(listings)