import streamlit as st
import pandas as pd
from db import query

st.set_page_config(
    page_title="Soccer Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #f8fafc;
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] p {
    color: #64748b !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Header ── */
.page-header {
    padding: 0 0 1.5rem 0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 2rem;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 0.25rem 0;
}
.page-header p {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0;
    border-bottom: 1px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.6rem 1.2rem;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom: 2px solid #2563eb !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}

/* ── Search box ── */
.stTextInput > div > div > input {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #0f172a;
    font-size: 0.875rem;
}
.stTextInput > div > div > input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}

/* ── Stat card ── */
.stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.2rem 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stat-card:hover {
    border-color: #2563eb;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08);
}
.card-header {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.85rem;
}
.card-rank {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    background: #f1f5f9;
    border-radius: 20px;
    padding: 1px 8px;
    flex-shrink: 0;
}
.card-name {
    font-size: 0.98rem;
    font-weight: 600;
    color: #0f172a;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ── Stat row (label + value + bar + pct) ── */
.stat-row {
    display: grid;
    grid-template-columns: 90px 38px 1fr 36px;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
}
.stat-label {
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}
.stat-value {
    font-size: 0.8rem;
    font-weight: 600;
    color: #334155;
    text-align: right;
}
.bar-bg {
    background: #e2e8f0;
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.bar-fill {
    height: 6px;
    border-radius: 4px;
}
.bar-low    { background: #f97316; }
.bar-mid    { background: #eab308; }
.bar-high   { background: #22c55e; }
.bar-elite  { background: #2563eb; }
.pct-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #94a3b8;
    text-align: right;
    white-space: nowrap;
}

/* ── Summary metric pills at top ── */
.summary-strip {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.summary-pill {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    min-width: 110px;
}
.summary-pill .pill-label {
    font-size: 0.68rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.summary-pill .pill-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}

/* ── Responsive grid ── */
div[data-testid="column"] {
    padding: 0 0.35rem;
}

/* ── About section ── */
.about-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.about-card h3 {
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.75rem 0;
}
.about-card p {
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.65;
    margin: 0 0 0.5rem 0;
}
.about-card p:last-child { margin-bottom: 0; }
.about-card a {
    color: #2563eb;
    text-decoration: none;
}
.about-card a:hover { text-decoration: underline; }
.tool-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.5rem;
}
.tool-chip {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #334155;
}
.tool-chip.highlight {
    background: #eff6ff;
    border-color: #bfdbfe;
    color: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def pct_bar(value: float, label: str, display: str) -> str:
    pct = float(value or 0)
    width = max(2, int(pct))
    if pct < 33:
        cls = "bar-low"
    elif pct < 60:
        cls = "bar-mid"
    elif pct < 85:
        cls = "bar-high"
    else:
        cls = "bar-elite"
    suffix = "th" if 4 <= int(pct) % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(int(pct) % 10, "th")
    return f"""
    <div class="stat-row">
      <span class="stat-label">{label}</span>
      <span class="stat-value">{display}</span>
      <div class="bar-bg"><div class="bar-fill {cls}" style="width:{width}%"></div></div>
      <span class="pct-label">{int(pct)}{suffix}</span>
    </div>"""


def player_card(p: dict) -> str:
    conv = float(p.get("conversion_rate") or 0) * 100
    return f"""
    <div class="stat-card">
      <div class="card-header">
        <span class="card-rank">#{p['rank']}</span>
        <span class="card-name">{p['player_name']}</span>
      </div>
      {pct_bar(p.get('goals_pct'), 'Goals', str(int(p['total_goals'])))}
      {pct_bar(p.get('shots_pct'), 'Shots', str(int(p['total_shots'])))}
      {pct_bar(p.get('passes_pct'), 'Passes', str(int(p['total_passes'])))}
      {pct_bar(p.get('conversion_pct'), 'Conv %', f"{conv:.1f}%")}
    </div>"""


def team_card(t: dict) -> str:
    conv = float(t.get("shot_conversion") or 0) * 100
    return f"""
    <div class="stat-card">
      <div class="card-header">
        <span class="card-rank">#{t['rank']}</span>
        <span class="card-name">{t['team']}</span>
      </div>
      {pct_bar(t.get('goals_pct'), 'Goals', str(int(t['goals_scored'])))}
      {pct_bar(t.get('shots_pct'), 'Shots', str(int(t['total_shots'])))}
      {pct_bar(t.get('passes_pct'), 'Passes', str(int(t['total_passes'])))}
      {pct_bar(t.get('conversion_pct'), 'Conv %', f"{conv:.1f}%")}
    </div>"""


def summary_strip(items: list[tuple]) -> str:
    pills = "".join(
        f'<div class="summary-pill"><div class="pill-label">{label}</div>'
        f'<div class="pill-value">{value}</div></div>'
        for label, value in items
    )
    return f'<div class="summary-strip">{pills}</div>'


def render_grid(cards: list[str], cols: int = 3) -> None:
    col_objs = st.columns(cols, gap="small")
    for i, card_html in enumerate(cards):
        col_objs[i % cols].markdown(card_html, unsafe_allow_html=True)


# ── Competition selector ───────────────────────────────────────────────────────

competitions = query("""
    WITH match_counts AS (
        SELECT competition_id, season_id, COUNT(*) AS match_count
        FROM matches
        GROUP BY competition_id, season_id
        HAVING COUNT(*) >= 10
    ),
    team_balance AS (
        SELECT competition_id, season_id,
               MAX(team_matches) AS max_tm,
               MIN(team_matches) AS min_tm
        FROM (
            SELECT competition_id, season_id, team,
                   COUNT(DISTINCT match_id) AS team_matches
            FROM events
            GROUP BY competition_id, season_id, team
        ) t
        GROUP BY competition_id, season_id
    )
    SELECT c.competition_id, c.season_id, c.competition_name, c.season_name,
           mc.match_count
    FROM competitions c
    JOIN match_counts mc USING (competition_id, season_id)
    JOIN team_balance tb USING (competition_id, season_id)
    WHERE tb.max_tm::float / NULLIF(tb.min_tm, 0) <= 4
    ORDER BY c.competition_name, c.season_name
""")

if not competitions:
    st.error("No data found. Run `python db/seed.py` to load StatsBomb data.")
    st.stop()

comp_labels = {
    f"{c['competition_name']} — {c['season_name']}": c
    for c in competitions
}


with st.sidebar:
    st.markdown("### Soccer Analytics")
    st.markdown("---")
    selected_label = st.selectbox(
        "Competition & Season",
        list(comp_labels.keys()),
        label_visibility="visible",
    )

selected = comp_labels[selected_label]
competition_id = selected["competition_id"]
season_id = selected["season_id"]

comp_name = selected["competition_name"]
season_name = selected["season_name"]

match_count = selected["match_count"]
st.markdown(f"""
<div class="page-header">
  <h1>{comp_name}</h1>
  <p>{season_name} &nbsp;·&nbsp; {match_count} matches &nbsp;·&nbsp; StatsBomb Open Data</p>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_teams, tab_players, tab_about = st.tabs(["Teams", "Players", "About"])


# ── Teams tab ─────────────────────────────────────────────────────────────────

with tab_teams:
    teams = query("""
        SELECT rank, team, goals_scored, total_shots, total_passes, shot_conversion,
               goals_pct, shots_pct, passes_pct, conversion_pct
        FROM top_teams
        WHERE competition_id = :cid AND season_id = :sid
        ORDER BY rank
    """, {"cid": competition_id, "sid": season_id})

    if not teams:
        st.info("No team data for this competition/season.")
    else:
        df_teams = pd.DataFrame(teams)
        total_goals = int(df_teams["goals_scored"].sum())
        avg_shots = int(df_teams["total_shots"].mean())
        avg_conv = round(df_teams["shot_conversion"].astype(float).mean() * 100, 1)
        n_teams = len(df_teams)

        st.markdown(summary_strip([
            ("Teams", n_teams),
            ("Total Goals", total_goals),
            ("Avg Shots / Team", avg_shots),
            ("Avg Conv %", f"{avg_conv}%"),
        ]), unsafe_allow_html=True)

        search = st.text_input("Search team", placeholder="Filter teams…", key="team_search")
        if search:
            teams = [t for t in teams if search.lower() in t["team"].lower()]

        cards = [team_card(t) for t in teams]
        render_grid(cards, cols=3)


# ── Players tab ───────────────────────────────────────────────────────────────

with tab_players:
    players = query("""
        SELECT rank, player_name, total_goals, total_shots, total_passes, conversion_rate,
               goals_pct, shots_pct, passes_pct, conversion_pct
        FROM top_players
        WHERE competition_id = :cid AND season_id = :sid
        ORDER BY rank
    """, {"cid": competition_id, "sid": season_id})

    if not players:
        st.info("No player data for this competition/season.")
    else:
        df_players = pd.DataFrame(players)
        total_goals = int(df_players["total_goals"].sum())
        top_scorer = df_players.iloc[0]["player_name"]
        top_goals = int(df_players.iloc[0]["total_goals"])
        n_players = len(df_players)

        st.markdown(summary_strip([
            ("Players", n_players),
            ("Total Goals", total_goals),
            ("Top Scorer", top_scorer),
            ("Top Goals", top_goals),
        ]), unsafe_allow_html=True)

        search = st.text_input("Search player", placeholder="Filter players…", key="player_search")
        if search:
            players = [p for p in players if search.lower() in p["player_name"].lower()]

        cards = [player_card(p) for p in players]
        render_grid(cards, cols=3)


# ── About tab ─────────────────────────────────────────────────────────────────

with tab_about:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("""
        <div class="about-card">
          <h3>What this shows</h3>
          <p>
            This dashboard explores player and team performance across professional
            soccer competitions. For each competition and season you can browse the
            top 100 players and every team, ranked by goals, shots, passes, and
            shot-conversion rate.
          </p>
          <p>
            Every stat card shows a <strong>percentile bar</strong> — the colored
            bar tells you where that player or team sits relative to everyone else
            in the same competition and season (100th percentile = best in the
            competition).
          </p>
        </div>

        <div class="about-card">
          <h3>Data source</h3>
          <p>
            All data comes from the
            <a href="https://github.com/statsbomb/open-data" target="_blank">StatsBomb Open Data</a>
            repository — a free, publicly available dataset of professional match
            event data released by StatsBomb for research and education.
          </p>
          <p>
            The dataset covers dozens of competitions and seasons, with millions of
            individual match events (passes, shots, goals, etc.) tracked to the
            second and pitch coordinate.
          </p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="about-card">
          <h3>Tools &amp; stack</h3>
          <div class="tool-list">
            <span class="tool-chip highlight">PostgreSQL</span>
            <span class="tool-chip highlight">SQL</span>
            <span class="tool-chip">Python</span>
            <span class="tool-chip">Streamlit</span>
            <span class="tool-chip">Neon (cloud DB)</span>
          </div>
        </div>

        <div class="about-card">
          <h3>How SQL powers the analytics</h3>
          <p>
            The raw StatsBomb events are stored in a PostgreSQL table with millions
            of rows. All aggregations are pre-computed as
            <strong>materialized views</strong> so the dashboard queries are fast.
          </p>
          <p>
            Key SQL techniques used:
          </p>
          <ul style="font-size:0.875rem;color:#334155;line-height:1.8;padding-left:1.2rem;margin:0">
            <li><strong>CTEs</strong> to stage aggregations in readable layers</li>
            <li><strong>Filtered aggregates</strong> (<code>COUNT(*) FILTER (WHERE …)</code>) to pivot event types into columns in a single pass</li>
            <li><strong>Window functions</strong> (<code>PERCENT_RANK()</code>, <code>ROW_NUMBER()</code>) to compute percentile ranks and leaderboard position per competition</li>
            <li><strong>Materialized views</strong> to cache the results so live queries are instant</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
