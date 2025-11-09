"""Refined test to find the correct data table."""
import pandas as pd
import requests
from io import StringIO

station_id = "60390"
year = 2024
month = 1

url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

session = requests.Session()
response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
response.encoding = "utf-8"

print(f"Response: {len(response.text)} chars\n")

tables = pd.read_html(StringIO(response.text))
print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables):
    print(f"Table {i}:")
    print(f"  Shape: {table.shape}")
    print(f"  Columns: {table.columns.tolist()[:5]}")
    
    # Check if this looks like actual data (has numeric values and dates)
    if table.shape[0] > 5:  # At least 5 rows
        print(f"  First column values: {table.iloc[:3, 0].tolist()}")
        print(f"  → This looks like the data table!")
        print(f"\nFull table preview:")
        print(table.head(10))
        break
    print()
