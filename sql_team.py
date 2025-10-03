import sys
import json
import random

def validate_filename(filename):
    return filename.endswith('.json')

position_map = {
    "PO": 1,
    "DFC": 2,
    "DFI": 3,
    "DFD": 4,
    "MCD": 5,
    "MC": 6,
    "MI": 7,
    "MD": 8,
    "DC": 9,
    "MCO": 10,
    "MP": 11,
    "EI": 12,
    "ED": 13,
}

def generate_club_sql(club_data, club_id):
    sql = []
    name = club_data["name"]
    league_id = club_data["league_id"]


    sql.append(f"-- Club: {name}")
    sql.append(f"INSERT INTO club (id, name, league_id) VALUES ({club_id}, '{name}', {league_id});")

    stadium = club_data.get("stadium")
    if stadium:
        stadium_name = stadium["name"].replace("'","''")
        capacity = stadium.get('capacity')
        sql.append(f"INSERT INTO stadium (id, name, capacity, club_id) VALUES ({club_id}, '{stadium_name}', {capacity}, {club_id});")
    
    sql.append(f"INSERT INTO youth_academy (id, club_id) VALUES ({club_id}, {club_id})")

    sql.append("")

    return sql

def generate_players_sql(players, club_id, starting_id=1000):
    sql = []

    for i, player in enumerate(players):
        player_id = starting_id + i
        attr_id = player_id
        ya_id = "NULL"  # real players are not gonna be in young academies 

        name = player["name"].replace("'","''")

        pos_txt = player["position"] or "NULL"
        if pos_txt == "NULL": continue
        pos_id = position_map.get(pos_txt, 99) 

        birth_date = player["birth_date"]
        age = player["age"]
        nationality = player["nationality"] or "Argentina"
        height = player["height"] or 1.75
        foot = player["foot"] or "Derecho"

        # random attributes for the moment
        attrs = {
            "passing": random.randint(40, 90),
            "shooting": random.randint(40, 90),
            "dribbling": random.randint(40, 90),
            "tackling": random.randint(40, 90),
            "pace": random.randint(40, 90),
            "stamina": random.randint(40, 90),
            "vision": random.randint(40, 90),
            "positioning": random.randint(40, 90),
            "decision_making": random.randint(40, 90),
            "strength": random.randint(40, 90)
        }

        sql.append(f"-- {name}")
        sql.append(
            f"INSERT INTO person (id, name, birth_date, age, nationality) VALUES "
            f"({player_id}, '{name}', '{birth_date}', {age}, '{nationality}');"
        )

        sql.append(
            f"INSERT INTO attributes (id, passing, shooting, dribbling, tackling, pace, stamina, vision, positioning, decision_making, strength) "
            f"VALUES ({attr_id}, {attrs['passing']}, {attrs['shooting']}, {attrs['dribbling']}, {attrs['tackling']}, {attrs['pace']}, {attrs['stamina']}, "
            f"{attrs['vision']}, {attrs['positioning']}, {attrs['decision_making']}, {attrs['strength']});"
        )

        sql.append(
            f"INSERT INTO player (id, foot, height, attr_id, club_id, ya_id) "
            f"VALUES ({player_id}, '{foot}', {height}, {attr_id}, {club_id}, {ya_id});"
        )

        sql.append(
            f"INSERT INTO player_position (player_id, position_id) VALUES ({player_id}, {pos_id});"
        )

        sql.append(
            f"INSERT INTO contract"
        )
        sql.append("")

    sql.append("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    sql.append("")
    new_player_index = player_id + 1
    return sql, new_player_index

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 3:
        print("USAGE: python3 sql_team <team_file> <team_id> <players_index>")
        sys.exit(1)
    team_file = args[0]
    club_id = args[1]
    players_index = int(args[2])


    if validate_filename(team_file):
        with open(team_file) as f:
            data = json.load(f)
    
        
        club_sql = generate_club_sql(data["club"], club_id)
        players_sql, players_index = generate_players_sql(data["players"], club_id, players_index)

        with open(f"insert_teams.sql", "a") as out:
            out.write("\n".join(club_sql + players_sql))

        print(f"Generated SQL file for {team_file}")
        print(players_index)

    else:
        print("Invalid file name")