CREATE TABLE IF NOT EXISTS competitions (
    competition_id INTEGER,
    season_id INTEGER,
    competition_name TEXT,
    season_name TEXT,
    PRIMARY KEY (competition_id, season_id)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER,
    season_id INTEGER,
    match_date DATE,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    FOREIGN KEY (competition_id, season_id) REFERENCES competitions(competition_id, season_id)
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT,
    nationality TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    team TEXT,
    type TEXT,
    minute INTEGER,
    second INTEGER,
    x NUMERIC,
    y NUMERIC,
    outcome TEXT,
    competition_id INTEGER,
    season_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_events_player ON events(player_id);
CREATE INDEX IF NOT EXISTS idx_events_team ON events(team);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_match ON events(match_id);
