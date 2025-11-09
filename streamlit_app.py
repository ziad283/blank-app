import streamlit as st
import pandas as pd
import requests
from lxml import html
from io import StringIO

# ------------------------
# 🔧 Function to fetch Ogimet data
# ------------------------
def fetch_table(station_id, year, month):
    """Fetch Ogimet monthly data for a given station/year/month."""
    url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"
    
    # More complete headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
        response.encoding = "utf-8"  # ensure proper text decoding
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

    if response.status_code != 200:
        st.error(f"Failed to fetch data (HTTP {response.status_code})")
        return None

    try:
        tree = html.fromstring(response.text)
    except Exception as e:
        st.error(f"Error parsing HTML: {e}")
        return None

    # Try to find tables using pandas read_html first (more robust)
    try:
        tables = pd.read_html(StringIO(response.text))
        
        # Look for the table with actual data (should have multiple rows)
        for table in tables:
            # Check if this table has 'Date' column and sufficient rows (actual data)
            has_date = 'Date' in table.columns or any('Date' in str(col) for col in table.columns)
            has_data = table.shape[0] > 5  # At least 5 rows of data
            
            if has_date and has_data:
                # Clean the dataframe
                df = table.copy()
                
                # Handle multi-level columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    # Flatten multi-level columns
                    df.columns = [' '.join(col).strip() if col[1] else col[0] for col in df.columns.values]
                
                # Remove any completely empty rows
                df = df.dropna(how='all')
                
                # Reset index
                df = df.reset_index(drop=True)
                
                # Convert numeric columns (suppress FutureWarning)
                for col in df.columns:
                    try:
                        # Try to convert to numeric, keep original if fails
                        converted = pd.to_numeric(df[col], errors='coerce')
                        # Only replace if we got some valid numbers
                        if converted.notna().sum() > 0:
                            df[col] = converted
                    except Exception:
                        pass
                
                return df
    except Exception as e:
        st.warning(f"pandas read_html failed: {e}. Trying manual parsing...")

    # Fallback: Manual XPath parsing
    tables = tree.xpath('//table')
    target_table = None
    
    for tbl in tables:
        text_content = tbl.text_content()
        if "Date" in text_content or "date" in text_content.lower():
            target_table = tbl
            break

    if target_table is None:
        st.error("Could not find data table in the response.")
        return None

    # Extract all rows
    rows = target_table.xpath(".//tr")
    
    if len(rows) < 2:
        st.error("Table found but has insufficient rows.")
        return None

    # Find header row (look for row with 'th' elements or first row with 'Date')
    headers = None
    data_start_idx = 0
    
    for idx, row in enumerate(rows):
        ths = row.xpath(".//th")
        if ths:
            headers = [th.text_content().strip() for th in ths]
            data_start_idx = idx + 1
            break
        else:
            # Check if this row contains 'Date' in td elements
            tds = row.xpath(".//td")
            if tds and any('Date' in td.text_content() for td in tds):
                headers = [td.text_content().strip() for td in tds]
                data_start_idx = idx + 1
                break

    if headers is None:
        st.error("Could not identify header row.")
        return None

    # Extract data rows
    data = []
    for row in rows[data_start_idx:]:
        cells = row.xpath(".//td")
        if cells:
            cell_values = [td.text_content().strip() for td in cells]
            if len(cell_values) == len(headers):
                data.append(cell_values)

    if not data:
        st.error("No data rows found after header.")
        return None

    df = pd.DataFrame(data, columns=headers)

    # Clean and convert numeric columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except Exception:
            pass

    return df


# ------------------------
# 🌦️ Streamlit UI
# ------------------------
st.set_page_config(page_title="Ogimet Data Visualizer", layout="wide")

st.title("🌦️ Ogimet Meteorological Data Viewer")
st.markdown("Visualize daily meteorological data directly from [Ogimet](https://www.ogimet.com/).")
st.info("💡 **Tip:** Data availability varies by station and date. Try recent months (last 2-3 months) for best results.")

# Initialize session state for data persistence
if 'df' not in st.session_state:
    st.session_state.df = None
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = None

# Sidebar inputs
st.sidebar.header("Select Parameters")
station_id = st.sidebar.text_input("Station ID (WMO code)", "60390")  # Example: Algiers
year = st.sidebar.number_input("Year", 2000, 2025, 2024)
month = st.sidebar.number_input("Month", 1, 12, 10)  # Default to October (recent month with data)

if st.sidebar.button("Fetch Data"):
    st.info("Fetching data from Ogimet...")
    df = fetch_table(station_id, year, month)

    if df is None or df.empty:
        st.warning("⚠️ No data found. Try another month or station.")
        st.session_state.df = None
        st.session_state.last_fetch = None
    else:
        st.session_state.df = df
        st.session_state.last_fetch = f"Station {station_id} ({year}-{month:02d})"
        st.success(f"✅ Data successfully loaded for {st.session_state.last_fetch}")

# Display data if available
if st.session_state.df is not None:
    st.subheader(f"📋 Data for {st.session_state.last_fetch}")
    st.dataframe(st.session_state.df, use_container_width=True)

    # Visualization section
    numeric_cols = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if numeric_cols:
        st.subheader("📊 Quick Visualization")
        selected_col = st.selectbox("Select a variable to plot:", numeric_cols)
        if selected_col:
            st.line_chart(st.session_state.df[selected_col])
    else:
        st.info("No numeric columns found for plotting.")
    
    # Download option
    csv = st.session_state.df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"ogimet_{station_id}_{year}_{month:02d}.csv",
        mime="text/csv"
    )
else:
    st.info("👈 Enter parameters and click **Fetch Data** to start.")


# ------------------------
# 🧾 Footer
# ------------------------
st.markdown("---")
st.caption("Developed by Ziad & powered by Streamlit + Ogimet data.")
