import csv
import webbrowser
import time
import webbrowser
import time

FILENAME = "listings_2025-03-25.csv"  # or your actual file

with open(FILENAME, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    urls = [row['url'] for row in reader if row['url'].startswith("http")]

# Open each URL in a new browser tab
for i, url in enumerate(urls):
    print(f"🔗 Opening: {url}")
    webbrowser.open_new_tab(url)
    time.sleep(0.5)  # slight delay to avoid browser freeze
