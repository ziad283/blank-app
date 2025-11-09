"""Final test with improved headers."""
import pandas as pd
import requests
from lxml import html
from io import StringIO

def fetch_table(station_id, year, month):
    """Fetch Ogimet monthly data for a given station/year/month."""
    url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
        response.encoding = "utf-8"
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch data (HTTP {response.status_code})")
        return None

    print(f"✓ Response received: {len(response.text)} chars")

    # Try pandas read_html first
    try:
        tables = pd.read_html(StringIO(response.text))
        print(f"✓ Found {len(tables)} tables using pandas")
        
        for i, table in enumerate(tables):
            if 'Date' in table.columns or any('Date' in str(col) for col in table.columns):
                print(f"✓ Found data table at index {i}")
                df = table.copy()
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                
                # Convert numeric columns
                for col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except Exception:
                        pass
                
                return df
    except Exception as e:
        print(f"pandas read_html failed: {e}")

    # Fallback: Manual parsing
    print("Trying manual XPath parsing...")
    try:
        tree = html.fromstring(response.text)
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

    tables = tree.xpath('//table')
    print(f"Found {len(tables)} tables via XPath")
    
    target_table = None
    for i, tbl in enumerate(tables):
        text_content = tbl.text_content()
        if "Date" in text_content:
            print(f"✓ Table {i} contains 'Date'")
            target_table = tbl
            break

    if target_table is None:
        print("✗ No table with 'Date' found")
        return None

    # Extract rows
    rows = target_table.xpath(".//tr")
    print(f"Table has {len(rows)} rows")
    
    if len(rows) < 2:
        print("✗ Insufficient rows")
        return None

    # Find header row
    headers = None
    data_start_idx = 0
    
    for idx, row in enumerate(rows):
        ths = row.xpath(".//th")
        if ths:
            headers = [th.text_content().strip() for th in ths]
            data_start_idx = idx + 1
            print(f"✓ Found header row at index {idx}: {headers[:5]}...")
            break
        else:
            tds = row.xpath(".//td")
            if tds and any('Date' in td.text_content() for td in tds):
                headers = [td.text_content().strip() for td in tds]
                data_start_idx = idx + 1
                print(f"✓ Found header row (td) at index {idx}: {headers[:5]}...")
                break

    if headers is None:
        print("✗ Could not identify header row")
        return None

    # Extract data
    data = []
    for row in rows[data_start_idx:]:
        cells = row.xpath(".//td")
        if cells:
            cell_values = [td.text_content().strip() for td in cells]
            if len(cell_values) == len(headers):
                data.append(cell_values)

    print(f"✓ Extracted {len(data)} data rows")

    if not data:
        print("✗ No data rows found")
        return None

    df = pd.DataFrame(data, columns=headers)

    # Convert numeric columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except Exception:
            pass

    return df


if __name__ == "__main__":
    print("Testing Ogimet data fetch with improved headers...")
    print("=" * 60)
    
    df = fetch_table("60390", 2024, 1)
    
    if df is not None:
        print("\n" + "=" * 60)
        print("✓✓✓ SUCCESS! Data fetched successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nFirst 5 rows:")
        print(df.head())
    else:
        print("\n" + "=" * 60)
        print("✗✗✗ FAILED: No data found")
