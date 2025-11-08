"""Debug script with better request handling."""
import requests

station_id = "60390"
year = 2024
month = 1

url = f"https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={station_id}&ndays=31&ano={year}&mes={month:02d}&day=31&hora=00&ord=REV&Send=Send"

# More complete headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

print(f"Fetching: {url}\n")

session = requests.Session()
response = session.get(url, headers=headers, timeout=20, allow_redirects=True)

print(f"Status: {response.status_code}")
print(f"Final URL: {response.url}")
print(f"Content length: {len(response.content)}")
print(f"Content type: {response.headers.get('content-type', 'unknown')}")
print(f"\nFirst 500 chars of response:")
print(response.text[:500])
