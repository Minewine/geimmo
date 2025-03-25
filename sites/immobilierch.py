import sys
import os
import re
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

async def run():
    listings_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        url = (
            f"https://www.immobilier.ch/fr/carte/louer/appartement-maison/"
            f"{config.LIEU.lower()}/page-1"
            f"?t=rent&c=1;2&p=s40&nb=false&gr=1"
        )
        await page.goto(url, timeout=60000)

        try:
            await page.get_by_role("button", name="Tout autoriser").click(timeout=3000)
        except:
            print("⚠️ No cookie banner found")

        print("🔧 Applying filters in UI...")

        # Set price
        await page.get_by_role("button", name=re.compile(r"Montant loyer")).click()
        await page.locator("input#min-price-range").fill(str(config.MIN_PRICE))
        await page.locator("input#max-price-range").fill(str(config.MAX_PRICE))

        # Set pieces
        await page.get_by_role("button", name=re.compile(r"Pièces")).click()
        await page.locator("input#min-room-range").fill(str(config.MIN_PIECES))
        await page.locator("input#max-room-range").fill(str(config.MAX_PIECES))

        # Turn off top offers & sort
        await page.get_by_text("Offres TOP").nth(1).click()
        await page.locator("span").filter(has_text=re.compile(r"^Biens les \+ récents$")).click()

        await page.wait_for_timeout(5000)

        content = await page.content()
        with open("/tmp/immobilier_filtered.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Filters applied and page saved to /tmp/immobilier_filtered.html")

        soup = BeautifulSoup(content, "html.parser")
        listings = soup.select("#map-search-results .filter-item")
        print(f"📦 Found {len(listings)} filtered listings:\n")

        for i, listing in enumerate(listings, start=1):
            try:
                title = listing.select_one(".filter-item-content p.object-type")
                title = title.text.strip() if title else "N/A"

                price = listing.select_one(".filter-item-content strong.title")
                price = price.text.strip() if price else "N/A"

                address_tag = listing.select_one(".filter-item-content p:nth-of-type(2)")
                address = address_tag.text.strip() if address_tag else "N/A"


                link_tag = listing.select_one("a[href]")
                href = link_tag["href"] if link_tag else "#"
                url = f"https://www.immobilier.ch{href}"

                listings_data.append({
                    "title": title,
                    "price": price,
                    "address": address,
                    "url": url,
                    "source": "immobilier.ch"
                })

            except Exception as e:
                print(f"❌ Error parsing listing {i}: {e}")

        await context.close()
        await browser.close()

    return listings_data


# Example usage
if __name__ == "__main__":
    import json
    results = asyncio.run(run())
    print(json.dumps(results, indent=2, ensure_ascii=False))
