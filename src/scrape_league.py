import sys
import os
import time
from bs4 import BeautifulSoup
import requests
import random
import hashlib
import subprocess
import re
import uuid

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

HEADERS = {
    'User-Agent': random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}

session = requests.Session()
session.headers.update(HEADERS)
session.get("https://www.transfermarkt.com")

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
        while True:
            # wait a random amount of seconds
            wait_time = random.randint(3,10)
            time.sleep(wait_time)
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                return response.text

pattern = re.compile(r"^https://www\.transfermarkt\.(com|es)/[a-z0-9\-]+/startseite/wettbewerb/[A-Z0-9]+$")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 4:
        generate_sql_file = True
    elif len(args) == 1:
        generate_sql_file = False
    else:
        print("Usage: ")
        print("    Generate JSONs only:   python3 scrape_league.py <league_url>")
        print("    Generate SQL too:      python3 scrape_league.py <league_url> <init_league_id> <init_clubs_index> <init_players_index>")
        sys.exit(1)

    league_url = args[0]
    if not pattern.match(league_url):
        print("Invalid URL, it must be a league url from https://www.transfermarkt.com/")
        sys.exit(1)

    if generate_sql_file:
        league_id = args[1]
        clubs_index = int(args[2])
        players_index = args[3]
    else:
        league_id = str(uuid.uuid4())[:8]      # random id for storing

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

        # search script from absolute path
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        scrape_team_path = os.path.join(SCRIPT_DIR, "scrape_team.py")

        if generate_sql_file:
            result = subprocess.run(["python3", scrape_team_path, f"{team_url}", f"{league_id}", f"{clubs_index}", f"{players_index}"], capture_output=True, text=True)
            print(result.stdout)

            try:
                players_index = int(result.stdout.strip().splitlines()[-1])
            except Exception:
                print("Couldn't read players index") 
                
            clubs_index += 1
        else:
            subprocess.run(["python3", scrape_team_path, f"{team_url}", f"{league_id}"])  # the last argument is a random id for the league
    
    if generate_sql_file:
        print(players_index)
        print(clubs_index)
    