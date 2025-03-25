import sys
import os
import csv
import asyncio
from datetime import datetime
import webbrowser
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sites import immoscout24ch, immobilierch

def open_links_in_browser(listings, max_tabs=10, delay=0.5):
    print("\n🌐 Opening listings in Chrome tabs...\n")
    opened = 0
    for listing in listings:
        url = listing.get("url", "")
        if url.startswith("http"):
            print(f"🔗 {url}")
            webbrowser.open_new_tab(url)
            opened += 1
            time.sleep(delay)
            if max_tabs and opened >= max_tabs:
                break
    print(f"\n✅ Opened {opened} listings in Chrome.")

def normalize_entry(entry, source=None):
    return {
        "title": entry.get("title", "N/A"),
        "price": entry.get("price", "N/A"),
        "address": entry.get("address", "N/A"),
        "url": entry.get("url", "N/A"),
        "source": entry.get("source", source or "N/A")
    }

async def main():
    scout_listings = await immoscout24ch.run()
    immobilier_listings = await immobilierch.run()

    all_listings = [
        normalize_entry(l, source="immoscout24.ch") for l in scout_listings
    ] + [
        normalize_entry(l, source="immobilier.ch") for l in immobilier_listings
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"listings_{timestamp}.csv")

    fieldnames = ["title", "price", "address", "url", "source"]
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_listings)

    print(f"✅ Saved {len(all_listings)} listings to {filename}")

    # Open listings in browser
    open_links_in_browser(all_listings, max_tabs=10)

if __name__ == "__main__":
    asyncio.run(main())
