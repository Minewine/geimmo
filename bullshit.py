from playwright.async_api import async_playwright
import re


async def run():
    listings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.immobilier.ch/fr/carte/louer/appartement-maison/geneve/page-1?t=rent&c=1;2&p=s40&nb=false&gr=1")

        # Accept cookies if present
        try:
            await page.get_by_role("button", name="Tout autoriser").click(timeout=3000)
        except:
            pass

        print("🔧 Applying filters in UI...")

        # Price filter
        await page.get_by_role("button", name=re.compile("Montant loyer")).click()
        await page.locator("#min-price-range").fill("800")
        await page.locator("#max-price-range").fill("1400")

        # Room filter
        await page.get_by_role("button", name=re.compile("Pièces")).click()
        await page.locator("#min-room-range").fill("1.5")
        await page.locator("#max-room-range").fill("4")

        # Sort by most recent
        await page.get_by_text("Offres TOP").nth(1).click()
        await page.get_by_text(re.compile(r"^Biens les \+ récents$")).click()

        # Wait for filtered content to render
        await page.wait_for_timeout(5000)

        # Save page for debugging
        with open("/tmp/immobilier_filtered.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        print("✅ Filters applied and page saved to /tmp/immobilier_filtered.html")

        # Extract data
        cards = await page.locator("#map-search-results .filter-item").all()
        print(f"📦 Found {len(cards)} filtered listings:\n")

        for i, card in enumerate(cards):
            try:
                title = await card.locator("p.object-type").inner_text()
                price = await card.locator("strong.title").inner_text()
                address = await card.locator("p").nth(1).inner_text()
                link = await card.locator("a").first.get_attribute("href")
                url = "https://www.immobilier.ch" + link if link else "N/A"

                listings.append({
                    "title": title.strip(),
                    "price": price.strip(),
                    "address": address.strip(),
                    "url": url,
                    "source": "immobilier.ch"
                })

                print(f"{i+1:02d}. 🏠 {title}\n   💵 {price}\n   📍 {address}\n   🔗 {url}\n")

            except Exception as e:
                print(f"⚠️  Skipped listing {i+1:02d} due to error: {e}\n")

        await browser.close()

    return listings


# Example usage
if __name__ == "__main__":
    import asyncio, json
    listings = asyncio.run(run())

    with open("/tmp/immobilier_results.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
