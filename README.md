# 🏡 Geimmo

**Geimmo** is an async property listing scraper for Swiss real estate platforms.  
Built with Python + Playwright, it extracts listings, filters by your criteria, and can even open top results in Chrome tabs.

---

## 🔍 Supports

- [immobilier.ch](https://www.immobilier.ch/)
- [immoscout24.ch](https://www.immoscout24.ch/)

---

## ⚙️ Features

- ✅ Asynchronous scraping with Playwright
- 🧠 Smart filtering: location, price, room count
- 🗃 Outputs results to CSV
- 🌐 Optionally opens results in browser tabs
- ⚡ Fast & extendable architecture

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone git@github.com:Minewine/geimmo.git
cd geimmo
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
Make sure Playwright is installed:

bash
Copy
Edit
playwright install
3. Run the scraper
bash
Copy
Edit
python main.py
4. Open links in your browser (optional)
bash
Copy
Edit
python openalllinks.py
📁 Project Structure
graphql
Copy
Edit
geimmo/
├── main.py               # Main entry point
├── filters.py            # Filtering logic
├── immobilier.py         # Scraper for immobilier.ch
├── immoscout.py          # Scraper for immoscout24.ch
├── utils.py              # Shared utilities
├── openalllinks.py       # Opens links in browser tabs
├── output/               # CSV files stored here
├── README.md
└── requirements.txt
🧪 Example Output
Results saved as CSV will include:

Title	Price	Rooms	Area	URL
Cozy 2.5 Room Flat	CHF 1,950	2.5	60 m²	View
Spacious Family Home	CHF 3,200	5.5	130 m²	View
🧠 Tech Stack
Python 3.10+

Playwright (async API)

Pandas for CSV

Role-based selectors

🧔 Author
Minewine

	
