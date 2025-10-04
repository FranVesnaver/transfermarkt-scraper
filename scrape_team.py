import time
import requests
from bs4 import BeautifulSoup
import json
import re
import random
import hashlib
import os
import sys
import subprocess

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

HEADERS = {
    'User-Agent': random.choice(USER_AGENTS)
}

position_map = {
    "Portero": "PO",
    "Defensa central": "DFC",
    "Defensa": "DFC",
    "Lateral derecho": "DFD",
    "Lateral izquierdo": "DFI",
    "Pivote": "MCD",
    "Mediocentro": "MC",
    "Interior derecho": "MD",
    "Interior izquierdo": "MI",
    "Extremo derecho": "ED",
    "Extremo izquierdo": "EI",
    "Delantero centro": "DC",
    "Delantero": "DC",
    "Mediocentro ofensivo": "MCO"
}

def url_to_filename(url):
    # Crea un nombre de archivo único basado en la URL
    h = hashlib.md5(url.encode()).hexdigest()
    return f"cache/{h}.html"

def fetch_or_load_html(url):
    # Devuelve el HTML desde cache si existe, o lo descarga
    os.makedirs("cache", exist_ok=True)
    file_path = url_to_filename(url)

    if os.path.exists(file_path):
        print(f"📂 Using cache: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"🌐 Downloading: {url}")
        while True:
            wait_time = random.randint(3,10)
            time.sleep(wait_time)
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                return response.text

def parse_height(height_str):
    match = re.match(r"^\d{1},\d{2}\s?m$", height_str)
    if match:
        return float(height_str.replace("m", "").replace(",", ".").strip())
    return None

def parse_foot(foot_str):
    return foot_str.strip() if foot_str in ["Derecho", "Izquierdo"] else None

def format_date(str):
    match = re.match(r"(\d{2})/(\d{2})/(\d{4})", str)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    return str

def scrape_team(url, league_id=0):
    html = fetch_or_load_html(url)
    if not html:
        sys.exit(1)
    soup = BeautifulSoup(html, 'html.parser')

    # Extrae el nombre del equipo desde el header principal
    header = soup.find("header", class_="data-header")
    team_name = None
    if header:
        h1 = header.find("h1")
        if h1:
            team_name = h1.text.strip()
    
    # Scrape stadium name and capacity
    stadium_name = None
    capacity = None

    # Busca el <li> que contiene "Estadio:"
    li_stadium = soup.find("li", string=lambda t: t and "Estadio:" in t)
    if not li_stadium:
        # Si no lo encuentra por string, busca por clase y recorre los <li>
        for li in soup.select("li.data-header__label"):
            if "Estadio:" in li.get_text():
                li_stadium = li
                break

    if li_stadium:
        # Nombre del estadio
        a = li_stadium.find("a")
        if a:
            stadium_name = a.text.strip()
        # Capacidad
        span = li_stadium.find("span", class_="tabellenplatz")
        if span:
            match = re.search(r"([\d\.]+)", span.text)
            if match:
                capacity = int(match.group(1).replace(".", ""))



    # Scrape players
    table = soup.find('table', class_='items')

    if not table:
        print("Couldn't find players table")
        sys.exit(1)

    players = []
    for row in table.select("tbody > tr"):
        if not row.find("td", class_="posrela"):
            continue

        # Name
        name_tag = row.select_one("td.posrela table.inline-table td.hauptlink a")
        name = name_tag.text.strip() if name_tag else None

        # Position
        position_tag = row.select_one("td.posrela table.inline-table tr:nth-of-type(2) td")
        position = position_tag.text.strip() if position_tag else None
        position = position_map.get(position)

        # Age and birth date
        age = None
        birth_date = None
        age_td = row.find("td", {"class": "zentriert"}, string=re.compile(r"\(\d+\)"))
        if age_td:
            text = age_td.text.strip()

            match_age = re.search(r"\((\d+)\)", text)
            if match_age:
                age = int(match_age.group(1))

            match_birth = re.search(r"(\d{2}/\d{2}/\d{4})", text)
            if match_birth:
                birth_date = match_birth.group(1)
                birth_date = format_date(birth_date)

        # Nationality
        nationality = None
        flag_img = row.find("img", class_="flaggenrahmen")
        if flag_img:
            nationality = flag_img.get("title", "")
            
        # Height
        height = None
        for td in row.find_all("td", class_="zentriert"):
            if "m" in td.text:
                height = parse_height(td.text.strip())
                break

        # Foot
        foot = "Derecho"
        for td in row.find_all("td", class_="zentriert"):
            if td.text.strip() in ["Derecho", "Izquierdo", "Ambidiestro"]:
                foot = td.text.strip()
                break

        players.append({
            "name": name,
            "position": position,
            "birth_date": birth_date,
            "age": age,
            "nationality": nationality,
            "height": height,
            "foot": foot
        })

    return {
        "club": {
            "name": team_name,
            "league_id": league_id,
            "stadium": {
                "name": stadium_name,
                "capacity": capacity
            }
        },
        "players": players
    }

pattern = re.compile(r"^https://www\.transfermarkt\.(com|es)/[a-z0-9\-]+/kader/verein/\d+/saison_id/\d{4}/plus/1$")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 4:
        generate_sql_file = True
    elif len(args) == 1 or len(args) == 2:       # if len(args) == 2 it means scrape_league run the script
        generate_sql_file = False
    else:
        print("Usage: ")
        print("    Generate JSONs only:   python3 scrape_team.py <url>")
        print("    Generate SQL too:      python3 scrape_team.py <url> <league_id> <team_id> <players_index>")
        sys.exit(1)
    
    url = args[0]
    if not pattern.match(url):
        print("Invalid URL, it must be a club url from https://www.transfermarkt.com/")
        sys.exit(1)
    league_id = args[1]

    if generate_sql_file:
        team_id = args[2]
        players_index = args[3]

    team = url.split("/")[-8]  # Extract team name from URL
    team = team.replace("-", "_").upper()  # Normalize team name
    if generate_sql_file:
        data = scrape_team(url, league_id)
    else:
        data = scrape_team(url)

    output_dir = os.path.join("output", f"league{league_id}")
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, f"{team}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    
    print(f"✅ Saved {len(data['players'])} players from {data['club']['name']} into {team}.json")
    
    if generate_sql_file:
        result = subprocess.run(
            ["python3", "sql_team.py", os.path.join("output", f"league{league_id}", f"{team}.json"), f"{team_id}", f"{players_index}"],
            capture_output=True, text=True
        )
        print(result.stdout)
        

        try:
            players_index = int(result.stdout.strip().splitlines()[-1])
        except Exception:
            print("Couldn't read players index")

        print(players_index)
