"""Test script to verify Ogimet data fetching works correctly."""
import pandas as pd
import requests
from lxml import html
from io import StringIO

def fetch_table(station_id, year, month):
    """Fetch Ogimet monthly data for a given station/year/month."""
    url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print(f"Fetching URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = "utf-8"
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch data (HTTP {response.status_code})")
        return None

    print(f"Response received, status: {response.status_code}")
    
    # Try pandas read_html first
    try:
        tables = pd.read_html(StringIO(response.text))
        print(f"Found {len(tables)} tables using pandas")
        
        for i, table in enumerate(tables):
            print(f"\nTable {i} columns: {table.columns.tolist()}")
            if 'Date' in table.columns or any('Date' in str(col) for col in table.columns):
                print(f"✓ Found data table at index {i}")
                print(f"Table shape: {table.shape}")
                print(f"First few rows:\n{table.head()}")
                return table
    except Exception as e:
        print(f"pandas read_html failed: {e}")
        return None

    print("No table with 'Date' column found")
    return None


if __name__ == "__main__":
    # Test with Algiers station
    print("Testing Ogimet data fetch...")
    print("=" * 60)
    
    df = fetch_table("60390", 2024, 1)
    
    if df is not None:
        print("\n" + "=" * 60)
        print("✓ SUCCESS: Data fetched successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
    else:
        print("\n" + "=" * 60)
        print("✗ FAILED: No data found")
