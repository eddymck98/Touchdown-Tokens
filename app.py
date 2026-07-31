import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

st.set_page_config(page_title="Touchdown Tokens", page_icon="🏈", layout="centered")

# ==========================================
# SUPABASE CONFIGURATION (SESSION ISOLATED)
# ==========================================
def get_supabase_client() -> Client:
    if "supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state.supabase_client = create_client(url, key)
    return st.session_state.supabase_client

supabase = get_supabase_client()

# ==========================================
# AUTHENTICATION STATE & PERSISTENCE
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
    try:
        current_session = supabase.auth.get_session()
        if current_session and current_session.user:
            st.session_state.user = current_session.user
    except Exception:
        pass

# ==========================================
# STATIC DATA & CUSTOMIZATION DICTIONARIES
# ==========================================
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

BORDER_STYLES = {
    "Classic Team Solid": "2px solid {color}",
    "Neon Glow Pulse": "2px solid {color}; box-shadow: 0 0 15px {color}aa;",
    "Gold Champion Ring": "3px solid #fbbf24; box-shadow: 0 0 15px #fbbf24aa;",
    "Dotted Challenger": "2px dotted {color};",
    "Stealth Midnight": "2px solid #475569;"
}

BACKGROUND_THEMES = {
    "Stadium Floodlights (Default)": "https://images.unsplash.com/photo-1566577739112-5180d4bf9390?auto=format&fit=crop&w=1920&q=80",
    "Midnight Turf": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1920&q=80",
    "Cyber Gridiron": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1920&q=80",
    "Gameday Tailgate": "https://images.unsplash.com/photo-1521412644187-c49fa049e84d?auto=format&fit=crop&w=1920&q=80"
}

PROFILE_SKINS = {
    "Standard Slate": "linear-gradient(135deg, rgba(30, 41, 59, 0.88) 0%, rgba(15, 23, 42, 0.92) 100%)",
    "Gold Gridiron (Req: 30+ Tokens)": "linear-gradient(135deg, rgba(180, 83, 9, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%)",
    "Midnight Stealth": "linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%)",
    "Hall of Famer (Champion)": "linear-gradient(135deg, rgba(251, 191, 36, 0.3) 0%, rgba(15, 23, 42, 0.95) 100%)"
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
bg_url = BACKGROUND_THEMES["Stadium Floodlights (Default)"]
avatar_border_css = "2px solid #fbbf24"
profile_skin_css = PROFILE_SKINS["Standard Slate"]

if st.session_state.user:
    try:
        res = supabase.table("profiles").select("favorite_team, bg_theme, border_style, profile_skin").eq("id", st.session_state.user.id).single().execute()
        if res.data:
            t_name = res.data.get("favorite_team", "🏈 Free Agent / Neutral")
            t_info = NFL_TEAM_DATA.get(t_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
            user_team_color = t_info["color"]
            user_team_logo = t_info["logo"]
            
            bg_choice = res.data.get("bg_theme")
            if bg_choice in BACKGROUND_THEMES:
                bg_url = BACKGROUND_THEMES[bg_choice]
                
            b_choice = res.data.get("border_style")
            if b_choice in BORDER_STYLES:
                avatar_border_css = BORDER_STYLES[b_choice].format(color=user_team_color)
                
            skin_choice = res.data.get("profile_skin")
            if skin_choice in PROFILE_SKINS:
                profile_skin_css = PROFILE_SKINS[skin_choice]
    except Exception:
        pass

# ==========================================
# ADVANCED CSS & GLASSMORPHISM STYLING
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&family=Teko:wght@500;700&display=swap');

    .stApp, div[data-testid="stAppViewContainer"] {{
        background: 
            radial-gradient(circle at 50% 20%, rgba(15, 23, 42, 0.88), rgba(7, 13, 25, 0.98)),
            url('{user_team_logo}') center center / 30% no-repeat fixed,
            url('{bg_url}') center center / cover no-repeat fixed !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    h1, h2, h3, .bebas-text {{
        font-family: 'Bebas Neue', cursive, sans-serif !important;
        letter-spacing: 1.5px;
    }}
    
    .teko-text {{
        font-family: 'Teko', sans-serif !important;
        letter-spacing: 2px;
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

    /* CSS Glassmorphism Standard Cards */
    .glass-card {{
        background: {profile_skin_css};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    /* Sticky Balance Header Bar */
    .sticky-balance-bar {{
        position: sticky;
        top: 50px;
        z-index: 9999;
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid {user_team_color};
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.6);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    /* Custom Avatar Circle */
    .avatar-circle {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        font-size: 24px;
        background: rgba(15, 23, 42, 0.8);
        {avatar_border_css}
    }}

    /* Stat Pills */
    .stat-pill {{
        display: inline-block;
        background-color: rgba(30, 41, 59, 0.9);
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 16px;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 6px;
    }}

    .badge-pill {{
        display: inline-block;
        background-color: #1e293b;
        color: {user_team_color};
        border: 1px solid {user_team_color};
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 700;
        margin: 2px;
    }}

    .leaderboard-row {{
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: all 0.25s ease-in-out;
    }}

    .summary-box {{
        background-color: rgba(15, 23, 42, 0.90) !important;
        backdrop-filter: blur(10px);
        border-left: 5px solid {user_team_color} !important;
        padding: 16px;
        border-radius: 8px;
        color: #f8fafc !important;
        margin-top: 12px;
        border: 1px solid #1e293b;
    }}

    button[data-baseweb="tab"] {{
        background-color: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
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
        font-size: 22px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 8px !important;
        border: none !important;
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

# ==========================================
# HELPER FUNCTIONS & CALCULATORS
# ==========================================
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
        if w_num not in weekly_nets:
            weekly_nets[w_num] = {"gains": 0, "losses": 0}
        if w_ans in ["Yes", "No"]:
            if b['pick'] == w_ans:
                total_lifetime_won += b['wager_amount']
                weekly_nets[w_num]["gains"] += b['wager_amount']
            else:
                weekly_nets[w_num]["losses"] += b['wager_amount']
                
    for td in u_td:
        w_num = td['week_number']
        if w_num in weekly_nets: weekly_nets[w_num]["gains"] += 5

    for w, w_data in weekly_nets.items():
        if (w_data["gains"] - w_data["losses"]) >= 20: badges.append("🔥 Untouchable Run")

    if len(weeks_played) >= 5: badges.append("🛡️ Iron Defender")
    if total_lifetime_won >= 100: badges.append("💰 Century Club")

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

def compute_user_stats(target_user_id):
    bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", target_user_id).execute().data
    tds = supabase.table("touchdown_picks").select("*").eq("user_id", target_user_id).eq("is_correct", True).execute().data
    
    total_bets = 0
    correct_bets = 0
    weekly_outcomes = {}
    
    for b in bets:
        w_ans = b.get("weekly_questions", {}).get("winning_answer")
        w_num = b["week_number"]
        if w_num not in weekly_outcomes: weekly_outcomes[w_num] = 0
        if w_ans in ["Yes", "No"]:
            total_bets += 1
            if b["pick"] == w_ans:
                correct_bets += 1
                weekly_outcomes[w_num] += b["wager_amount"]
            else:
                weekly_outcomes[w_num] -= b["wager_amount"]
                
    win_rate = int((correct_bets / total_bets) * 100) if total_bets > 0 else 0
    td_hits = len(tds) if tds else 0
    
    sorted_weeks = sorted(list(weekly_outcomes.keys()))
    streak_count = 0
    streak_type = "🔥"
    for w in reversed(sorted_weeks):
        net = weekly_outcomes[w]
        if streak_count == 0:
            streak_type = "🔥" if net >= 0 else "🧊"
            streak_count += 1
        else:
            if (streak_type == "🔥" and net >= 0) or (streak_type == "🧊" and net < 0):
                streak_count += 1
            else:
                break
                
    streak_str = f"{streak_type} {streak_count}W" if streak_type == "🔥" else f"{streak_type} {streak_count}L"
    if not sorted_weeks: streak_str = "🔥 0W"
    
    all_other_bets = supabase.table("user_bets").select("user_id, user_name, question_id, pick").neq("user_id", target_user_id).execute().data
    user_pick_map = {b["question_id"]: b["pick"] for b in bets}
    
    conflict_counts = {}
    for ob in all_other_bets:
        q_id = ob["question_id"]
        other_name = ob["user_name"]
        if q_id in user_pick_map:
            if ob["pick"] != user_pick_map[q_id]:
                conflict_counts[other_name] = conflict_counts.get(other_name, 0) + 1
                
    nemesis_name = max(conflict_counts, key=conflict_counts.get) if conflict_counts else "None (No Opponents)"
    
    return {
        "win_rate": win_rate,
        "td_hits": td_hits,
        "streak_str": streak_str,
        "nemesis_name": nemesis_name
    }

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
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab_signup:
        st.subheader("Create a New Account")
        st.caption("New players start with 10 free tokens!")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
        reg_name = st.text_input("Full Name / Display Name", key="reg_name")
        
        if st.button("Sign Up", type="primary", use_container_width=True):
            if not reg_name:
                st.warning("Please enter your name.")
            else:
                try:
                    res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                    if res.user:
                        supabase.table("profiles").insert({
                            "id": res.user.id,
                            "email": reg_email,
                            "full_name": reg_name,
                            "tokens": 10,
                            "is_admin": False,
                            "favorite_team": "🏈 Free Agent / Neutral",
                            "favorite_player": "Patrick Mahomes",
                            "bio": "Ready for Kickoff!",
                            "avatar_emoji": "🏈",
                            "bg_theme": "Stadium Floodlights (Default)",
                            "border_style": "Classic Team Solid",
                            "profile_skin": "Standard Slate",
                            "featured_badges": []
                        }).execute()
                        st.success("Account created successfully! You can now log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

# ==========================================
# 2. MAIN LOGGED-IN GAME PORTAL
# ==========================================
else:
    user_id = st.session_state.user.id
    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    user_avatar = profile.get("avatar_emoji", "🏈")
    user_team = profile.get('favorite_team', '🏈 Free Agent / Neutral')
    fav_player = profile.get('favorite_player', 'Patrick Mahomes')
    team_data = NFL_TEAM_DATA.get(user_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
    
    get_user_badges(user_id, check_celebration=True)

    # --- SIDEBAR ---
    st.sidebar.title(f"{user_avatar} {profile['full_name']}")
    st.sidebar.image(team_data["logo"], width=50)
    st.sidebar.caption(f"Team: {user_team} | Star: ⭐ {fav_player}")
    
    weeks_res = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute()
    available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
    
    active_tokens_display = profile['tokens']
    if available_weeks:
        latest_w_active = available_weeks[-1]
        user_active_bets = supabase.table("user_bets").select("wager_amount").eq("user_id", user_id).eq("week_number", latest_w_active).execute().data
        total_wagered_active = sum([b['wager_amount'] for b in user_active_bets]) if user_active_bets else 0
        active_tokens_display = max(0, profile['tokens'] - total_wagered_active)

    st.sidebar.metric(label="Available Tokens", value=f"{active_tokens_display} 🪙")
    
    if profile.get("is_admin"): st.sidebar.success("👑 Admin Mode Active")
        
    st.sidebar.divider()
    if st.sidebar.button("Log Out", use_container_width=True):
        try: supabase.auth.sign_out()
        except Exception: pass
        st.session_state.user = None
        if "supabase_client" in st.session_state: del st.session_state["supabase_client"]
        st.rerun()

    # --- NAVIGATION TABS ---
    if profile.get("is_admin"):
        tab_home, tab_profile, tab_rules, tab_bet, tab_leaders, tab_admin = st.tabs(
            ["🏠 Home", "👤 Profile & Skins", "📖 Rules", "🎯 Place Bets", "🏆 Standings & HoF", "⚙️ Admin Control"]
        )
    else:
        tab_home, tab_profile, tab_rules, tab_bet, tab_leaders = st.tabs(
            ["🏠 Home", "👤 Profile & Skins", "📖 Rules", "🎯 Place Bets", "🏆 Standings & HoF"]
        )

    # ------------------------------------------
    # TAB 0: HOME
    # ------------------------------------------
    with tab_home:
        st.markdown(f"## Welcome back, {profile['full_name']}! 👋")
        
        st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size: 16px; letter-spacing: 2px; text-transform: uppercase; color: #93c5fd;">Available Balance</div>
                <div style="font-family: 'Bebas Neue'; font-size: 68px; color: {user_team_color};">{active_tokens_display} 🪙</div>
                <div style="font-size: 14px; color: #cbd5e1;">Total Bank: {profile['tokens']} 🪙 (Active Wagers Deducted)</div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("👁️ Your Active Lock-Ins & Group Chat Share Hub")
        
        if not available_weeks:
            st.info("No active weeks available.")
        else:
            view_week = st.selectbox("Select Week to View", available_weeks, index=len(available_weeks)-1, key="home_view_current_week_sel")
            
            curr_user_bets = supabase.table("user_bets").select("*, weekly_questions(question_number, question_text)").eq("user_id", user_id).eq("week_number", view_week).order("question_id").execute().data
            curr_user_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", view_week).execute().data
            
            if not curr_user_bets and not curr_user_td:
                st.warning(f"You haven't submitted any picks for Week {view_week} yet! Head over to 'Place Bets'.")
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

    # ------------------------------------------
    # TAB 1: PROFILE, SKINS & CUSTOMIZATION
    # ------------------------------------------
    with tab_profile:
        st.header("👤 Profile Customization & Identity Skins")
        
        with st.form("profile_customization_form"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                new_display_name = st.text_input("Display Name", value=profile.get("full_name", ""))
                curr_team = profile.get("favorite_team", "🏈 Free Agent / Neutral")
                new_team = st.selectbox("Favorite NFL Team", NFL_TEAMS, index=NFL_TEAMS.index(curr_team) if curr_team in NFL_TEAMS else 0)
                new_fav_player = st.text_input("Favorite NFL Player / Legend", value=profile.get("favorite_player", "Patrick Mahomes"))
                new_bio = st.text_input("Profile Bio / Catchphrase", value=profile.get("bio", "Ready for Kickoff!"), max_chars=100)
            
            with col_p2:
                curr_avatar = profile.get("avatar_emoji", "🏈")
                new_avatar = st.selectbox("Avatar Emoji", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(curr_avatar) if curr_avatar in AVATAR_OPTIONS else 0)
                
                curr_b = profile.get("border_style", "Classic Team Solid")
                b_keys = list(BORDER_STYLES.keys())
                new_border = st.selectbox("Avatar Border Style", b_keys, index=b_keys.index(curr_b) if curr_b in b_keys else 0)
                
                curr_bg = profile.get("bg_theme", "Stadium Floodlights (Default)")
                bg_keys = list(BACKGROUND_THEMES.keys())
                new_bg = st.selectbox("App Background Theme", bg_keys, index=bg_keys.index(curr_bg) if curr_bg in bg_keys else 0)
                
                curr_skin = profile.get("profile_skin", "Standard Slate")
                skin_keys = list(PROFILE_SKINS.keys())
                new_skin = st.selectbox("Profile Card Skin Unlock", skin_keys, index=skin_keys.index(curr_skin) if curr_skin in skin_keys else 0)

            st.divider()
            st.markdown("#### 🏆 Showcase Top 3 Badges on Leaderboard")
            unlocked_b = get_user_badges(user_id)
            existing_featured = profile.get("featured_badges") or []
            selected_featured = st.multiselect("Select up to 3 unlocked badges:", options=unlocked_b, default=[b for b in existing_featured if b in unlocked_b][:3], max_selections=3)

            save_profile = st.form_submit_button("Save All Settings 💾", type="primary", use_container_width=True)
            
            if save_profile:
                if "Gold Gridiron" in new_skin and profile["tokens"] < 30:
                    st.error("Gold Gridiron Skin requires a 30+ Token Balance!")
                else:
                    supabase.table("profiles").update({
                        "full_name": new_display_name.strip(),
                        "favorite_team": new_team,
                        "favorite_player": new_fav_player.strip(),
                        "avatar_emoji": new_avatar,
                        "bio": new_bio.strip(),
                        "border_style": new_border,
                        "bg_theme": new_bg,
                        "profile_skin": new_skin,
                        "featured_badges": selected_featured
                    }).eq("id", user_id).execute()
                    st.success("Profile customization updated!")
                    st.rerun()

        st.divider()
        st.subheader("📜 Your Past Wagers & Results")
        history_bets = supabase.table("user_bets").select("*, weekly_questions(question_number, question_text, winning_answer)").eq("user_id", user_id).execute().data
        if history_bets:
            formatted_data = []
            for b in history_bets:
                q_info = b.get("weekly_questions", {})
                w_ans = q_info.get("winning_answer", "Pending")
                raw_q_text = q_info.get("question_text", "N/A")
                clean_q_prompt = raw_q_text.split(" | MATCHUP: ")[0] if " | MATCHUP: " in raw_q_text else raw_q_text
                
                if w_ans in ["Pending", "LOCKED"] or w_ans.startswith("LOCKTIME:"): outcome = "Pending"
                elif b["pick"] == w_ans: outcome = f"✅ Won (+{b['wager_amount'] * 2})"
                else: outcome = f"❌ Lost (-{b['wager_amount']})"
                        
                formatted_data.append({"Week": b["week_number"], "Question": clean_q_prompt, "Pick": b["pick"], "Wager": b["wager_amount"], "Winner": w_ans, "Result": outcome})
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 2: RULES & INFO
    # ------------------------------------------
    with tab_rules:
        st.header("📖 Official Game Rules")
        st.markdown("""
        1. 🪙 **Wager Limits:** Don't go over your current total token balance.
        2. 🎯 **One Choice Per Question:** You must only place a bet on 1 option (`Yes` or `No`) per question.
        3. ⏰ **Submission Cutoff:** Cutoff is **15 minutes before 1st kickoff** on Sunday.
        4. 🏈 **Touchdown Scorer Eligibility:** Must either **rush or receive** a touchdown. Passing TDs do NOT count!
        """)

    # ------------------------------------------
    # TAB 3: PLACE BETS (MODERN CARDS & STICKY BAR)
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        
        if not available_weeks:
            st.info("No active questions available yet.")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            is_locked = any(q.get("winning_answer") == "LOCKED" for q in questions)
            all_week_bets = supabase.table("user_bets").select("question_id, pick, wager_amount").eq("user_id", user_id).eq("week_number", selected_week).execute().data

            # STICKY COMPACT BALANCE BAR
            st.markdown(f"""
                <div class="sticky-balance-bar">
                    <div>
                        <span style="font-family:'Teko'; font-size: 22px; color:#cbd5e1;">WEEK {selected_week} SLATE</span>
                    </div>
                    <div>
                        <span style="font-family:'Bebas Neue'; font-size: 26px; color:{user_team_color};">AVAILABLE: {active_tokens_display} / {profile['tokens']} 🪙</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("weekly_bet_form_modern"):
                wagers = {}
                picks = {}
                
                for q in questions:
                    if q.get("winning_answer", "").startswith("LOCKTIME:"): continue
                    
                    full_q_text = q['question_text']
                    away_team_name = "🏈 Neutral"
                    home_team_name = "🏈 Neutral"
                    prompt_text = full_q_text
                    
                    if " | MATCHUP: " in full_q_text:
                        parts = full_q_text.split(" | MATCHUP: ")
                        prompt_text = parts[0]
                        if " @ " in parts[1]:
                            teams_split = parts[1].split(" @ ")
                            away_team_name = teams_split[0]
                            home_team_name = teams_split[1]

                    existing_bet_row = [b for b in all_week_bets if b.get('question_id') == q['id']]
                    default_pick_val = existing_bet_row[0]['pick'] if existing_bet_row else "Yes"
                    default_wager_val = existing_bet_row[0]['wager_amount'] if existing_bet_row else 0

                    # MODERN BET CARD LAYOUT
                    st.markdown(f"""
                        <div class="glass-card" style="padding: 14px; margin-bottom: 10px;">
                            <div style="font-size: 12px; color: #94a3b8; font-weight: bold;">Q{q['question_number']} • {away_team_name} @ {home_team_name}</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ffffff; margin: 4px 0;">{prompt_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    col_p, col_w = st.columns([1, 1])
                    with col_p:
                        picks[q['id']] = st.radio(
                            f"Pick Q{q['question_number']}", ["Yes", "No"], 
                            index=0 if default_pick_val == "Yes" else 1, key=f"p_{q['id']}", horizontal=True, disabled=is_locked
                        )
                    with col_w:
                        wagers[q['id']] = st.number_input(
                            f"Wager Q{q['question_number']}", min_value=0, max_value=profile['tokens'], value=default_wager_val, key=f"w_{q['id']}", disabled=is_locked
                        )

                st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                existing_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", selected_week).execute().data
                default_td = existing_td[0]["player_name"] if existing_td else ""
                td_pick = st.text_input("Player Name (Rushing/Receiving Only)", value=default_td, key="td_scorer", disabled=is_locked)
                
                total_wagered = sum(wagers.values())
                if total_wagered > profile['tokens']:
                    st.error(f"⚠️ Over-wagered! Allocated {total_wagered} tokens but only have {profile['tokens']} available.")

                submit_bet = st.form_submit_button("Submit Lock-In Wagers 🚀", type="primary", use_container_width=True, disabled=is_locked)
                
                if submit_bet and not is_locked:
                    if total_wagered <= profile['tokens']:
                        for q_id, pick_val in picks.items():
                            w_amt = wagers[q_id]
                            supabase.table("user_bets").delete().eq("user_id", user_id).eq("question_id", q_id).execute()
                            supabase.table("user_bets").insert({
                                "user_id": user_id, "user_name": profile["full_name"], "week_number": selected_week, "question_id": q_id, "pick": pick_val, "wager_amount": w_amt
                            }).execute()
                        if td_pick:
                            supabase.table("touchdown_picks").delete().eq("user_id", user_id).eq("week_number", selected_week).execute()
                            supabase.table("touchdown_picks").insert({"user_id": user_id, "week_number": selected_week, "player_name": td_pick, "is_correct": None}).execute()
                        st.balloons()
                        st.success("Bets locked in successfully!")

    # ------------------------------------------
    # TAB 4: STANDINGS, COMPARISONS, NEMESIS & HOF
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 League Standings & Comparison Hub")
        
        leader_res = supabase.table("profiles").select("*").execute().data
        
        if leader_res:
            # --- SIDE-BY-SIDE PLAYER RESULTS COMPARISON ---
            with st.expander("⚔️ Side-by-Side Head-to-Head Player Comparison", expanded=False):
                st.caption("Select any player to compare your win rates, streaks, and nemeses side-by-side.")
                all_player_names = [p["full_name"] for p in leader_res]
                comp_player_name = st.selectbox("Choose Player to Compare Against:", [n for n in all_player_names if n != profile["full_name"]])
                
                comp_p_data = [p for p in leader_res if p["full_name"] == comp_player_name][0]
                
                u_stats = compute_user_stats(user_id)
                c_stats = compute_user_stats(comp_p_data["id"])
                
                col_u, col_vs, col_c = st.columns([2, 1, 2])
                with col_u:
                    st.markdown(f"### You ({profile['full_name']})")
                    st.write(f"🪙 Tokens: **{profile['tokens']}**")
                    st.write(f"📈 Win Rate: **{u_stats['win_rate']}%**")
                    st.write(f"🏈 TD Hits: **{u_stats['td_hits']}**")
                    st.write(f"Streak: **{u_stats['streak_str']}**")
                    st.write(f"😈 Nemesis: **{u_stats['nemesis_name']}**")
                with col_vs:
                    st.markdown("<h2 style='text-align:center; padding-top:20px;'>VS</h2>", unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"### {comp_p_data['full_name']}")
                    st.write(f"🪙 Tokens: **{comp_p_data['tokens']}**")
                    st.write(f"📈 Win Rate: **{c_stats['win_rate']}%**")
                    st.write(f"🏈 TD Hits: **{c_stats['td_hits']}**")
                    st.write(f"Streak: **{c_stats['streak_str']}**")
                    st.write(f"😈 Nemesis: **{c_stats['nemesis_name']}**")

            st.divider()
            st.subheader("📊 Official Standings")

            for idx, p in enumerate(sorted(leader_res, key=lambda x: -x["tokens"])):
                p_stats = compute_user_stats(p["id"])
                p_team = p.get("favorite_team", "🏈 Free Agent / Neutral")
                t_info = NFL_TEAM_DATA.get(p_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                
                # STAT PILLS & FEATURED BADGES
                feat_b = p.get("featured_badges") or []
                badge_html = "".join([f'<span class="badge-pill">{b}</span>' for b in feat_b]) if feat_b else '<span style="color:#64748b; font-size:11px;">No Featured Badges</span>'
                
                b_style = BORDER_STYLES.get(p.get("border_style"), "2px solid #fbbf24").format(color=t_info["color"])

                st.markdown(f"""
                    <div class="leaderboard-row">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span style="font-family: 'Bebas Neue'; font-size: 28px; color: #fbbf24;">#{idx+1}</span>
                                <div class="avatar-circle" style="{b_style}">{p.get('avatar_emoji', '🏈')}</div>
                                <div>
                                    <b style="font-size: 18px; color: #ffffff;">{p['full_name']}</b> <small style="color:#94a3b8;">({p_team})</small><br>
                                    <span class="stat-pill">{p_stats['win_rate']}% Win Rate</span>
                                    <span class="stat-pill">{p_stats['td_hits']} TD Hits</span>
                                    <span class="stat-pill">Streak: {p_stats['streak_str']}</span>
                                    <span class="stat-pill" style="border-color:#f43f5e; color:#fda4af;">😈 Nemesis: {p_stats['nemesis_name']}</span>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-family: 'Bebas Neue'; font-size: 32px; color: #38bdf8;">{p['tokens']} 🪙</span>
                            </div>
                        </div>
                        <div style="border-top: 1px solid #334155; padding-top: 6px; margin-top: 8px;">
                            <span style="font-size: 11px; text-transform: uppercase; color: #94a3b8; font-weight: bold;">Showcase:</span> {badge_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        # --- HALL OF FAME EMBEDDED AT BOTTOM OF LEADERBOARD ---
        st.subheader("🏛️ Hall of Fame & Historical Archives")
        st.caption("Archive of past champions and legendary historical seasons.")
        
        hof_year = st.selectbox("Select Historical Season Archive:", ["2024 Season", "2023 Season"])
        if hof_year == "2024 Season":
            st.markdown("""
                <div class="glass-card" style="text-align:center;">
                    <div style="font-size:18px; color:#fbbf24;">👑 2024 CHAMPION: Louis Lynn (74 🪙)</div>
                </div>
            """, unsafe_allow_html=True)
            df_2024 = pd.DataFrame([
                {"Rank": "🥇", "Player": "Louis Lynn", "Final Tokens": 74},
                {"Rank": "🥈", "Player": "John Willis", "Final Tokens": 66},
                {"Rank": "🥉", "Player": "Will Granger", "Final Tokens": 29},
                {"Rank": "3rd (Tied)", "Player": "Adam Volpin", "Final Tokens": 29},
                {"Rank": "5th", "Player": "Gary Shaw", "Final Tokens": 23},
                {"Rank": "6th", "Player": "Suzie McKenna", "Final Tokens": 21},
                {"Rank": "7th", "Player": "Dan Hammerton", "Final Tokens": 14},
                {"Rank": "7th (Tied)", "Player": "Tom Wood", "Final Tokens": 14},
                {"Rank": "9th", "Player": "Patrick Smith", "Final Tokens": 13},
                {"Rank": "10th", "Player": "Joe Kewley-Joy", "Final Tokens": 10},
                {"Rank": "11th", "Player": "Paul Hindle", "Final Tokens": 6},
                {"Rank": "12th", "Player": "Liam Murphy", "Final Tokens": 0}
            ])
            st.dataframe(df_2024, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
                <div class="glass-card" style="text-align:center;">
                    <div style="font-size:18px; color:#fbbf24;">👑 2023 CHAMPION: Ed McKenna (117 🪙)</div>
                </div>
            """, unsafe_allow_html=True)
            df_2023 = pd.DataFrame([
                {"Rank": "🥇", "Player": "Ed McKenna", "Final Tokens": 117},
                {"Rank": "🥈", "Player": "Suzie McKenna", "Final Tokens": 87},
                {"Rank": "🥉", "Player": "Gary Shaw", "Final Tokens": 76},
                {"Rank": "4th", "Player": "Adam Volpin", "Final Tokens": 67},
                {"Rank": "5th", "Player": "Tom Wood", "Final Tokens": 49},
                {"Rank": "6th", "Player": "Jay Kewley-Joy", "Final Tokens": 48},
                {"Rank": "7th", "Player": "Will Granger", "Final Tokens": 47},
                {"Rank": "8th", "Player": "John Willis", "Final Tokens": 28},
                {"Rank": "9th", "Player": "Patrick Smith", "Final Tokens": 4},
                {"Rank": "10th", "Player": "Ethan Lewis", "Final Tokens": 3}
            ])
            st.dataframe(df_2023, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # TAB 5: ADMIN CONTROL
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            
            admin_sec = st.radio("Select Action", ["Manage Questions", "Auto-Lockout Scheduler", "Grade Week & Calculate Points", "Bulk Token Adjuster", "Export League Data (CSV)", "League Chat Announcement", "Archive & Reset Season", "Season Champion Banner"], horizontal=True)
            
            if admin_sec == "Manage Questions":
                st.subheader("📋 Manage & Edit Weekly Questions & Matchups")
                
                all_db_weeks = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute().data
                db_week_nums = sorted(list(set([r["week_number"] for r in all_db_weeks]))) if all_db_weeks else []
                next_suggested_week = (db_week_nums[-1] + 1) if db_week_nums else 1
                
                week_options = db_week_nums + [next_suggested_week] if next_suggested_week not in db_week_nums else db_week_nums
                selected_manage_week = st.selectbox("Select Week to Manage", week_options, index=len(week_options)-1, key="admin_manage_week_sel")
                
                existing_week_qs = supabase.table("weekly_questions").select("*").eq("week_number", selected_manage_week).order("question_number").execute().data
                real_existing_qs = {q["question_number"]: q for q in existing_week_qs if q.get("question_number", 0) <= 10}
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    if st.button("📋 Load 10 Default Question Templates"):
                        for i in range(1, 11):
                            st.session_state[f"m_prompt_w{selected_manage_week}_q{i}"] = DEFAULT_QUESTION_TEMPLATES[i-1]
                        st.success("Default templates loaded instantly!")
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Clear Unpublished Questions"):
                        try:
                            supabase.table("weekly_questions").delete().eq("week_number", selected_manage_week).eq("winning_answer", "Pending").execute()
                            for i in range(1, 11):
                                skey = f"m_prompt_w{selected_manage_week}_q{i}"
                                if skey in st.session_state:
                                    del st.session_state[skey]
                            st.success(f"Cleared unpublished questions for Week {selected_manage_week}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error clearing questions: {e}")

                with st.form(key=f"manage_questions_form_week_{selected_manage_week}"):
                    question_payloads = []
                    
                    for i in range(1, 11):
                        st.markdown(f"#### Question {i}")
                        
                        q_obj = real_existing_qs.get(i, {})
                        raw_txt = q_obj.get("question_text", "")
                        
                        db_prompt = raw_txt.split(" | MATCHUP: ")[0] if " | MATCHUP: " in raw_txt else raw_txt
                        session_key = f"m_prompt_w{selected_manage_week}_q{i}"
                        
                        existing_prompt = st.session_state.get(session_key, db_prompt)
                            
                        existing_away = "🏈 Free Agent / Neutral"
                        existing_home = "🏈 Free Agent / Neutral"
                        
                        if " | MATCHUP: " in raw_txt:
                            matchup_part = raw_txt.split(" | MATCHUP: ")[1]
                            if " @ " in matchup_part:
                                split_teams = matchup_part.split(" @ ")
                                existing_away = split_teams[0] if split_teams[0] in NFL_TEAMS else "🏈 Free Agent / Neutral"
                                existing_home = split_teams[1] if split_teams[1] in NFL_TEAMS else "🏈 Free Agent / Neutral"

                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            away_t = st.selectbox(f"Q{i} Away Team", NFL_TEAMS, index=NFL_TEAMS.index(existing_away) if existing_away in NFL_TEAMS else 0, key=f"m_away_w{selected_manage_week}_q{i}")
                        with col_m2:
                            home_t = st.selectbox(f"Q{i} Home Team", NFL_TEAMS, index=NFL_TEAMS.index(existing_home) if existing_home in NFL_TEAMS else 0, key=f"m_home_w{selected_manage_week}_q{i}")
                            
                        prompt_val = st.text_input(f"Question {i} Prompt", value=existing_prompt, key=session_key)
                        
                        question_payloads.append({
                            "question_number": i,
                            "prompt": prompt_val.strip(),
                            "away": away_t,
                            "home": home_t,
                            "db_id": q_obj.get("id")
                        })
                        st.divider()
                    
                    save_all_questions_btn = st.form_submit_button("Save & Publish All Questions 💾", type="primary")
                    
                    if save_all_questions_btn:
                        for item in question_payloads:
                            if item["prompt"]:
                                combined_text = f"{item['prompt']} | MATCHUP: {item['away']} @ {item['home']}"
                                
                                if item["db_id"]:
                                    supabase.table("weekly_questions").update({
                                        "question_text": combined_text
                                    }).eq("id", item["db_id"]).execute()
                                else:
                                    supabase.table("weekly_questions").insert({
                                        "week_number": selected_manage_week,
                                        "question_number": item["question_number"],
                                        "question_text": combined_text,
                                        "winning_answer": "Pending"
                                    }).execute()
                                    
                        st.balloons()
                        st.success(f"Successfully saved and updated Week {selected_manage_week} questions!")
                        st.rerun()

            elif admin_sec == "Auto-Lockout Scheduler":
                st.subheader("⏰ Auto-Lockout Scheduler & Emergency Override")
                lock_week = st.number_input("Select Week", min_value=1, max_value=24, step=1, key="admin_lock_week")
                
                existing_lock_row = supabase.table("weekly_questions").select("winning_answer").eq("week_number", lock_week).eq("question_number", 99).execute().data
                current_lock_val = existing_lock_row[0]["winning_answer"] if existing_lock_row else "Not Set"
                
                st.info(f"Current Lock Status for Week {lock_week}: `{current_lock_val}`")
                
                col_sch1, col_sch2 = st.columns(2)
                with col_sch1:
                    lock_date = st.date_input("Automatic Lockout Date (UTC)")
                    lock_time = st.time_input("Automatic Lockout Time (UTC)")
                with col_sch2:
                    st.write("")
                    st.write("")
                    manual_override_toggle = st.toggle("🚨 Manual Emergency Lockout Override", value=(current_lock_val == "LOCKED"))
                
                if st.button("Save Lockout Configuration 🔒", type="primary"):
                    if manual_override_toggle:
                        supabase.table("weekly_questions").delete().eq("week_number", lock_week).eq("question_number", 99).execute()
                        supabase.table("weekly_questions").insert({
                            "week_number": lock_week,
                            "question_number": 99,
                            "question_text": "WEEK LOCKOUT TIMESTAMP",
                            "winning_answer": "LOCKED"
                        }).execute()
                        st.success(f"Week {lock_week} has been MANUALLY LOCKED by Admin override!")
                    else:
                        combined_dt = datetime.combine(lock_date, lock_time).isoformat()
                        supabase.table("weekly_questions").delete().eq("week_number", lock_week).eq("question_number", 99).execute()
                        supabase.table("weekly_questions").insert({
                            "week_number": lock_week,
                            "question_number": 99,
                            "question_text": "WEEK LOCKOUT TIMESTAMP",
                            "winning_answer": f"LOCKTIME:{combined_dt}"
                        }).execute()
                        st.success(f"Auto-lockout scheduled for Week {lock_week} at {combined_dt} UTC!")

            elif admin_sec == "Grade Week & Calculate Points":
                st.subheader("Grade Weekly Results & Live Score Feeder")
                grade_week = st.number_input("Select Week to Grade", min_value=1, max_value=24, step=1, key="grade_week_num")
                
                with st.expander("⚡ Fetch Live ESPN Scores for Reference", expanded=False):
                    if st.button("🔄 Fetch Live Scores Now"):
                        try:
                            espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                            resp = requests.get(espn_url, timeout=10)
                            if resp.status_code == 200:
                                data = resp.json()
                                events = data.get("events", [])
                                game_results_cache = {}
                                for ev in events:
                                    comp = ev.get("competitions", [{}])[0]
                                    status_type = ev.get("status", {}).get("type", {}).get("name", "")
                                    competitors = comp.get("competitors", [])
                                    home_team_abbr = ""
                                    away_team_abbr = ""
                                    home_score = 0
                                    away_score = 0
                                    for team_obj in competitors:
                                        abbr = team_obj.get("team", {}).get("abbreviation", "")
                                        score = int(team_obj.get("score", 0))
                                        if team_obj.get("homeAway") == "home":
                                            home_team_abbr = abbr
                                            home_score = score
                                        else:
                                            away_team_abbr = abbr
                                            away_score = score
                                    if status_type == "STATUS_FINAL":
                                        game_results_cache[f"{away_team_abbr} @ {home_team_abbr}"] = {
                                            "status": "FINAL",
                                            "home_score": home_score,
                                            "away_score": away_score
                                        }
                                st.session_state["espn_fetched_scores"] = game_results_cache
                                st.success("Connected to ESPN! Scores fetched.")
                            else:
                                st.error("Failed to reach ESPN API.")
                        except Exception as e:
                            st.error(f"API Error: {e}")
                            
                    if "espn_fetched_scores" in st.session_state:
                        fetched_map = st.session_state["espn_fetched_scores"]
                        for matchup_key, info in fetched_map.items():
                            st.info(f"🏟️ **{matchup_key}** | Status: `{info['status']}` | Score: {info['away_score']} - {info['home_score']}")

                week_q = supabase.table("weekly_questions").select("*").eq("week_number", grade_week).order("question_number").execute().data
                real_grade_q = [q for q in week_q if q.get("question_number", 0) <= 10]
                
                if not real_grade_q:
                    st.warning("No questions found for this week.")
                else:
                    with st.form("grade_form"):
                        answers = {}
                        for q in real_grade_q:
                            default_val = q["winning_answer"] if q["winning_answer"] in ["Yes", "No"] else "Pending"
                            clean_prompt = q["question_text"].split(" | MATCHUP: ")[0] if " | MATCHUP: " in q["question_text"] else q["question_text"]
                            
                            answers[q["id"]] = st.selectbox(
                                f"Q{q['question_number']}: {clean_prompt}", 
                                ["Pending", "Yes", "No"], 
                                index=["Pending", "Yes", "No"].index(default_val),
                                key=f"ans_{q['id']}"
                            )
                        
                        st.markdown("---")
                        st.markdown("#### 🏈 Touchdown Scorer Correct Picks")
                        
                        td_picks_data = supabase.table("touchdown_picks").select("*").eq("week_number", grade_week).execute().data
                        all_profiles = supabase.table("profiles").select("id, full_name").execute().data
                        profile_dict = {p["id"]: p["full_name"] for p in all_profiles}
                        
                        td_winners = []
                        if not td_picks_data:
                            st.info("No Touchdown picks submitted for this week.")
                        else:
                            for td in td_picks_data:
                                player_user_name = profile_dict.get(td["user_id"], "Unknown Player")
                                current_is_correct = td.get("is_correct")
                                default_checkbox_val = bool(current_is_correct) if current_is_correct is not None else False
                                
                                is_winner = st.checkbox(
                                    f"**{player_user_name}** picked: *{td['player_name']}*", 
                                    value=default_checkbox_val,
                                    key=f"td_check_{td['id']}"
                                )
                                if is_winner:
                                    td_winners.append(td["user_id"])
                                    supabase.table("touchdown_picks").update({"is_correct": True}).eq("id", td["id"]).execute()
                                else:
                                    supabase.table("touchdown_picks").update({"is_correct": False}).eq("id", td["id"]).execute()

                        if st.form_submit_button("Calculate & Process Payouts 🏆", type="primary"):
                            for q_id, ans in answers.items():
                                supabase.table("weekly_questions").update({"winning_answer": ans}).eq("id", q_id).execute()
                            
                            week_bets = supabase.table("user_bets").select("*").eq("week_number", grade_week).execute().data
                            
                            user_token_changes = {}
                            for bet in week_bets:
                                u_id = bet["user_id"]
                                q_id = bet["question_id"]
                                correct_ans = answers.get(q_id)
                                wager = bet["wager_amount"]
                                
                                if u_id not in user_token_changes:
                                    user_token_changes[u_id] = 0
                                    
                                if correct_ans in ["Yes", "No"]:
                                    if bet["pick"] == correct_ans:
                                        user_token_changes[u_id] += wager
                                    else:
                                        user_token_changes[u_id] -= wager
                            
                            for winner_id in td_winners:
                                user_token_changes[winner_id] = user_token_changes.get(winner_id, 0) + 5
                            
                            for u_id, change in user_token_changes.items():
                                p_data = supabase.table("profiles").select("tokens").eq("id", u_id).single().execute().data
                                new_balance = max(0, p_data["tokens"] + change)
                                supabase.table("profiles").update({"tokens": new_balance}).eq("id", u_id).execute()
                                
                            st.balloons()
                            st.success("Scores graded and user token balances updated!")

            elif admin_sec == "Bulk Token Adjuster":
                st.subheader("👥 Bulk Player Token Adjuster")
                all_profiles_bulk = supabase.table("profiles").select("id, full_name, tokens, favorite_team").order("tokens", desc=True).execute().data
                
                if all_profiles_bulk:
                    with st.form("bulk_token_form"):
                        selected_user_ids = []
                        for p in all_profiles_bulk:
                            if st.checkbox(f"**{p['full_name']}** (`{p['tokens']} 🪙`)", key=f"bulk_chk_{p['id']}"):
                                selected_user_ids.append(p['id'])
                                
                        col_ba1, col_ba2 = st.columns(2)
                        with col_ba1: action_type = st.selectbox("Operation", ["Add Tokens", "Subtract Tokens", "Set Exact Token Balance"])
                        with col_ba2: token_amount_val = st.number_input("Token Value Amount", min_value=0, value=5, step=1)
                            
                        if st.form_submit_button("Apply Bulk Adjustment ⚡", type="primary"):
                            for u_id in selected_user_ids:
                                p_curr = supabase.table("profiles").select("tokens").eq("id", u_id).single().execute().data.get("tokens", 0)
                                if action_type == "Add Tokens": new_bal = p_curr + token_amount_val
                                elif action_type == "Subtract Tokens": new_bal = max(0, p_curr - token_amount_val)
                                else: new_bal = token_amount_val
                                supabase.table("profiles").update({"tokens": new_bal}).eq("id", u_id).execute()
                            st.balloons()
                            st.success(f"Updated {len(selected_user_ids)} players!")
                            st.rerun()

            elif admin_sec == "Export League Data (CSV)":
                st.subheader("📥 Export League Data")
                bets_data = supabase.table("user_bets").select("*").execute().data
                if bets_data:
                    st.download_button("Download All User Bets (CSV)", data=pd.DataFrame(bets_data).to_csv(index=False), file_name="touchdown_tokens_all_bets.csv", mime="text/csv")

            elif admin_sec == "League Chat Announcement":
                st.subheader("📢 Pre-Formatted League Announcement")
                ann_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="admin_ann_week")
                announcement_template = f"""🏈 *TOUCHDOWN TOKENS - WEEK {ann_week} IS LIVE!* 🏈

👉 Place your wagers and TD scorer pick now on Touchdown Tokens!
Good luck this week! 🔥"""
                st.code(announcement_template, language="markdown")

            elif admin_sec == "Archive & Reset Season":
                st.subheader("🧹 End-of-Season Reset Utility")
                confirm_check = st.checkbox("I confirm I wish to reset all user balances to 10 tokens.")
                if st.button("Reset Balances Now 🔄", type="primary", disabled=not confirm_check):
                    all_p = supabase.table("profiles").select("id").execute().data
                    for p in all_p:
                        supabase.table("profiles").update({"tokens": 10}).eq("id", p["id"]).execute()
                    st.success("All balances reset to 10 tokens!")

            elif admin_sec == "Season Champion Banner":
                st.subheader("🏆 End-of-Season Banner")
                all_players = supabase.table("profiles").select("full_name").order("tokens", desc=True).execute().data
                player_names = [p["full_name"] for p in all_players] if all_players else ["Player"]
                
                banner_toggle = st.toggle("Enable Banner")
                selected_champion = st.selectbox("Select Season Winner", player_names)
                
                if st.button("Save Banner Settings 🏆"):
                    state_str = "ON" if banner_toggle else "OFF"
                    supabase.table("weekly_questions").delete().eq("week_number", 999).execute()
                    supabase.table("weekly_questions").insert({"week_number": 999, "question_number": 1, "question_text": selected_champion, "winning_answer": state_str}).execute()
                    st.success("Saved Banner Settings!")
