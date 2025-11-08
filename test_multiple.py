"""Test multiple dates to find working data."""
import pandas as pd
import requests
from io import StringIO

def test_fetch(station_id, year, month):
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
    
    print(f"{station_id} {year}-{month:02d}: {len(response.text)} chars, ", end="")
    
    try:
        tables = pd.read_html(StringIO(response.text))
        print(f"{len(tables)} tables")
        
        for table in tables:
            if table.shape[0] > 5:  # Likely data table
                print(f"  → Found data table: {table.shape}")
                return table
    except Exception as e:
        print(f"Error: {e}")
    
    return None

# Test different combinations
print("Testing different dates:\n")

# Recent months
for month in [10, 9, 8]:
    df = test_fetch("60390", 2024, month)
    if df is not None:
        print(f"\n✓ SUCCESS with 2024-{month:02d}")
        print(df.head())
        break
    print()
