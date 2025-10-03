# Transfermarkt Scraper

This project contains a set of Python scripts to scrape data from [Transfermarkt](https://www.transfermarkt.com/) using **BeautifulSoup**.  
It allows you to extract league, club, and player information into JSON files.  
Additionally, it includes an **SQL generator** that adapts the scraped data to a custom database schema (originally designed for a Football Manager–style game).

---

## Features
- Scrape any league page from Transfermarkt:
  - Extracts all clubs in the league.
  - For each club, extracts stadium info and player roster.
- Saves results into structured **JSON files**.
- (Optional) Converts JSON into **SQL insert statements** for a specific database schema.

---

## Project Structure
```
.
├── scrape_league.py    # Entry point: scrape an entire league
├── scrape_team.py      # Scrape a single team and its players
├── sql_team.py         # Convert scraped JSON into SQL inserts (custom schema)
├── cache/              # Local cache of downloaded HTML pages
└── league<ID>/         # JSON output directory per league
```

---

## Requirements
- Python 3.8+
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://pypi.org/project/requests/)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
### Scraping a League
```bash
python3 scrape_league.py <league_url> <league_id> <clubs_index> <players_index>
```
- `league_url`: URL of the league page on Transfermarkt (e.g. https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1)

- `league_id`: Numeric ID (custom, used in JSON/SQL output).

- `clubs_index`: Starting index for club IDs.

- `players_index`: Starting index for player IDs.

This will:

1. Download (or load from cache) the league page.

2. Scrape all teams in the league.

3. For each team, call `scrape_team.py`.

4. Save JSON files under `league<league_id>/`.

### Scraping a Team
```bash
python3 scrape_team.py <team_url> <league_id> <team_id> <players_index>
```
This saves a <TEAM>.json file with:

```json
{
  "club": {
    "name": "Example FC",
    "league_id": 1,
    "stadium": {
      "name": "Sample Stadium",
      "capacity": 50000
    }
  },
  "players": [
    {
      "name": "John Doe",
      "position": "DC",
      "birth_date": "1995-06-21",
      "age": 28,
      "nationality": "England",
      "height": 1.85,
      "foot": "Right"
    }
  ]
}
```
---
## SQL Generator (Optional)
The script sql_team.py converts JSON into SQL insert statements following a custom schema designed for a Football Manager–style game.

Usage:

```bash
python3 sql_team.py <team_file.json> <team_id> <players_index>
```
It will append insert statements to insert_teams.sql.

⚠️ Note: This schema is specific to my own game project.
If you want to use the scraper for another purpose, you can ignore sql_team.py and work directly with the JSON output.

## Disclaimer
This project is for educational and personal use.

Respect Transfermarkt’s Terms of Service.

Avoid making excessive requests (use caching as implemented).

## License
MIT License – feel free to use, adapt, and extend the scraping scripts.
The SQL generator is provided as an example integration with a custom game database.