# Transfermarkt Scraper

This project contains a set of Python scripts to scrape data from [Transfermarkt](https://www.transfermarkt.com/) using **BeautifulSoup**.  
It allows you to extract league, club, and player information into JSON files.  
Additionally, it includes an **SQL generator** that adapts the scraped data to a custom database schema, serving to the functionality of manually update the squads of the football management game [ChiquiLeague](https://github.com/FranVesnaver/chiquileague).

---

## Features
- Scrape any league page from Transfermarkt:
  - Extracts all clubs in the league.
  - For each club, extracts stadium info and player roster.
- Saves results into structured **JSON files**.
- (Optional) Converts JSON into **SQL insert statements** for a [specific database schema](#about-the-sql-generator).

---

## Project Structure
```
.
├── scrape_league.py        # Entry point: scrape an entire league
├── scrape_team.py          # Scrape a single team and its players
├── sql_team.py             # Convert scraped JSON into SQL inserts (custom schema)
├── cache/                  # Local cache of downloaded HTML pages
└── output/                 # Output folder
    ├── league<ID>/         # JSON output directory per league
    └── insert_teams.sql    # SQL inserts for teams and players
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
You can run the scraper in two modes:
1. JSON only – download data as JSON files.
2. JSON + SQL – download JSON and also generate SQL inserts for a custom schema.

### Scraping a League
#### JSON only
```bash
python3 scrape_league.py <league_url>
```
- `league_url`: URL of the league page on Transfermarkt (e.g. https://www.transfermarkt.com/torneo-final/startseite/wettbewerb/ARGC)

This will:
- Scrape all teams and players in the league.
- Save JSON files into:

---
#### JSON + SQL
```bash
python3 scrape_league.py <league_url> <league_id> <clubs_index> <players_index>
```
- `league_url`: URL of the league page on Transfermarkt (e.g. https://www.transfermarkt.com/torneo-final/startseite/wettbewerb/ARGC)

- `league_id`: Numeric ID (custom, used in JSON/SQL output).

- `clubs_index`: Starting index for club IDs.

- `players_index`: Starting index for player IDs.

This will:
- Scrape all teams and players in the league.
- Save JSON files into `output/league<league_id>/<TEAM>.json`.
- Generate an SQL file with all insert statements: `output/insert_teams.sql`.

### Scraping a Team
You could also run the script to an individual team
```bash
python3 scrape_team.py <team_url> <league_id> <team_id> <players_index>
```
This saves a `<TEAM>.json` file with:

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
## About the SQL Generator
The script `sql_team.py` converts JSON into SQL insert statements following a custom schema designed for [ChiquiLeague](https://github.com/FranVesnaver/chiquileague), a Football Manager–style game. It can be used to manually update the squads of the clubs featured in the game. 

Usage:

```bash
python3 sql_team.py <team_file.json> <team_id> <players_index>
```
It will append insert statements to insert_teams.sql. It is recommended not to use this script individually, but to run `scrape_league.py` with the SQL option.
Follow instructions in the [ChiquiLeague repo](https://github.com/FranVesnaver/chiquileague) to integrate the new squads to the game. 

Note: This schema is specific to my own game project.
If you want to use the scraper for another purpose, you can ignore sql_team.py and work directly with the JSON output.

## Disclaimer
This project is for educational and personal use.

Respect Transfermarkt’s Terms of Service.

Avoid making excessive requests (use caching as implemented).
