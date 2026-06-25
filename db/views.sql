-- Drop old views first (order matters due to dependencies)
DROP MATERIALIZED VIEW IF EXISTS top_players;
DROP MATERIALIZED VIEW IF EXISTS top_teams;

-- Top 100 players per competition/season with percentile ranks vs all players
CREATE MATERIALIZED VIEW top_players AS
WITH all_player_stats AS (
  SELECT
    e.player_id,
    p.player_name,
    e.competition_id,
    e.season_id,
    COUNT(*) FILTER (WHERE e.type = 'Shot' AND e.outcome = 'Goal') AS total_goals,
    COUNT(*) FILTER (WHERE e.type = 'Shot')                         AS total_shots,
    COUNT(*) FILTER (WHERE e.type = 'Pass')                         AS total_passes,
    ROUND(
      COUNT(*) FILTER (WHERE e.type = 'Shot' AND e.outcome = 'Goal')::NUMERIC
      / NULLIF(COUNT(*) FILTER (WHERE e.type = 'Shot'), 0), 3
    ) AS conversion_rate
  FROM events e
  JOIN players p ON e.player_id = p.player_id
  GROUP BY e.player_id, p.player_name, e.competition_id, e.season_id
),
ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY competition_id, season_id
      ORDER BY total_goals DESC, total_shots DESC
    ) AS rank,
    ROUND(PERCENT_RANK() OVER (
      PARTITION BY competition_id, season_id ORDER BY total_goals
    ) * 100) AS goals_pct,
    ROUND(PERCENT_RANK() OVER (
      PARTITION BY competition_id, season_id ORDER BY total_shots
    ) * 100) AS shots_pct,
    ROUND(PERCENT_RANK() OVER (
      PARTITION BY competition_id, season_id ORDER BY total_passes
    ) * 100) AS passes_pct,
    ROUND(PERCENT_RANK() OVER (
      PARTITION BY competition_id, season_id ORDER BY conversion_rate
    ) * 100) AS conversion_pct
  FROM all_player_stats
)
SELECT * FROM ranked WHERE rank <= 100;

-- All teams per competition/season with percentile ranks
CREATE MATERIALIZED VIEW top_teams AS
WITH all_team_stats AS (
  SELECT
    team,
    competition_id,
    season_id,
    COUNT(*) FILTER (WHERE type = 'Shot' AND outcome = 'Goal') AS goals_scored,
    COUNT(*) FILTER (WHERE type = 'Shot') AS total_shots,
    COUNT(*) FILTER (WHERE type = 'Pass') AS total_passes,
    ROUND(
      COUNT(*) FILTER (WHERE type = 'Shot' AND outcome = 'Goal')::NUMERIC
      / NULLIF(COUNT(*) FILTER (WHERE type = 'Shot'), 0), 3
    ) AS shot_conversion
  FROM events
  GROUP BY team, competition_id, season_id
)
SELECT *,
  ROW_NUMBER() OVER (
    PARTITION BY competition_id, season_id
    ORDER BY goals_scored DESC, total_shots DESC
  ) AS rank,
  ROUND(PERCENT_RANK() OVER (
    PARTITION BY competition_id, season_id ORDER BY goals_scored
  ) * 100) AS goals_pct,
  ROUND(PERCENT_RANK() OVER (
    PARTITION BY competition_id, season_id ORDER BY total_shots
  ) * 100) AS shots_pct,
  ROUND(PERCENT_RANK() OVER (
    PARTITION BY competition_id, season_id ORDER BY total_passes
  ) * 100) AS passes_pct,
  ROUND(PERCENT_RANK() OVER (
    PARTITION BY competition_id, season_id ORDER BY shot_conversion
  ) * 100) AS conversion_pct
FROM all_team_stats;

-- Refresh after re-seeding:
-- REFRESH MATERIALIZED VIEW top_players;
-- REFRESH MATERIALIZED VIEW top_teams;
