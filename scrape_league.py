import sys
import os
from bs4 import BeautifulSoup
import requests
import random
import hashlib
import subprocess

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

HEADERS = {
    'User-Agent': random.choice(USER_AGENTS)
}

def format_league_name(str):
    result = str.replace("-"," ")
    result = result.capitalize()
    return result

def url_to_filename(url):
    # Creates a hashname to store the html file into the cache folder
    h = hashlib.md5(url.encode()).hexdigest()
    return f"cache/{h}.html"

def fetch_or_load_html(url):
    # Uses the cache html if it exists, otherwise it downloads it
    os.makedirs("cache", exist_ok=True)
    file_path = url_to_filename(url)

    if os.path.exists(file_path):
        print(f"📂 Using cache: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"🌐 Downloading: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return response.text
        else:
            print("❌ Error downloading the page.")
            return None


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 4:
        print("Usage: python3 scrape_league.py <url> <league_id> <clubs_index> <players_index>")
        sys.exit(1)

    league_url = args[0]
    league_id = args[1]
    clubs_index = int(args[2])
    players_index = args[3]

    league_name = format_league_name(league_url.split('/')[3])

    html = fetch_or_load_html(league_url)
    if not html:
        sys.exit(1)
    soup = BeautifulSoup(html, 'html.parser')
    
    table = soup.find('table', class_='items')

    if table is None:
        print("Couldn't find teams table")
        sys.exit(1)

    for row in table.select("tbody > tr"):
        a_tag = row.find("a", href=lambda x: x and "/kader/verein/" in x)
        
        if not a_tag:
            continue
        
        relative_url = a_tag.get("href")
        team_url = f"https://www.transfermarkt.es{relative_url}/plus/1"
        
        result = subprocess.run(["python3", "scrape_team.py", f"{team_url}", f"{league_id}", f"{clubs_index}", f"{players_index}"], capture_output=True, text=True)
        print(result.stdout)

        try:
            players_index = int(result.stdout.strip().splitlines()[-1])
        except Exception:
            print("Couldn't read players index") 
            
        clubs_index += 1
    print(players_index)
    print(clubs_index)
    