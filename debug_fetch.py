"""Debug script to see what Ogimet returns."""
import requests
from lxml import html

station_id = "60390"
year = 2024
month = 1

url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print(f"Fetching: {url}\n")

response = requests.get(url, headers=headers, timeout=20)
response.encoding = "utf-8"

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

# Parse with lxml
tree = html.fromstring(response.text)
tables = tree.xpath('//table')

print(f"\nFound {len(tables)} tables")

for i, table in enumerate(tables):
    text = table.text_content()[:200]  # First 200 chars
    print(f"\nTable {i}: {text}...")
    
    # Check for Date
    if "Date" in table.text_content():
        print(f"  → Contains 'Date'")
        
        # Get rows
        rows = table.xpath(".//tr")
        print(f"  → Has {len(rows)} rows")
        
        if len(rows) > 0:
            # Check first few rows
            for j, row in enumerate(rows[:5]):
                cells = row.xpath(".//th | .//td")
                cell_text = [c.text_content().strip()[:20] for c in cells]
                print(f"    Row {j}: {cell_text}")
