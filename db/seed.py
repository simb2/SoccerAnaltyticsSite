import os
import json
import requests
import psycopg2
import psycopg2.extras

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

def fetch(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_xy(location):
    if isinstance(location, list) and len(location) >= 2:
        return location[0], location[1]
    return None, None

def seed():
    conn = psycopg2.connect(dbname="soccer", user=os.environ["USER"])
    cur = conn.cursor()

    cur.execute("TRUNCATE events, players, matches, competitions RESTART IDENTITY CASCADE")
    conn.commit()

    # --- Competitions ---
    comps = fetch(f"{BASE_URL}/competitions.json")
    psycopg2.extras.execute_values(cur,
        "INSERT INTO competitions (competition_id, season_id, competition_name, season_name) VALUES %s",
        [(c["competition_id"], c["season_id"], c["competition_name"], c["season_name"]) for c in comps]
    )
    conn.commit()
    print(f"Loaded {len(comps)} competitions")

    # --- Matches + Events ---
    seen_players = set()
    total_matches = 0
    total_events = 0

    for comp in comps:
        cid = comp["competition_id"]
        sid = comp["season_id"]

        try:
            matches = fetch(f"{BASE_URL}/matches/{cid}/{sid}.json")
        except Exception as e:
            print(f"  SKIP matches {cid}/{sid}: {e}")
            continue

        match_rows = []
        for m in matches:
            match_rows.append((
                m["match_id"],
                cid, sid,
                m.get("match_date"),
                m["home_team"]["home_team_name"],
                m["away_team"]["away_team_name"],
                m.get("home_score"),
                m.get("away_score")
            ))

        psycopg2.extras.execute_values(cur,
            """INSERT INTO matches
               (match_id, competition_id, season_id, match_date, home_team, away_team, home_score, away_score)
               VALUES %s ON CONFLICT (match_id) DO NOTHING""",
            match_rows
        )
        conn.commit()
        total_matches += len(matches)

        # --- Events: one match at a time ---
        for m in matches:
            mid = m["match_id"]
            try:
                events = fetch(f"{BASE_URL}/events/{mid}.json")
            except Exception as e:
                print(f"  SKIP events {mid}: {e}")
                continue

            event_rows = []
            player_rows = []

            for e in events:
                x, y = extract_xy(e.get("location"))
                event_rows.append((
                    e["id"],
                    mid,
                    e.get("player", {}).get("id") if e.get("player") else None,
                    e.get("team", {}).get("name") if e.get("team") else None,
                    e.get("type", {}).get("name") if e.get("type") else None,
                    e.get("minute"),
                    e.get("second"),
                    x, y,
                    e.get("shot", {}).get("outcome", {}).get("name") if e.get("shot") else None,
                    cid, sid
                ))

                if e.get("player"):
                    pid = e["player"]["id"]
                    if pid not in seen_players:
                        seen_players.add(pid)
                        player_rows.append((pid, e["player"].get("name")))

            if player_rows:
                psycopg2.extras.execute_values(cur,
                    "INSERT INTO players (player_id, player_name) VALUES %s ON CONFLICT (player_id) DO NOTHING",
                    player_rows
                )

            psycopg2.extras.execute_values(cur,
                """INSERT INTO events
                   (event_id, match_id, player_id, team, type, minute, second, x, y, outcome, competition_id, season_id)
                   VALUES %s""",
                event_rows
            )
            conn.commit()
            total_events += len(event_rows)

        print(f"[{comp['competition_name']} {comp['season_name']}] {len(matches)} matches, {total_events} events so far")

    cur.close()
    conn.close()
    print(f"Done. {total_matches} matches, {total_events} events total.")

if __name__ == "__main__":
    seed()
