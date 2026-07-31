import streamlit as stimport streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

st.set_page_config(page_title="Touchdown Tokens", page_icon="🏈", layout="centered")

# --- SUPABASE CONFIGURATION (SESSION ISOLATED) ---
def get_supabase_client() -> Client:
    if "supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state.supabase_client = create_client(url, key)
    return st.session_state.supabase_client

supabase = get_supabase_client()

# --- AUTHENTICATION STATE & PERSISTENCE ---
if "user" not in st.session_state:
    st.session_state.user = None
    try:
        current_session = supabase.auth.get_session()
        if current_session and current_session.user:
            st.session_state.user = current_session.user
    except Exception:
        pass

# Comprehensive NFL Team Logos & Primary Accent Hex Colors
NFL_TEAM_DATA = {
    "🏈 Free Agent / Neutral": {"logo": "https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg", "color": "#fbbf24"},
    "🔴 Arizona Cardinals": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png", "color": "#97233F"},
    "🔴 Atlanta Falcons": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png", "color": "#A71930"},
    "🟣 Baltimore Ravens": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png", "color": "#241773"},
    "🔴 Buffalo Bills": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png", "color": "#00338D"},
    "🔵 Carolina Panthers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png", "color": "#0085CA"},
    "🟠 Chicago Bears": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png", "color": "#C83803"},
    "🟠 Cincinnati Bengals": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png", "color": "#FB4F14"},
    "🟤 Cleveland Browns": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png", "color": "#FF3C00"},
    "🔵 Dallas Cowboys": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png", "color": "#003594"},
    "🟠 Denver Broncos": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/den.png", "color": "#FB4F14"},
    "🔵 Detroit Lions": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/det.png", "color": "#0076B6"},
    "🟢 Green Bay Packers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png", "color": "#203731"},
    "🔴 Houston Texans": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png", "color": "#03202F"},
    "🔵 Indianapolis Colts": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png", "color": "#002C5F"},
    "🐆 Jacksonville Jaguars": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png", "color": "#006778"},
    "🔴 Kansas City Chiefs": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png", "color": "#E31837"},
    "🪙 Las Vegas Raiders": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png", "color": "#A5ACAF"},
    "⚡ Los Angeles Chargers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png", "color": "#0080C6"},
    "🟡 Los Angeles Rams": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png", "color": "#003594"},
    "🐬 Miami Dolphins": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png", "color": "#008E97"},
    "🟣 Minnesota Vikings": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/min.png", "color": "#4F2683"},
    "🔵 New England Patriots": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png", "color": "#002244"},
    "⚜️ New Orleans Saints": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png", "color": "#D3BC8D"},
    "🔵 New York Giants": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png", "color": "#0B2265"},
    "🟢 New York Jets": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png", "color": "#125740"},
    "🦅 Philadelphia Eagles": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png", "color": "#004C54"},
    "🟡 Pittsburgh Steelers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png", "color": "#FFB612"},
    "🔴 San Francisco 49ers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png", "color": "#AA0000"},
    "🟢 Seattle Seahawks": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png", "color": "#69BE28"},
    "🔴 Tampa Bay Buccaneers": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png", "color": "#D50A0A"},
    "🔵 Tennessee Titans": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png", "color": "#4B92DB"},
    "🔴 Washington Commanders": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/was.png", "color": "#5A1414"}
}

NFL_TEAMS = list(NFL_TEAM_DATA.keys())
AVATAR_OPTIONS = ["🏈", "🐐", "⚡", "👑", "🎯", "💣", "💎", "🔥", "🛡️", "🚀"]

BORDER_OPTIONS = {
    "None": "border: none;",
    "Gold Champion": "border: 3px solid #f59e0b; box-shadow: 0 0 10px #f59e0b;",
    "Neon Pulse": "border: 3px solid #06b6d4; box-shadow: 0 0 10px #06b6d4;",
    "Fire Red": "border: 3px solid #ef4444; box-shadow: 0 0 10px #ef4444;",
    "Toxic Green": "border: 3px solid #22c55e; box-shadow: 0 0 10px #22c55e;",
    "Deep Purple": "border: 3px solid #9333ea; box-shadow: 0 0 10px #9333ea;"
}

MASTER_BADGES = {
    "🚀 Token Tycoon": "Reach a balance of 30+ tokens",
    "🎯 High Roller": "Wager 10+ tokens on a single question",
    "⚡ Double Down Legend": "Wager 15+ total tokens in a single week",
    "💣 All-In Maverick": "Wager 100% of your remaining token balance on a slate",
    "🏈 TD Guru": "Correctly predict 2+ Touchdown Scorers",
    "🎯 Sniper": "Correctly predict 3+ Touchdown Scorers across the season",
    "👑 Weekly High Scorer": "Win the most net tokens in a single week",
    "🎯 Perfect 10/10": "Correctly answer all 10 scenarios in a single week",
    "🧊 Clutch Gene": "Win a scenario where 75%+ of the league picked the wrong side",
    "🛡️ Iron Defender": "Submit bets for 5 or more weeks without missing",
    "💰 Century Club": "Accumulate 100+ total cumulative tokens won across history",
    "📉 Wall Street Bets": "Take the largest token loss in a single week",
    "📉 Down Bad": "Reach a token balance of 0 tokens",
    "🏆 League Champion": "Be crowned the official end-of-season League Champion",
    "🔮 Oracle of Delphi": "Successfully call a 5+ token wager correctly 4 weeks in a row",
    "🔥 Untouchable Run": "Gain 20+ net tokens in a single weekly slate",
    "⚡ Gridiron Prophet": "Correctly predict 5+ Touchdown Scorers across the season",
    "💎 Diamond Hands": "Survive with fewer than 3 tokens remaining and bounce back to 30+"
}

DEFAULT_QUESTION_TEMPLATES = [
    "Will QB 1 throw for over 250+ passing yards?",
    "Will RB 1 rush for 75+ rushing yards?",
    "Will WR 1 catch 6 or more receptions?",
    "Will Away Team score a touchdown in the 1st quarter?",
    "Will there be a successful 50+ yard Field Goal kicked?",
    "Will this game have over 45.5 combined points scored?",
    "Will any Defense record a pick-six or fumble recovery touchdown?",
    "Will TE 1 score a rushing or receiving touchdown?",
    "Will this game go into Overtime?",
    "Will Home Team record 3 or more sacks?"
]

user_team_color = "#fbbf24"
user_team_logo = "https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg"
if st.session_state.user:
    try:
        res = supabase.table("profiles").select("favorite_team").eq("id", st.session_state.user.id).single().execute()
        if res.data:
            t_name = res.data.get("favorite_team", "🏈 Free Agent / Neutral")
            t_info = NFL_TEAM_DATA.get(t_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
            user_team_color = t_info["color"]
            user_team_logo = t_info["logo"]
    except Exception:
        pass

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Teko:wght@500;700&display=swap');

    .stApp, div[data-testid="stAppViewContainer"] {{
        background: 
            radial-gradient(circle at 50% 20%, rgba(15, 23, 42, 0.88), rgba(7, 13, 25, 0.98)),
            url('{user_team_logo}') center center / 30% no-repeat fixed,
            url('https://images.unsplash.com/photo-1566577739112-5180d4bf9390?auto=format&fit=crop&w=1920&q=80') center center / cover no-repeat fixed !important;
        color: #ffffff !important;
        font-family: 'Teko', sans-serif !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: #030712 !important;
        border-right: 3px solid {user_team_color} !important;
    }}
    
    .nfl-header {{ text-align: center; padding: 10px 0 5px 0; }}
    .nfl-title {{
        font-family: 'Bebas Neue', cursive, sans-serif !important;
        font-size: 72px !important;
        letter-spacing: 5px;
        text-transform: uppercase;
        background: linear-gradient(180deg, #ffffff 15%, {user_team_color} 65%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 25px {user_team_color}88;
        margin: 0;
        line-height: 1.0;
    }}
    .nfl-subtitle {{
        font-family: 'Teko', sans-serif;
        font-size: 24px;
        letter-spacing: 4px;
        color: #93c5fd;
        text-transform: uppercase;
        margin-top: -2px;
    }}
    .header-logo {{
        width: 95px;
        filter: drop-shadow(0px 8px 18px {user_team_color}cc);
    }}
    
    @keyframes teamPulse {{
        0% {{ box-shadow: 0 0 12px {user_team_color}33; }}
        50% {{ box-shadow: 0 0 28px {user_team_color}aa; }}
        100% {{ box-shadow: 0 0 12px {user_team_color}33; }}
    }}

    .big-token-card {{
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.85) 0%, rgba(6, 10, 18, 0.90) 100%);
        padding: 30px;
        border-radius: 18px;
        color: #ffffff !important;
        text-align: center;
        border: 2px solid {user_team_color};
        margin-bottom: 25px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        animation: teamPulse 3.5s infinite ease-in-out;
    }}
    .big-token-number {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 74px;
        letter-spacing: 3px;
        margin: 0;
        color: {user_team_color} !important;
        text-shadow: 0px 4px 18px {user_team_color}88;
    }}

    .champion-card {{
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.9) 0%, rgba(180, 83, 9, 0.9) 50%, rgba(245, 158, 11, 0.9) 100%);
        padding: 30px;
        border-radius: 16px;
        color: #ffffff !important;
        text-align: center;
        border: 3px solid #fbbf24;
        margin-bottom: 30px;
        backdrop-filter: blur(12px);
        animation: teamPulse 2s infinite ease-in-out;
    }}

    .mvp-banner {{
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.88) 0%, rgba(30, 58, 138, 0.92) 100%);
        border: 2px solid #c084fc;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 18px rgba(192, 132, 252, 0.5);
    }}

    .trophy-card-unlocked {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.88) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 2px solid {user_team_color};
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 12px {user_team_color}44;
    }}

    .trophy-card-locked {{
        background: rgba(15, 23, 42, 0.5);
        border: 1px dashed #475569;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        opacity: 0.55;
    }}

    .leaderboard-row {{
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: all 0.25s ease-in-out;
    }}
    .leaderboard-row:hover {{
        transform: translateY(-4px);
        border-color: {user_team_color};
        box-shadow: 0 8px 24px {user_team_color}66;
    }}

    .podium-rank-1 {{
        border: 2px solid #fbbf24 !important;
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4) !important;
    }}
    .podium-rank-2 {{
        border: 2px solid #94a3b8 !important;
        background: linear-gradient(135deg, rgba(148, 163, 184, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
    }}
    .podium-rank-3 {{
        border: 2px solid #b45309 !important;
        background: linear-gradient(135deg, rgba(180, 83, 9, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] > label {{
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin-right: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
        border-color: {user_team_color} !important;
        box-shadow: 0 0 12px {user_team_color}66 !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {{
        background: linear-gradient(135deg, {user_team_color}44 0%, rgba(15,23,42,0.95) 100%) !important;
        border: 2px solid {user_team_color} !important;
        box-shadow: 0 0 15px {user_team_color}bb !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] * {{
        color: #ffffff !important;
        font-weight: 800 !important;
    }}

    .matchup-team-title {{
        font-family: 'Teko', sans-serif;
        font-size: 22px;
        letter-spacing: 1.5px;
        color: #fbbf24;
        text-transform: uppercase;
    }}

    .timer-card {{
        background: rgba(15, 23, 42, 0.92);
        border: 2px solid {user_team_color};
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }}

    .badge-pill {{
        display: inline-block;
        background-color: #1e293b;
        color: {user_team_color};
        border: 1px solid {user_team_color};
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 700;
        margin: 2px;
    }}
    
    .consensus-badge {{
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }}
    
    .chat-bubble {{
        background-color: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }}

    .summary-box {{
        background-color: rgba(15, 23, 42, 0.90) !important;
        backdrop-filter: blur(10px);
        border-left: 5px solid {user_team_color} !important;
        padding: 18px;
        border-radius: 8px;
        color: #f8fafc !important;
        margin-top: 15px;
        border: 1px solid #1e293b;
    }}
    
    .vs-card {{
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        height: 100%;
    }}

    button[data-baseweb="tab"] {{
        background-color: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        margin-right: 6px !important;
    }}
    button[data-baseweb="tab"] * {{
        font-family: 'Teko', sans-serif !important;
        font-size: 20px !important;
        letter-spacing: 1.5px !important;
        color: #cbd5e1 !important;
    }}
    button[aria-selected="true"] {{
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important;
        border: 2px solid {user_team_color} !important;
        box-shadow: 0 4px 18px {user_team_color}77 !important;
    }}
    button[aria-selected="true"] * {{
        color: {user_team_color} !important;
    }}

    div.stButton > button[kind="primary"], div.stFormSubmitButton > button {{
        background: linear-gradient(135deg, {user_team_color} 0%, #d97706 100%) !important;
        color: #000000 !important;
        font-family: 'Teko', sans-serif !important;
        font-size: 24px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease-in-out !important;
    }}
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px {user_team_color}99 !important;
    }}

    .stTextInput > label, .stNumberInput > label, .stRadio > label, .stSelectbox > label {{
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        letter-spacing: 1px;
    }}
    .stTextInput input, .stNumberInput input {{
        background-color: rgba(15, 23, 42, 0.92) !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="nfl-header">
        <img src="https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg" class="header-logo" alt="NFL Logo" />
        <h1 class="nfl-title">TOUCHDOWN TOKENS</h1>
        <div class="nfl-subtitle">Weekly NFL Predictions & Wagers</div>
    </div>
""", unsafe_allow_html=True)
st.write("")

def get_user_badges(target_user_id, check_celebration=False):
    p_data = supabase.table("profiles").select("tokens").eq("id", target_user_id).single().execute().data
    toks = p_data.get("tokens", 0) if p_data else 0
    
    u_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", target_user_id).execute().data
    u_td = supabase.table("touchdown_picks").select("*").eq("user_id", target_user_id).eq("is_correct", True).execute().data
    
    badges = []
    if toks >= 30: badges.append("🚀 Token Tycoon")
    if any(b['wager_amount'] >= 10 for b in u_bets): badges.append("🎯 High Roller")
    if len(u_td) >= 2: badges.append("🏈 TD Guru")
    if len(u_td) >= 3: badges.append("🎯 Sniper")
    if len(u_td) >= 5: badges.append("⚡ Gridiron Prophet")
    if toks == 0: badges.append("📉 Down Bad")
        
    weeks_played = set()
    total_lifetime_won = 0
    weekly_nets = {}
    
    for b in u_bets:
        w_num = b['week_number']
        weeks_played.add(w_num)
        w_ans = b.get("weekly_questions", {}).get("winning_answer")
        if w_num not in weekly_nets: weekly_nets[w_num] = {"gains": 0, "losses": 0, "large_wager_hits": 0}
        if w_ans in ["Yes", "No"]:
            if b['pick'] == w_ans:
                total_lifetime_won += b['wager_amount']
                weekly_nets[w_num]["gains"] += b['wager_amount']
                if b['wager_amount'] >= 5: weekly_nets[w_num]["large_wager_hits"] += 1
            else:
                weekly_nets[w_num]["losses"] += b['wager_amount']
                
    for td in u_td:
        w_num = td['week_number']
        if w_num in weekly_nets: weekly_nets[w_num]["gains"] += 5

    sorted_weeks = sorted(list(weekly_nets.keys()))
    consecutive_oracle_weeks = 0
    for w in sorted_weeks:
        w_slate_bets = [b for b in u_bets if b['week_number'] == w]
        has_large_win = any(b['wager_amount'] >= 5 and b['pick'] == b.get("weekly_questions", {}).get("winning_answer") for b in w_slate_bets)
        if has_large_win:
            consecutive_oracle_weeks += 1
            if consecutive_oracle_weeks >= 4: badges.append("🔮 Oracle of Delphi")
        else:
            consecutive_oracle_weeks = 0

    for w, w_data in weekly_nets.items():
        if (w_data["gains"] - w_data["losses"]) >= 20: badges.append("🔥 Untouchable Run")

    if toks >= 30:
        sim_tokens = 10
        ever_low = False
        for w in sorted_weeks:
            if sim_tokens < 3: ever_low = True
            w_data = weekly_nets[w]
            sim_tokens += (w_data["gains"] - w_data["losses"])
        if ever_low: badges.append("💎 Diamond Hands")

    if len(weeks_played) >= 5: badges.append("🛡️ Iron Defender")
    if total_lifetime_won >= 100: badges.append("💰 Century Club")

    champ_setting = supabase.table("weekly_questions").select("question_text, winning_answer").eq("week_number", 999).execute().data
    if champ_setting and champ_setting[0]["winning_answer"] == "ON":
        champ_name = champ_setting[0]["question_text"]
        user_prof = supabase.table("profiles").select("full_name").eq("id", target_user_id).single().execute().data
        if user_prof and user_prof.get("full_name") == champ_name: badges.append("🏆 League Champion")

    graded_q = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
    if graded_q:
        latest_w = graded_q[0]["week_number"]
        all_latest_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("week_number", latest_w).execute().data
        user_gains, user_loss, user_correct = {}, {}, {}
        for b in all_latest_bets:
            u = b['user_id']
            w_ans = b.get("weekly_questions", {}).get("winning_answer")
            if u not in user_gains:
                user_gains[u], user_loss[u], user_correct[u] = 0, 0, 0
            if w_ans in ["Yes", "No"]:
                if b['pick'] == w_ans:
                    user_gains[u] += b['wager_amount']
                    user_correct[u] += 1
                else:
                    user_loss[u] += b['wager_amount']
        
        if user_gains and max(user_gains.values(), default=-1) > 0 and max(user_gains, key=user_gains.get) == target_user_id:
            badges.append("👑 Weekly High Scorer")
        if user_loss and max(user_loss.values(), default=-1) > 0 and max(user_loss, key=user_loss.get) == target_user_id:
            badges.append("📉 Wall Street Bets")
        if user_correct.get(target_user_id, 0) == 10:
            badges.append("🎯 Perfect 10/10")

    if check_celebration and target_user_id == st.session_state.user.id:
        cache_key = f"seen_badges_{target_user_id}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = badges
        else:
            new_badges = [b for b in badges if b not in st.session_state[cache_key]]
            if new_badges:
                st.balloons()
                for nb in new_badges: st.toast(f"🏆 NEW TROPHY UNLOCKED: {nb}!", icon="🎉")
                st.session_state[cache_key] = badges
    return badges

# ==========================================
# 1. LOGIN & SIGNUP SCREEN
# ==========================================
if st.session_state.user is None:
    tab_login, tab_signup = st.tabs(["🔒 Log In", "📝 Sign Up"])
    
    with tab_login:
        st.subheader("Welcome Back!")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", type="primary", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = res.user
                st.success("Log in successful!")
                st.rerun()
            except Exception as e: st.error(f"Login failed: {e}")

        st.write("")
        with st.expander("🔑 Forgot Password?"):
            st.caption("Enter your email address to receive a password reset link.")
            reset_email = st.text_input("Your Account Email", key="reset_email_input")
            if st.button("Send Reset Link"):
                if reset_email:
                    try:
                        supabase.auth.reset_password_for_email(reset_email)
                        st.success("Password reset email sent! Check your inbox.")
                    except Exception as e: st.error(f"Error sending email: {e}")
                else: st.warning("Please enter your email address.")

    with tab_signup:
        st.subheader("Create a New Account")
        st.caption("New players start with 10 free tokens!")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
        reg_name = st.text_input("Full Name / Display Name", key="reg_name")
        if st.button("Sign Up", type="primary", use_container_width=True):
            if not reg_name: st.warning("Please enter your name.")
            else:
                try:
                    res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                    if res.user:
                        supabase.table("profiles").insert({
                            "id": res.user.id, "email": reg_email, "full_name": reg_name, "tokens": 10,
                            "is_admin": False, "favorite_team": "🏈 Free Agent / Neutral",
                            "bio": "Ready for Kickoff!", "avatar_emoji": "🏈",
                            "avatar_border": "None", "showcase_badges": []
                        }).execute()
                        st.success("Account created successfully! You can now log in.")
                except Exception as e: st.error(f"Sign up failed: {e}")

# ==========================================
# 2. MAIN LOGGED-IN GAME PORTAL
# ==========================================
else:
    user_id = st.session_state.user.id
    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    user_avatar = profile.get("avatar_emoji", "🏈")
    user_border = profile.get("avatar_border", "None")
    user_team = profile.get('favorite_team', '🏈 Free Agent / Neutral')
    team_data = NFL_TEAM_DATA.get(user_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
    
    get_user_badges(user_id, check_celebration=True)

    # --- SIDEBAR (Custom Avatar Border + Info & Logout) ---
    border_css = BORDER_OPTIONS.get(user_border, "border: none;")
    st.sidebar.markdown(f"""
        <div style="display:flex; align-items:center; gap:15px; margin-bottom:15px;">
            <div style="font-size:36px; width:65px; height:65px; display:flex; align-items:center; justify-content:center; border-radius:50%; {border_css} background:rgba(255,255,255,0.05);">
                {user_avatar}
            </div>
            <h2 style="margin:0; font-family:'Bebas Neue', sans-serif;">{profile['full_name']}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.image(team_data["logo"], width=55)
    st.sidebar.caption(f"Team: {user_team}")
    
    weeks_res = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute()
    available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
    
    active_tokens_display = profile['tokens']
    if available_weeks:
        latest_w_active = available_weeks[-1]
        user_active_bets = supabase.table("user_bets").select("wager_amount").eq("user_id", user_id).eq("week_number", latest_w_active).execute().data
        total_wagered_active = sum([b['wager_amount'] for b in user_active_bets]) if user_active_bets else 0
        active_tokens_display = max(0, profile['tokens'] - total_wagered_active)

    st.sidebar.metric(label="Available Tokens", value=f"{active_tokens_display} 🪙", help="Total Tokens minus active wagers placed for the upcoming week.")
    if profile.get("is_admin"): st.sidebar.success("👑 Admin Mode Active")
    st.sidebar.divider()
    if st.sidebar.button("Log Out", use_container_width=True):
        try: supabase.auth.sign_out()
        except Exception: pass
        st.session_state.user = None
        if "supabase_client" in st.session_state: del st.session_state["supabase_client"]
        st.rerun()

    if profile.get("is_admin"):
        tabs = st.tabs(["🏠 Home", "👤 Profile", "📖 Rules", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏛️ Hall of Fame", "⚙️ Admin Control"])
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_hof, tab_admin = tabs
    else:
        tabs = st.tabs(["🏠 Home", "👤 Profile", "📖 Rules", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏛️ Hall of Fame"])
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_hof = tabs

    # ------------------------------------------
    # TAB 0: HOME
    # ------------------------------------------
    with tab_home:
        champ_setting = supabase.table("weekly_questions").select("question_text, winning_answer").eq("week_number", 999).execute().data
        if champ_setting and champ_setting[0]["winning_answer"] == "ON":
            st.balloons()
            champ_name = champ_setting[0]["question_text"]
            st.markdown(f"""
                <div class="champion-card">
                    <div style="font-size: 22px; letter-spacing: 2px; text-transform: uppercase;">🏆 LEAGUE CHAMPION DECLARED 🏆</div>
                    <div style="font-size: 52px; font-weight: 900; margin: 10px 0;">{champ_name}</div>
                    <div style="font-size: 18px;">Congratulations to the Touchdown Tokens Champion! 👑</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"## Welcome back, {profile['full_name']}! 👋")
        st.markdown(f"""
            <div class="big-token-card">
                <div style="font-size: 18px; letter-spacing: 2px; text-transform: uppercase; color: #93c5fd;">Available Balance</div>
                <div class="big-token-number">{active_tokens_display} 🪙</div>
                <div style="font-size: 16px; color: #cbd5e1;">Total Bank: {profile['tokens']} 🪙 (Active Wagers Deducted)</div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("👁️ Your Current Weekly Picks & Share Hub")
        st.caption("Review your active entries for the upcoming week and grab a quick share text for your group chat.")
        
        if not available_weeks:
            st.info("No active weeks available.")
        else:
            view_week = st.selectbox("Select Week to View", available_weeks, index=len(available_weeks)-1, key="home_view_current_week_sel")
            curr_user_bets = supabase.table("user_bets").select("*, weekly_questions(question_number, question_text)").eq("user_id", user_id).eq("week_number", view_week).order("question_id").execute().data
            curr_user_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", view_week).execute().data
            
            if not curr_user_bets and not curr_user_td:
                st.warning(f"You haven't submitted any picks for Week {view_week} yet! Head over to the 'Place Bets' tab.")
            else:
                share_lines = [f"🏈 *{profile['full_name']} - Week {view_week} Lock-Ins* 🏈"]
                for b in curr_user_bets:
                    q_num = b.get("weekly_questions", {}).get("question_number", "?")
                    q_txt = b.get("weekly_questions", {}).get("question_text", "").split(" | MATCHUP: ")[0]
                    pick_val = b["pick"]
                    wager_amt = b["wager_amount"]
                    st.markdown(f"""
                        <div class="summary-box">
                            <b>Q{q_num}: {q_txt}</b><br>
                            • Your Pick: <b style="color:{user_team_color};">{pick_val}</b> | Wager: <b>{wager_amt} 🪙</b>
                        </div>
                    """, unsafe_allow_html=True)
                    share_lines.append(f"Q{q_num}: {pick_val} ({wager_amt} tokens)")
                
                td_name = curr_user_td[0]["player_name"] if curr_user_td else "None"
                st.markdown(f"""
                    <div class="summary-box" style="border-left-color: #38bdf8 !important;">
                        <b>🏈 Touchdown Scorer Bonus Pick:</b><br>
                        • Player: <b style="color:#38bdf8;">{td_name}</b>
                    </div>
                """, unsafe_allow_html=True)
                share_lines.append(f"TD Scorer Pick: {td_name}")
                
                st.write("")
                st.subheader("📋 Group Chat Share Text")
                st.code("\n".join(share_lines), language="markdown")
                st.success("Copy the text box above to share your picks directly into WhatsApp or group chat!")

        graded_q_badge = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
        if graded_q_badge:
            latest_mvp_week = graded_q_badge[0]["week_number"]
            mvp_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("week_number", latest_mvp_week).execute().data
            mvp_tds = supabase.table("touchdown_picks").select("*").eq("week_number", latest_mvp_week).eq("is_correct", True).execute().data
            user_weekly_net = {}
            for b in mvp_bets:
                u = b['user_id']
                w_ans = b.get("weekly_questions", {}).get("winning_answer")
                if u not in user_weekly_net: user_weekly_net[u] = 0
                if w_ans in ["Yes", "No"]:
                    if b['pick'] == w_ans: user_weekly_net[u] += b['wager_amount']
                    else: user_weekly_net[u] -= b['wager_amount']
            for td in mvp_tds:
                u = td['user_id']
                user_weekly_net[u] = user_weekly_net.get(u, 0) + 5
                
            if user_weekly_net and max(user_weekly_net.values(), default=-1) > 0:
                top_mvp_id = max(user_weekly_net, key=user_weekly_net.get)
                top_mvp_tokens = user_weekly_net[top_mvp_id]
                mvp_profile = supabase.table("profiles").select("full_name, avatar_emoji, favorite_team").eq("id", top_mvp_id).single().execute().data
                if mvp_profile:
                    st.markdown(f"""
                        <div class="mvp-banner">
                            <div style="font-size: 16px; letter-spacing: 2px; text-transform: uppercase; color: #f3e8ff;">🔥 Week {latest_mvp_week} League MVP 🔥</div>
                            <div style="font-size: 36px; font-weight: 900; margin: 5px 0; color: #ffffff;">{mvp_profile.get('avatar_emoji', '🏈')} {mvp_profile['full_name']}</div>
                            <div style="font-size: 16px; color: #d8b4fe;">Dominated the slate with <b>+{top_mvp_tokens} Net Tokens</b>! 🚀</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📈 Token History Graph")
        history_bets_all = supabase.table("user_bets").select("week_number, wager_amount, pick, weekly_questions(winning_answer)").eq("user_id", user_id).execute().data
        if history_bets_all:
            week_tokens = {0: 10}
            curr_tokens = 10
            weeks_logged = sorted(list(set([b['week_number'] for b in history_bets_all])))
            for w in weeks_logged:
                w_bets = [b for b in history_bets_all if b['week_number'] == w]
                for b in w_bets:
                    w_ans = b.get("weekly_questions", {}).get("winning_answer")
                    if w_ans in ["Yes", "No"]:
                        if b["pick"] == w_ans: curr_tokens += b["wager_amount"]
                        else: curr_tokens -= b["wager_amount"]
                week_tokens[w] = max(0, curr_tokens)
            st.line_chart(pd.DataFrame(list(week_tokens.items()), columns=["Week", "Tokens"]).set_index("Week"))

    # ------------------------------------------
    # TAB 1: PROFILE & CUSTOMIZATION (With Border & Showcase Badges)
    # ------------------------------------------
    with tab_profile:
        st.header("👤 Profile & Customization")
        st.caption("Personalize your avatar, select a custom border, and choose your top 3 badges to showcase on the leaderboard!")
        
        with st.form("profile_customization_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_display_name = st.text_input("Display Name", value=profile.get("full_name", ""))
                curr_team = profile.get("favorite_team", "🏈 Free Agent / Neutral")
                new_team = st.selectbox("Favorite NFL Team", NFL_TEAMS, index=NFL_TEAMS.index(curr_team) if curr_team in NFL_TEAMS else 0)
                new_bio = st.text_input("Catchphrase / Bio", value=profile.get("bio", "Ready for Kickoff!"), max_chars=100)
            
            with c2:
                curr_avatar = profile.get("avatar_emoji", "🏈")
                new_avatar = st.selectbox("Profile Avatar Emoji", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(curr_avatar) if curr_avatar in AVATAR_OPTIONS else 0)
                
                curr_border = profile.get("avatar_border", "None")
                border_keys = list(BORDER_OPTIONS.keys())
                new_border = st.selectbox("Custom Avatar Border", border_keys, index=border_keys.index(curr_border) if curr_border in border_keys else 0)

            st.divider()
            st.markdown("#### 🏆 Showcase Your Top 3 Badges")
            st.caption("Select up to 3 of your unlocked badges to display prominently next to your name on the leaderboard.")
            
            unlocked_badges = get_user_badges(user_id)
            current_showcase = profile.get("showcase_badges") or []
            valid_showcase = [b for b in current_showcase if b in unlocked_badges][:3]
            
            selected_showcase = st.multiselect(
                "Select Badges to Showcase (Max 3):",
                options=unlocked_badges,
                default=valid_showcase,
                max_selections=3
            )

            if st.form_submit_button("Save Profile Settings 💾", type="primary"):
                if not new_display_name.strip():
                    st.error("Display Name cannot be blank.")
                else:
                    supabase.table("profiles").update({
                        "full_name": new_display_name.strip(),
                        "favorite_team": new_team,
                        "avatar_emoji": new_avatar,
                        "avatar_border": new_border,
                        "bio": new_bio.strip(),
                        "showcase_badges": selected_showcase
                    }).eq("id", user_id).execute()
                    st.success("Profile and visual customizations updated successfully!")
                    st.rerun()

        st.divider()
        st.subheader("🏆 Virtual Trophy Cabinet")
        all_league_profiles = supabase.table("profiles").select("id, full_name, avatar_emoji, favorite_team").execute().data
        user_name_map = {p["full_name"]: p for p in all_league_profiles}
        default_profile_name = profile.get("full_name", list(user_name_map.keys())[0] if user_name_map else "")
        default_index = list(user_name_map.keys()).index(default_profile_name) if default_profile_name in user_name_map else 0
        
        selected_player_name = st.selectbox("Select Player Trophy Showcase", list(user_name_map.keys()), index=default_index, key="trophy_player_select")
        selected_player = user_name_map[selected_player_name]
        selected_badges = get_user_badges(selected_player["id"])
        
        unlocked_count = len(selected_badges)
        total_badges_count = len(MASTER_BADGES)
        st.progress(unlocked_count / total_badges_count, text=f"**Cabinet Completion:** `{int((unlocked_count / total_badges_count) * 100)}%` Unlocked")
        
        t_col1, t_col2 = st.columns(2)
        for idx, (b_name, b_desc) in enumerate(MASTER_BADGES.items()):
            is_unlocked = b_name in selected_badges
            target_col = t_col1 if idx % 2 == 0 else t_col2
            with target_col:
                if is_unlocked:
                    st.markdown(f'<div class="trophy-card-unlocked"><b>{b_name}</b> <span style="color:#fbbf24;">(UNLOCKED)</span><br><small>{b_desc}</small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="trophy-card-locked"><b>🔒 {b_name}</b><br><small>{b_desc}</small></div>', unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: RULES
    # ------------------------------------------
    with tab_rules:
        st.header("📖 Rules & Information")
        st.write("Each week I will release a new form with 10 scenarios. Each player will start with 10 tokens...")

    # ------------------------------------------
    # TAB 3: PLACE BETS
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        if not available_weeks:
            st.info("No active questions available yet.")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            with st.form("weekly_bet_form"):
                wagers, picks = {}, {}
                for q in questions:
                    if q.get("winning_answer", "").startswith("LOCKTIME:"): continue
                    full_q_text = q['question_text']
                    prompt_text = full_q_text.split(" | MATCHUP: ")[0] if " | MATCHUP: " in full_q_text else full_q_text
                    
                    st.markdown(f"**Q{q['question_number']}: {prompt_text}**")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        picks[q['id']] = st.radio(f"Pick Q{q['question_number']}", ["Yes", "No"], key=f"pick_{q['id']}", horizontal=True, label_visibility="collapsed")
                    with col2:
                        wagers[q['id']] = st.number_input(f"Wager Q{q['question_number']}", min_value=0, max_value=profile['tokens'], value=0, key=f"wager_{q['id']}", label_visibility="collapsed")
                
                td_pick = st.text_input("Bonus Touchdown Scorer Pick", value="", key="td_scorer")
                total_wagered = sum(wagers.values())
                
                if total_wagered > profile['tokens']:
                    st.error(f"⚠️ Over-wagered! Allocated {total_wagered} tokens but only have {profile['tokens']} available.")
                
                if st.form_submit_button("Submit Weekly Bets 🚀", type="primary"):
                    if total_wagered <= profile['tokens']:
                        for q_id, pick_val in picks.items():
                            supabase.table("user_bets").delete().eq("user_id", user_id).eq("question_id", q_id).execute()
                            supabase.table("user_bets").insert({"user_id": user_id, "user_name": profile["full_name"], "week_number": selected_week, "question_id": q_id, "pick": pick_val, "wager_amount": wagers[q_id]}).execute()
                        if td_pick:
                            supabase.table("touchdown_picks").delete().eq("user_id", user_id).eq("week_number", selected_week).execute()
                            supabase.table("touchdown_picks").insert({"user_id": user_id, "week_number": selected_week, "player_name": td_pick, "is_correct": None}).execute()
                        st.balloons()
                        st.success("Bets locked in successfully!")

    # ------------------------------------------
    # TAB 4: HISTORY
    # ------------------------------------------
    with tab_history:
        st.header("Your Past Bets & Results")
        history_bets = supabase.table("user_bets").select("*, weekly_questions(question_number, question_text, winning_answer)").eq("user_id", user_id).execute().data
        if history_bets:
            formatted_data = []
            for b in history_bets:
                q_info = b.get("weekly_questions", {})
                w_ans = q_info.get("winning_answer", "Pending")
                raw_q = q_info.get("question_text", "N/A").split(" | MATCHUP: ")[0]
                outcome = "Pending" if w_ans in ["Pending", "LOCKED"] or w_ans.startswith("LOCKTIME:") else (f"✅ Won (+{b['wager_amount'] * 2} Tokens)" if b["pick"] == w_ans else f"❌ Lost (-{b['wager_amount']} Tokens)")
                formatted_data.append({"Week": b["week_number"], "Question": raw_q, "Your Pick": b["pick"], "Wager": b["wager_amount"], "Result": outcome})
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 5: LEADERBOARD & HEAD-TO-HEAD
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 League Standings & Head-to-Head")
        leader_res = supabase.table("profiles").select("*").execute().data
        player_stats = []
        
        if leader_res:
            for p in leader_res:
                correct_tds = supabase.table("touchdown_picks").select("*").eq("user_id", p["id"]).eq("is_correct", True).execute().data
                td_count = len(correct_tds) if correct_tds else 0
                u_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", p["id"]).execute().data
                wins, total_graded = 0, 0
                for b in u_bets:
                    w_ans = b.get("weekly_questions", {}).get("winning_answer")
                    if w_ans in ["Yes", "No"]:
                        total_graded += 1
                        if b["pick"] == w_ans: wins += 1
                win_rate = int((wins / total_graded) * 100) if total_graded > 0 else 0
                player_stats.append({**p, "correct_tds": td_count, "win_rate": win_rate, "total_bets": total_graded})
            
            player_stats = sorted(player_stats, key=lambda x: (-x["tokens"], -x["correct_tds"], x["full_name"]))
            
            # Head-to-Head Rival Comparison
            with st.expander("⚔️ Head-to-Head Player Comparison", expanded=False):
                all_other_names = [p["full_name"] for p in player_stats if p["id"] != user_id]
                if all_other_names:
                    compare_name = st.selectbox("Select Rival to Compare Against:", all_other_names)
                    my_stat = next(p for p in player_stats if p["id"] == user_id)
                    rival_stat = next(p for p in player_stats if p["full_name"] == compare_name)
                    
                    c1, c2, c3 = st.columns([3, 1, 3])
                    with c1:
                        st.markdown(f"""
                        <div class="vs-card">
                            <h3>{my_stat['avatar_emoji']} You ({my_stat['full_name']})</h3>
                            <h2 style="color: {user_team_color};">{my_stat['tokens']} 🪙</h2>
                            <p><b>Win Rate:</b> {my_stat['win_rate']}%</p>
                            <p><b>Correct TDs:</b> {my_stat['correct_tds']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2: st.markdown("<h1 style='text-align:center; margin-top:50px;'>VS</h1>", unsafe_allow_html=True)
                    with c3:
                        r_color = NFL_TEAM_DATA.get(rival_stat.get("favorite_team"), NFL_TEAM_DATA["🏈 Free Agent / Neutral"])["color"]
                        st.markdown(f"""
                        <div class="vs-card">
                            <h3>{rival_stat.get('avatar_emoji','🏈')} {rival_stat['full_name']}</h3>
                            <h2 style="color: {r_color};">{rival_stat['tokens']} 🪙</h2>
                            <p><b>Win Rate:</b> {rival_stat['win_rate']}%</p>
                            <p><b>Correct TDs:</b> {rival_stat['correct_tds']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            st.divider()

            current_rank = 1
            prev_score, prev_tds = None, None
            for idx, p in enumerate(player_stats):
                score, tds = p["tokens"], p["correct_tds"]
                if idx > 0 and score == prev_score and tds == prev_tds: display_rank = current_rank
                else: current_rank, display_rank = idx + 1, idx + 1
                prev_score, prev_tds = score, tds
                
                av = p.get("avatar_emoji") or "🏈"
                p_border = p.get("avatar_border", "None")
                p_border_css = BORDER_OPTIONS.get(p_border, "border: none;")
                team_name = p.get("favorite_team") or "🏈 Free Agent / Neutral"
                t_info = NFL_TEAM_DATA.get(team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                
                showcased = p.get("showcase_badges") or []
                badges_html = "".join([f'<span class="badge-pill">{b}</span>' for b in showcased]) if showcased else '<span style="color:#64748b; font-size:12px;">No Badges Displayed</span>'
                
                podium_class = "leaderboard-row"
                if display_rank == 1: podium_class, rank_display = podium_class + " podium-rank-1", "🥇 #1"
                elif display_rank == 2: podium_class, rank_display = podium_class + " podium-rank-2", "🥈 #2"
                elif display_rank == 3: podium_class, rank_display = podium_class + " podium-rank-3", "🥉 #3"
                else: rank_display = f"#{display_rank}"
                
                st.markdown(f"""
                    <div class="{podium_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span style="font-family: 'Bebas Neue'; font-size: 26px; color: #fbbf24; width: 45px;">{rank_display}</span>
                                <div style="font-size:24px; width:45px; height:45px; display:flex; align-items:center; justify-content:center; border-radius:50%; {p_border_css} background:rgba(255,255,255,0.05);">
                                    {av}
                                </div>
                                <div>
                                    <b style="font-size: 19px; color: #ffffff;">{p['full_name']}</b>
                                    <div style="font-size: 13px; color: #94a3b8;">{team_name} • Correct TDs: <b>{tds}</b></div>
                                </div>
                            </div>
                            <div style="text-align: right;"><span style="font-family: 'Bebas Neue'; font-size: 30px; color: #38bdf8;">{p['tokens']} 🪙</span></div>
                        </div>
                        <div style="border-top: 1px solid #334155; padding-top: 8px; margin-top: 4px;">
                            <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; font-weight: bold; margin-right: 8px;">Showcase:</span> {badges_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 6: HALL OF FAME
    # ------------------------------------------
    with tab_hof:
        st.header("🏛️ Touchdown Tokens Hall of Fame")
        archive_year_sel = st.selectbox("Select Season Archive", ["2024 Season", "2023 Season"])
        if archive_year_sel == "2024 Season":
            st.dataframe(pd.DataFrame([{"Rank": "🥇", "Player": "Louis Lynn", "Final Tokens": 74}, {"Rank": "🥈", "Player": "John Willis", "Final Tokens": 66}]), use_container_width=True, hide_index=True)
        else:
            st.dataframe(pd.DataFrame([{"Rank": "🥇", "Player": "Ed McKenna", "Final Tokens": 117}, {"Rank": "🥈", "Player": "Suzie McKenna", "Final Tokens": 87}]), use_container_width=True, hide_index=True)

    # ------------------------------------------
    # TAB 7: ADMIN CONTROL
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            admin_sec = st.radio("Select Action", ["Manage Questions", "Auto-Lockout Scheduler", "Grade Week & Calculate Points", "Bulk Token Adjuster", "Export League Data (CSV)", "League Chat Announcement", "Archive & Reset Season", "Season Champion Banner"], horizontal=True)
            
            if admin_sec == "Manage Questions":
                st.subheader("📋 Manage & Edit Weekly Questions")
                all_db_weeks = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute().data
                db_week_nums = sorted(list(set([r["week_number"] for r in all_db_weeks]))) if all_db_weeks else []
                next_week = (db_week_nums[-1] + 1) if db_week_nums else 1
                selected_manage_week = st.selectbox("Select Week", db_week_nums + [next_week], index=len(db_week_nums))
                
                if st.button("📋 Load Default Question Templates"):
                    for i in range(1, 11): st.session_state[f"m_prompt_w{selected_manage_week}_q{i}"] = DEFAULT_QUESTION_TEMPLATES[i-1]
                    st.success("Templates loaded!")
                    st.rerun()
                
                with st.form("manage_questions_form"):
                    q_payloads = []
                    for i in range(1, 11):
                        prompt = st.text_input(f"Question {i} Prompt", value=DEFAULT_QUESTION_TEMPLATES[i-1], key=f"m_prompt_w{selected_manage_week}_q{i}")
                        q_payloads.append({"question_number": i, "prompt": prompt})
                    if st.form_submit_button("Save Questions 💾", type="primary"):
                        for item in q_payloads:
                            supabase.table("weekly_questions").insert({"week_number": selected_manage_week, "question_number": item["question_number"], "question_text": item["prompt"], "winning_answer": "Pending"}).execute()
                        st.success("Questions published successfully!")

            elif admin_sec == "Grade Week & Calculate Points":
                st.subheader("Grade Weekly Results")
                grade_week = st.number_input("Week to Grade", min_value=1, max_value=24, step=1)
                week_q = supabase.table("weekly_questions").select("*").eq("week_number", grade_week).order("question_number").execute().data
                
                with st.form("grade_form"):
                    answers = {}
                    for q in week_q:
                        if q.get("question_number", 0) <= 10:
                            answers[q["id"]] = st.selectbox(f"Q{q['question_number']}: {q['question_text']}", ["Pending", "Yes", "No"], key=f"ans_{q['id']}")
                    if st.form_submit_button("Process Payouts 🏆", type="primary"):
                        for q_id, ans in answers.items():
                            supabase.table("weekly_questions").update({"winning_answer": ans}).eq("id", q_id).execute()
                        st.success("Scores graded successfully!")

            elif admin_sec == "Bulk Token Adjuster":
                st.subheader("👥 Bulk Token Adjuster")
                all_profiles_bulk = supabase.table("profiles").select("id, full_name, tokens").execute().data
                with st.form("bulk_form"):
                    selected_users = [p['id'] for p in all_profiles_bulk if st.checkbox(f"{p['full_name']} ({p['tokens']} 🪙)", key=f"bulk_{p['id']}")]
                    val = st.number_input("Token Adjustment Value", value=5)
                    if st.form_submit_button("Apply"):
                        for u_id in selected_users:
                            curr = supabase.table("profiles").select("tokens").eq("id", u_id).single().execute().data.get("tokens", 0)
                            supabase.table("profiles").update({"tokens": curr + val}).eq("id", u_id).execute()
                        st.success("Bulk tokens applied!")

            elif admin_sec == "Export League Data (CSV)":
                st.subheader("📥 Export CSV")
                bets_data = supabase.table("user_bets").select("*").execute().data
                if bets_data: st.download_button("Download All Bets (CSV)", data=pd.DataFrame(bets_data).to_csv(index=False), file_name="bets.csv", mime="text/csv")

            elif admin_sec == "League Chat Announcement":
                st.subheader("📢 Announcement Generator")
                st.code("🏈 WEEK IS LIVE! Place your wagers now!", language="markdown")

            elif admin_sec == "Archive & Reset Season":
                st.subheader("🧹 End-of-Season Reset")
                if st.button("Reset All Users to 10 Tokens"):
                    for p in supabase.table("profiles").select("id").execute().data:
                        supabase.table("profiles").update({"tokens": 10}).eq("id", p["id"]).execute()
                    st.success("Season reset!")

            elif admin_sec == "Season Champion Banner":
                st.subheader("🏆 Champion Banner")
                enable_champ = st.toggle("Enable Champion Banner")
                if st.button("Save Banner"):
                    supabase.table("weekly_questions").delete().eq("week_number", 999).execute()
                    supabase.table("weekly_questions").insert({"week_number": 999, "question_number": 1, "question_text": "Champion", "winning_answer": "ON" if enable_champ else "OFF"}).execute()
                    st.success("Banner updated!")
