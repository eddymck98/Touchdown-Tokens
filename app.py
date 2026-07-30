import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

# --- SUPABASE CONFIGURATION ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.set_page_config(page_title="Touchdown Tokens", page_icon="🏈", layout="centered")

# --- AUTHENTICATION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None

# Comprehensive NFL Team Logos & Primary Accent Hex Colors
NFL_TEAM_DATA = {
    "🏈 Free Agent / Neutral": {"logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nfl.png", "color": "#fbbf24"},
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
    "📉 Down Bad": "Reach a token balance of 0 tokens"
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
user_team_logo = "https://a.espncdn.com/i/teamlogos/nfl/500/nfl.png"
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
        box-shadow: 0 0 15px rgba(148, 163, 184, 0.3) !important;
    }}
    .podium-rank-3 {{
        border: 2px solid #b45309 !important;
        background: linear-gradient(135deg, rgba(180, 83, 9, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        box-shadow: 0 0 15px rgba(180, 83, 9, 0.3) !important;
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
    if toks >= 30:
        badges.append("🚀 Token Tycoon")
    if any(b['wager_amount'] >= 10 for b in u_bets):
        badges.append("🎯 High Roller")
    if len(u_td) >= 2:
        badges.append("🏈 TD Guru")
    if len(u_td) >= 3:
        badges.append("🎯 Sniper")
    if toks == 0:
        badges.append("📉 Down Bad")
        
    weeks_played = set()
    total_lifetime_won = 0
    for b in u_bets:
        weeks_played.add(b['week_number'])
        w_ans = b.get("weekly_questions", {}).get("winning_answer")
        if w_ans in ["Yes", "No"] and b['pick'] == w_ans:
            total_lifetime_won += b['wager_amount']
            
    if len(weeks_played) >= 5:
        badges.append("🛡️ Iron Defender")
    if total_lifetime_won >= 100:
        badges.append("💰 Century Club")

    graded_q = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
    if graded_q:
        latest_w = graded_q[0]["week_number"]
        all_latest_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("week_number", latest_w).execute().data
        
        user_gains = {}
        user_loss = {}
        user_correct = {}
        
        for b in all_latest_bets:
            u = b['user_id']
            w_ans = b.get("weekly_questions", {}).get("winning_answer")
            if u not in user_gains:
                user_gains[u] = 0
                user_loss[u] = 0
                user_correct[u] = 0
            
            if w_ans in ["Yes", "No"]:
                if b['pick'] == w_ans:
                    user_gains[u] += b['wager_amount']
                    user_correct[u] += 1
                else:
                    user_loss[u] += b['wager_amount']
        
        if user_gains and max(user_gains.values(), default=-1) > 0:
            if max(user_gains, key=user_gains.get) == target_user_id:
                badges.append("👑 Weekly High Scorer")
                
        if user_loss and max(user_loss.values(), default=-1) > 0:
            if max(user_loss, key=user_loss.get) == target_user_id:
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
                for nb in new_badges:
                    st.toast(f"🏆 NEW TROPHY UNLOCKED: {nb}!", icon="🎉")
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
            except Exception as e:
                st.error(f"Login failed: {e}")

        st.write("")
        with st.expander("🔑 Forgot Password?"):
            st.caption("Enter your email address to receive a password reset link.")
            reset_email = st.text_input("Your Account Email", key="reset_email_input")
            if st.button("Send Reset Link"):
                if reset_email:
                    try:
                        supabase.auth.reset_password_for_email(reset_email)
                        st.success("Password reset email sent! Check your inbox.")
                    except Exception as e:
                        st.error(f"Error sending email: {e}")
                else:
                    st.warning("Please enter your email address.")

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
                            "bio": "Ready for Kickoff!",
                            "avatar_emoji": "🏈"
                        }).execute()
                        st.success("Account created! You can now log in.")
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
    team_data = NFL_TEAM_DATA.get(user_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
    
    get_user_badges(user_id, check_celebration=True)

    st.sidebar.title(f"{user_avatar} {profile['full_name']}")
    st.sidebar.image(team_data["logo"], width=55)
    st.sidebar.caption(f"Team: {user_team}")
    st.sidebar.metric(label="Available Tokens", value=f"{profile['tokens']} 🪙")
    
    st.sidebar.divider()
    st.sidebar.subheader("📌 Quick Jump Menu")
    nav_choice = st.sidebar.radio(
        "Jump to Section:", 
        ["Home", "Profile & Trophies", "Rules & Info", "Place Bets", "My History", "Leaderboard", "Hall of Fame"] + (["Admin Control"] if profile.get("is_admin") else []),
        label_visibility="collapsed"
    )
    
    if profile.get("is_admin"):
        st.sidebar.success("👑 Admin Mode Active")
        
    if st.sidebar.button("Log Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    if profile.get("is_admin"):
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_hof, tab_admin = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏛️ Hall of Fame", "⚙️ Admin Control"]
        )
    else:
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_hof = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏛️ Hall of Fame"]
        )

    weeks_res = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute()
    available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []

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
                <div style="font-size: 18px; letter-spacing: 2px; text-transform: uppercase; color: #93c5fd;">Current Balance</div>
                <div class="big-token-number">{profile['tokens']} 🪙</div>
                <div style="font-size: 16px; color: #cbd5e1;">Touchdown Tokens</div>
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
                share_text_block = "\n".join(share_lines)
                st.code(share_text_block, language="markdown")
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
                if u not in user_weekly_net:
                    user_weekly_net[u] = 0
                if w_ans in ["Yes", "No"]:
                    if b['pick'] == w_ans:
                        user_weekly_net[u] += b['wager_amount']
                    else:
                        user_weekly_net[u] -= b['wager_amount']
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

        if graded_q_badge:
            last_w_num = graded_q_badge[0]["week_number"]
            st.divider()
            st.subheader(f"📈 Week {last_w_num} Community Trends & Most Picked Lines")
            
            lw_all_bets = supabase.table("user_bets").select("question_id, pick, wager_amount, weekly_questions(question_text)").eq("week_number", last_w_num).execute().data
            if lw_all_bets:
                q_stats = {}
                for b in lw_all_bets:
                    q_text = b.get("weekly_questions", {}).get("question_text", "Question")
                    clean_q = q_text.split(" | MATCHUP: ")[0] if " | MATCHUP: " in q_text else q_text
                    if clean_q not in q_stats:
                        q_stats[clean_q] = {"Yes": 0, "No": 0, "TotalWager": 0, "Votes": 0}
                    q_stats[clean_q][b["pick"]] += 1
                    q_stats[clean_q]["TotalWager"] += b["wager_amount"]
                    q_stats[clean_q]["Votes"] += 1
                
                trend_list = []
                for q_name, data in q_stats.items():
                    yes_v = data["Yes"]
                    no_v = data["No"]
                    tot = data["Votes"]
                    if tot > 0:
                        yes_pct = int((yes_v / tot) * 100)
                        no_pct = 100 - yes_pct
                        majority_pick = "YES" if yes_pct >= 50 else "NO"
                        majority_pct = max(yes_pct, no_pct)
                        trend_list.append({
                            "question": q_name,
                            "consensus": f"{majority_pct}% {majority_pick}",
                            "total_wagered": data["TotalWager"],
                            "votes": tot
                        })
                
                if trend_list:
                    trend_df = pd.DataFrame(trend_list).sort_values(by="total_wagered", ascending=False).head(3)
                    for _, row in trend_df.iterrows():
                        st.markdown(f"""
                            <div class="summary-box">
                                <b>🔥 Heaviest Action: {row['question']}</b><br>
                                • <b>League Consensus:</b> {row['consensus']} ({row['votes']} total player bets)<br>
                                • <b>Total Tokens Wagered on Matchup:</b> {row['total_wagered']} 🪙
                            </div>
                        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📊 Last Week's Performance Summary")
        
        if not graded_q_badge:
            st.info("No weeks have been graded yet. Place your bets for Week 1 to get started!")
        else:
            latest_graded_week = graded_q_badge[0]["week_number"]
            
            lw_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", user_id).eq("week_number", latest_graded_week).execute().data
            lw_td = supabase.table("touchdown_picks").select("*").eq("user_id", user_id).eq("week_number", latest_graded_week).execute().data
            
            if not lw_bets and not lw_td:
                st.warning(f"You did not submit any bets or touchdown picks for Week {latest_graded_week}.")
            else:
                bet_gains = 0
                bet_losses = 0
                correct_count = 0
                total_bets_placed = len(lw_bets)
                
                for b in lw_bets:
                    w_ans = b.get("weekly_questions", {}).get("winning_answer")
                    if w_ans in ["Yes", "No"]:
                        if b["pick"] == w_ans:
                            bet_gains += b["wager_amount"]
                            correct_count += 1
                        else:
                            bet_losses += b["wager_amount"]
                
                td_bonus = 5 if (lw_td and lw_td[0].get("is_correct")) else 0
                td_player = lw_td[0]["player_name"] if lw_td else "None"
                
                net_total = bet_gains - bet_losses + td_bonus
                
                if net_total > 0:
                    st.balloons()
                
                st.markdown(f"### Week {latest_graded_week} Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Net Tokens Earned", f"{'+' if net_total >= 0 else ''}{net_total} 🪙")
                with col2:
                    st.metric("Questions Correct", f"{correct_count} / {total_bets_placed}")
                with col3:
                    st.metric("TD Scorer Bonus", f"+{td_bonus} 🪙" if td_bonus > 0 else "0 🪙")
                
                st.markdown(f"""
                <div class="summary-box">
                    <b>Week {latest_graded_week} Breakdown:</b><br>
                    • <b>Question Wins:</b> +{bet_gains} Tokens<br>
                    • <b>Question Losses:</b> -{bet_losses} Tokens<br>
                    • <b>Touchdown Scorer Pick:</b> '{td_player}' ({'✅ +5 Tokens' if td_bonus > 0 else '❌ Missed'})
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
                        if b["pick"] == w_ans:
                            curr_tokens += b["wager_amount"]
                        else:
                            curr_tokens -= b["wager_amount"]
                week_tokens[w] = max(0, curr_tokens)
                
            chart_df = pd.DataFrame(list(week_tokens.items()), columns=["Week", "Tokens"]).set_index("Week")
            st.line_chart(chart_df)

    # ------------------------------------------
    # TAB 1: PROFILE & TROPHY CABINET
    # ------------------------------------------
    with tab_profile:
        st.header("👤 Profile & Trophy Cabinet")
        st.caption("Personalize your profile settings and inspect player badge collections across the league!")
        
        curr_team = profile.get("favorite_team", "🏈 Free Agent / Neutral")
        team_index = NFL_TEAMS.index(curr_team) if curr_team in NFL_TEAMS else 0
        
        new_team = st.selectbox("Favorite NFL Team", NFL_TEAMS, index=team_index)
        selected_team_data = NFL_TEAM_DATA.get(new_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
        
        col_logo, col_info = st.columns([1, 4])
        with col_logo:
            st.image(selected_team_data["logo"], width=75)
        with col_info:
            st.markdown(f"### {new_team}")
            st.markdown(f"<span style='color:{selected_team_data['color']}; font-weight:bold;'>Primary Theme Color: {selected_team_data['color']}</span>", unsafe_allow_html=True)

        with st.form("profile_customization_form"):
            new_display_name = st.text_input("Display Name", value=profile.get("full_name", ""))
            curr_avatar = profile.get("avatar_emoji", "🏈")
            avatar_index = AVATAR_OPTIONS.index(curr_avatar) if curr_avatar in AVATAR_OPTIONS else 0
            new_avatar = st.selectbox("Choose Profile Avatar Emoji", AVATAR_OPTIONS, index=avatar_index)
            new_bio = st.text_input("Profile Catchphrase / Bio (max 100 chars)", value=profile.get("bio", "Ready for Kickoff!"), max_chars=100)
            
            save_profile = st.form_submit_button("Save Profile Settings 💾", type="primary")
            
            if save_profile:
                if not new_display_name.strip():
                    st.error("Display Name cannot be blank.")
                else:
                    supabase.table("profiles").update({
                        "full_name": new_display_name.strip(),
                        "favorite_team": new_team,
                        "avatar_emoji": new_avatar,
                        "bio": new_bio.strip()
                    }).eq("id", user_id).execute()
                    st.success("Profile updated successfully!")
                    st.rerun()

        st.divider()
        st.subheader("🏆 Virtual Trophy Cabinet")
        st.caption("Inspect badge showcases across any league member.")
        
        all_league_profiles = supabase.table("profiles").select("id, full_name, avatar_emoji, favorite_team").execute().data
        user_name_map = {p["full_name"]: p for p in all_league_profiles}
        
        selected_player_name = st.selectbox("Select Player Trophy Showcase", list(user_name_map.keys()), key="trophy_player_select")
        selected_player = user_name_map[selected_player_name]
        
        selected_badges = get_user_badges(selected_player["id"])
        selected_team_info = NFL_TEAM_DATA.get(selected_player.get("favorite_team"), NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
        
        unlocked_count = len(selected_badges)
        total_badges_count = len(MASTER_BADGES)
        progress_ratio = unlocked_count / total_badges_count
        progress_pct = int(progress_ratio * 100)
        
        col_t_logo, col_t_info = st.columns([1, 4])
        with col_t_logo:
            st.image(selected_team_info["logo"], width=70)
        with col_t_info:
            st.markdown(f"### {selected_player.get('avatar_emoji', '🏈')} {selected_player['full_name']}'s Showcase")
            st.markdown(f"**Unlocked:** `{unlocked_count}` / `{total_badges_count}` Badges")
        
        st.progress(progress_ratio, text=f"**Cabinet Completion:** `{progress_pct}%` Unlocked")
        st.write("")
        
        t_col1, t_col2 = st.columns(2)
        for idx, (b_name, b_desc) in enumerate(MASTER_BADGES.items()):
            is_unlocked = b_name in selected_badges
            target_col = t_col1 if idx % 2 == 0 else t_col2
            
            with target_col:
                if is_unlocked:
                    st.markdown(f"""
                        <div class="trophy-card-unlocked">
                            <b>{b_name}</b> <span style="color:#fbbf24; font-weight:bold;">(UNLOCKED)</span><br>
                            <small style="color:#cbd5e1;">{b_desc}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="trophy-card-locked">
                            <b>🔒 {b_name}</b><br>
                            <small>{b_desc}</small>
                        </div>
                    """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: RULES & INFO
    # ------------------------------------------
    with tab_rules:
        st.header("📖 Rules & Information")
        
        st.subheader("Welcome to TOUCHDOWN TOKENS!")
        st.write("""
        Each week I will release a new form with 10 scenarios. Each player will start with 10 tokens. 
        If you win your bet, you will double however many tokens you placed on that scenario. 
        If you lose the scenario, you will lose all your tokens that you placed on that scenario.
        
        Tokens are cumulative, so if you gain 8 tokens from right answers in Week 1, you will have 18 tokens for Week 2, and so on.
        
        At the bottom of the weekly picks is a place for you to write a free bet on a player you think will score a touchdown this week. 
        If your player scores, you will gain extra bonus tokens to use in the next week!
        
        All games picked will be Sunday/Monday games. No Thursday games will be picked. 
        Whilst you can pick the same scorer every week, mix it up and test your NFL knowledge!
        """)
        
        st.divider()
        st.subheader("📜 Official Game Rules")
        
        st.markdown("""
        1. 🪙 **Wager Limits:** Don't go over your current total token balance.
        2. 🎯 **One Choice Per Question:** You must only place a bet on 1 option (`Yes` or `No`) per question.
        3. 📅 **Attendance & Active Play:** If you miss a week that is absolutely fine; however, if you continue to miss weeks, you will be docked points per week missed.
        4. 🚑 **Late Scratches / Inactive Players:** If for any reason a player chosen in a scenario is ruled out just before a game, all points bet on that scenario will be refunded.
        5. ⏰ **Submission Cutoff:** The cutoff for weekly submissions will be **15 minutes before the first kickoff** on Sunday.
        6. 🏈 **Touchdown Scorer Eligibility:** The free bet scorer must either **rush or receive** a touchdown. Passing touchdowns do **NOT** count!
        """)

        st.markdown("""
        <div class="summary-box">
            <b>📱 Pro Tip: Add to Phone Home Screen!</b><br>
            • <b>iPhone (Safari):</b> Tap the <i>Share Button</i> at the bottom → select <b>'Add to Home Screen'</b>.<br>
            • <b>Android (Chrome):</b> Tap the <i>3 Dots Menu</i> at the top right → select <b>'Install App'</b> or <b>'Add to Home Screen'</b>.
        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 3: PLACE BETS
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        st.link_button("🏈 View NFL Scores, Lines & Fixtures ↗️", "https://www.espn.com/nfl/schedule", use_container_width=True)
        st.caption("Check real-time odds, matchups, and player news on ESPN before placing your bets!")
        st.write("")

        if not available_weeks:
            st.info("No active questions available yet. Check back soon when the Admin posts Week 1!")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            is_locked = False
            lock_time_row = [q for q in questions if q.get("winning_answer", "").startswith("LOCKTIME:")]
            
            if lock_time_row:
                raw_lock_str = lock_time_row[0]["winning_answer"].replace("LOCKTIME:", "")
                try:
                    lock_dt = datetime.fromisoformat(raw_lock_str).replace(tzinfo=timezone.utc)
                    now_dt = datetime.now(timezone.utc)
                    time_diff = lock_dt - now_dt
                    
                    if time_diff.total_seconds() <= 0:
                        is_locked = True
                        st.error("🔒 Entries for this week are locked! Kickoff deadline has passed.")
                    else:
                        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        st.markdown(f"""
                            <div class="timer-card">
                                ⏳ <b>KICKOFF LOCKOUT COUNTDOWN:</b> <span style="font-size:20px; font-weight:bold; color:{user_team_color};">{hours}h {minutes}m {seconds}s remaining</span>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception:
                    pass
            
            if any(q.get("winning_answer") == "LOCKED" for q in questions):
                is_locked = True
                st.error("🔒 Entries for this week have been manually locked by the Admin.")

            if not questions:
                st.info("No questions found for this week.")
            else:
                all_week_bets = supabase.table("user_bets").select("question_id, pick").eq("week_number", selected_week).execute().data
                
                if not is_locked and profile['tokens'] > 0:
                    col_rand1, col_rand2 = st.columns([3, 1])
                    with col_rand2:
                        if st.button("🎲 Feeling Lucky (Randomize Bets)", help="Randomly distributes your available tokens across the questions!"):
                            real_q_items = [q for q in questions if not q.get("winning_answer", "").startswith("LOCKTIME:")]
                            if real_q_items:
                                remaining_tokens = profile['tokens']
                                supabase.table("user_bets").delete().eq("user_id", user_id).eq("week_number", selected_week).execute()
                                
                                token_allocations = {q['id']: 0 for q in real_q_items}
                                for _ in range(remaining_tokens):
                                    chosen_q = random.choice(real_q_items)
                                    token_allocations[chosen_q['id']] += 1
                                    
                                for q_item in real_q_items:
                                    random_pick = random.choice(["Yes", "No"])
                                    w_amt = token_allocations[q_item['id']]
                                    supabase.table("user_bets").insert({
                                        "user_id": user_id,
                                        "week_number": selected_week,
                                        "question_id": q_item['id'],
                                        "pick": random_pick,
                                        "wager_amount": w_amt
                                    }).execute()
                                st.success("🎲 Random bets generated successfully! Check your selections below.")
                                st.rerun()

                with st.form("weekly_bet_form"):
                    wagers = {}
                    picks = {}
                    
                    st.markdown("### 10 Weekly Questions")
                    st.caption("Expand any question below to make your pick and wager tokens.")
                    
                    for q in questions:
                        if q.get("winning_answer", "").startswith("LOCKTIME:"):
                            continue
                            
                        full_q_text = q['question_text']
                        away_team_name = "🏈 Free Agent / Neutral"
                        home_team_name = "🏈 Free Agent / Neutral"
                        prompt_text = full_q_text
                        
                        if " | MATCHUP: " in full_q_text:
                            parts = full_q_text.split(" | MATCHUP: ")
                            prompt_text = parts[0]
                            matchup_str = parts[1]
                            if " @ " in matchup_str:
                                teams_split = matchup_str.split(" @ ")
                                away_team_name = teams_split[0]
                                home_team_name = teams_split[1]

                        away_info = NFL_TEAM_DATA.get(away_team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                        home_info = NFL_TEAM_DATA.get(home_team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])

                        existing_bet_row = [b for b in all_week_bets if b.get('question_id') == q['id']]
                        default_pick_val = existing_bet_row[0]['pick'] if existing_bet_row else "Yes"
                        default_wager_val = existing_bet_row[0]['wager_amount'] if existing_bet_row else 0

                        with st.expander(f"Q{q['question_number']}: {prompt_text[:50]}... ({away_team_name} @ {home_team_name})", expanded=True):
                            col_away_logo, col_matchup_txt, col_home_logo = st.columns([1, 4, 1])
                            with col_away_logo:
                                st.image(away_info["logo"], width=40)
                            with col_matchup_txt:
                                st.markdown(f"""
                                    <div style="text-align:center; padding-top:2px;">
                                        <span class="matchup-team-title">{away_team_name}</span>
                                        <span style="color:#cbd5e1; font-weight:bold; margin: 0 6px;">@</span>
                                        <span class="matchup-team-title">{home_team_name}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col_home_logo:
                                st.image(home_info["logo"], width=40)

                            q_bets = [b for b in all_week_bets if b['question_id'] == q['id']]
                            if q_bets:
                                yes_cnt = sum(1 for b in q_bets if b['pick'] == "Yes")
                                pct_yes = int((yes_cnt / len(q_bets)) * 100)
                                st.markdown(f'<span class="consensus-badge">📊 League Pick: {pct_yes}% YES ({len(q_bets)} votes)</span>', unsafe_allow_html=True)

                            st.markdown(f"**Question: {prompt_text}**")
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                picks[q['id']] = st.radio(
                                    f"Pick Q{q['question_number']}", 
                                    ["Yes", "No"], 
                                    index=0 if default_pick_val == "Yes" else 1,
                                    key=f"pick_{q['id']}", 
                                    horizontal=True,
                                    disabled=is_locked
                                )
                            with col2:
                                wagers[q['id']] = st.number_input(
                                    f"Wager Q{q['question_number']}", 
                                    min_value=0, 
                                    max_value=profile['tokens'], 
                                    value=default_wager_val, 
                                    key=f"wager_{q['id']}",
                                    disabled=is_locked
                                )

                    st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                    st.caption("Name 1 player to score a TD this week (Rushing/Receiving only!). Correct pick = Bonus Tokens!")
                    
                    existing_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", selected_week).execute().data
                    default_td = existing_td[0]["player_name"] if existing_td else ""
                    
                    td_pick = st.text_input("Player Name (e.g., Patrick Mahomes)", value=default_td, key="td_scorer", disabled=is_locked)
                    
                    total_wagered = sum(wagers.values())
                    max_available = max(1, profile['tokens'])
                    progress_val = min(1.0, total_wagered / max_available)
                    pct_str = int(progress_val * 100)
                    
                    if total_wagered > profile['tokens']:
                        st.error(f"⚠️ Over-wagered! You have allocated {total_wagered} tokens but only have {profile['tokens']} available.")
                    else:
                        st.progress(
                            progress_val, 
                            text=f"**Tokens Allocated:** `{total_wagered}` / `{profile['tokens']}` Tokens ({pct_str}%)"
                        )
                    
                    submit_bet = st.form_submit_button("Submit Weekly Bets 🚀", type="primary", use_container_width=True, disabled=is_locked)
                    
                    if submit_bet and not is_locked:
                        if total_wagered > profile['tokens']:
                            st.error(f"Cannot wager {total_wagered} tokens! You only have {profile['tokens']} tokens available.")
                        else:
                            for q_id, pick_val in picks.items():
                                w_amt = wagers[q_id]
                                supabase.table("user_bets").delete().eq("user_id", user_id).eq("question_id", q_id).execute()
                                supabase.table("user_bets").insert({
                                    "user_id": user_id,
                                    "week_number": selected_week,
                                    "question_id": q_id,
                                    "pick": pick_val,
                                    "wager_amount": w_amt
                                }).execute()
                                
                            if td_pick:
                                supabase.table("touchdown_picks").delete().eq("user_id", user_id).eq("week_number", selected_week).execute()
                                supabase.table("touchdown_picks").insert({
                                    "user_id": user_id,
                                    "week_number": selected_week,
                                    "player_name": td_pick
                                }).execute()
                                
                            st.balloons()
                            st.success("Your bets and touchdown pick have been successfully locked in!")

    # ------------------------------------------
    # TAB 4: MY HISTORY
    # ------------------------------------------
    with tab_history:
        st.header("Your Past Bets & Results")
        history_bets = supabase.table("user_bets").select("*, weekly_questions(question_number, question_text, winning_answer)").eq("user_id", user_id).execute().data
        
        if not history_bets:
            st.info("You haven't placed any bets yet.")
        else:
            formatted_data = []
            for b in history_bets:
                q_info = b.get("weekly_questions", {})
                w_ans = q_info.get("winning_answer", "Pending")
                raw_q_text = q_info.get("question_text", "N/A")
                clean_q_prompt = raw_q_text.split(" | MATCHUP: ")[0] if " | MATCHUP: " in raw_q_text else raw_q_text
                
                if w_ans in ["Pending", "LOCKED"] or w_ans.startswith("LOCKTIME:"):
                    outcome = "Pending"
                elif b["pick"] == w_ans:
                    outcome = f"✅ Won (+{b['wager_amount'] * 2} Tokens)"
                else:
                    outcome = f"❌ Lost (-{b['wager_amount']} Tokens)"
                        
                formatted_data.append({
                    "Week": b["week_number"],
                    "Question": clean_q_prompt,
                    "Your Pick": b["pick"],
                    "Wager": b["wager_amount"],
                    "Winner": w_ans if not w_ans.startswith("LOCKTIME:") and w_ans not in ["Pending", "LOCKED"] else "Pending",
                    "Result": outcome
                })
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 5: LEADERBOARD
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 Player Standings")
        leader_res = supabase.table("profiles").select("id, full_name, tokens, favorite_team, bio, avatar_emoji").order("tokens", desc=True).execute().data
        
        if leader_res:
            for idx, p in enumerate(leader_res):
                av = p.get("avatar_emoji") or "🏈"
                team_name = p.get("favorite_team") or "🏈 Free Agent / Neutral"
                t_info = NFL_TEAM_DATA.get(team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                p_badges = get_user_badges(p["id"])
                
                badges_html = "".join([f'<span class="badge-pill">{b}</span>' for b in p_badges]) if p_badges else '<span style="color:#64748b; font-size:12px;">No Badges Yet</span>'
                bio_text = p.get('bio', '')
                
                podium_class = "leaderboard-row"
                rank_display = f"#{idx + 1}"
                if idx == 0:
                    podium_class += " podium-rank-1"
                    rank_display = "🥇 #1"
                elif idx == 1:
                    podium_class += " podium-rank-2"
                    rank_display = "🥈 #2"
                elif idx == 2:
                    podium_class += " podium-rank-3"
                    rank_display = "🥉 #3"
                
                st.markdown(f"""
                    <div class="{podium_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-family: 'Bebas Neue'; font-size: 26px; color: #fbbf24; width: 45px;">{rank_display}</span>
                                <img src="{t_info['logo']}" style="width: 32px; height: 32px;" />
                                <div>
                                    <b style="font-size: 19px; color: #ffffff;">{av} {p['full_name']}</b>
                                    <div style="font-size: 13px; color: #94a3b8;">{team_name} {f'• "{bio_text}"' if bio_text else ''}</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-family: 'Bebas Neue'; font-size: 30px; color: #38bdf8;">{p['tokens']} 🪙</span>
                            </div>
                        </div>
                        <div style="border-top: 1px solid #334155; padding-top: 8px; margin-top: 4px;">
                            <span style="font-size: 12px; text-transform: uppercase; color: #94a3b8; font-weight: bold; margin-right: 8px;">Trophies:</span> {badges_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.subheader("💬 League Trash Talk Feed")
        
        with st.form("trash_talk_form"):
            chat_msg = st.text_input("Post a message to the league...", key="chat_input")
            post_chat = st.form_submit_button("Post Message 💬")
            
            if post_chat and chat_msg.strip():
                try:
                    supabase.table("trash_talk").insert({
                        "user_id": user_id,
                        "message": chat_msg.strip()
                    }).execute()
                    st.success("Message posted!")
                    st.rerun()
                except Exception as e:
                    st.error("Make sure the 'trash_talk' table is created in Supabase.")

        recent_chats = supabase.table("trash_talk").select("message, created_at, user_id").order("created_at", desc=True).limit(10).execute().data
        all_profiles = supabase.table("profiles").select("id, full_name, avatar_emoji, favorite_team").execute().data
        profile_map = {p["id"]: p for p in all_profiles}

        if recent_chats:
            for c in recent_chats:
                p_info = profile_map.get(c["user_id"], {})
                author_name = p_info.get("full_name", "Player")
                author_av = p_info.get("avatar_emoji", "🏈")
                author_team = p_info.get("favorite_team", "🏈 Free Agent / Neutral")
                t_info = NFL_TEAM_DATA.get(author_team, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                
                st.markdown(f"""
                <div class="chat-bubble" style="border-left: 5px solid {t_info['color']} !important;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <img src="{t_info['logo']}" style="width:28px; height:28px;" />
                        <b>{author_av} {author_name}</b> <small style="opacity:0.7;">({author_team})</small>
                    </div>
                    <div style="margin-top:6px;">{c['message']}</div>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 6: HALL OF FAME & SEASON ARCHIVES (2023 & 2024)
    # ------------------------------------------
    with tab_hof:
        st.header("🏛️ Touchdown Tokens Hall of Fame")
        st.caption("Archive of past champions and legendary historical seasons.")
        
        archive_year_sel = st.selectbox("Select Season Archive", ["2024 Season", "2023 Season"])
        
        if archive_year_sel == "2024 Season":
            st.markdown(f"""
                <div class="champion-card">
                    <div style="font-size: 20px; letter-spacing: 2px;">👑 2024 SEASON CHAMPION</div>
                    <div style="font-size: 48px; font-weight: 900; margin: 8px 0;">Louis Lynn (74 🪙)</div>
                    <div style="font-size: 16px;">Crowned the ultimate Touchdown Tokens victor of the 2024 campaign!</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📜 2024 Official Season Final Standings")
            st.caption("Complete historical results from the 2024 Touchdown Tokens leaderboard.")
            
            data_2024 = [
                {"Rank": "🥇", "Player": "Louis Lynn", "Final Tokens": 74},
                {"Rank": "🥈", "Player": "John Willis", "Final Tokens": 66},
                {"Rank": "🥉", "Player": "Will Granger", "Final Tokens": 29},
                {"Rank": "3nd (Tied)", "Player": "Adam Volpin", "Final Tokens": 29},
                {"Rank": "5th", "Player": "Gary Shaw", "Final Tokens": 23},
                {"Rank": "6th", "Player": "Suzie McKenna", "Final Tokens": 21},
                {"Rank": "7th", "Player": "Dan Hammerton", "Final Tokens": 14},
                {"Rank": "7th (Tied)", "Player": "Tom Wood", "Final Tokens": 14},
                {"Rank": "9th", "Player": "Patrick Smith", "Final Tokens": 13},
                {"Rank": "10th", "Player": "Joe Kewley-Joy", "Final Tokens": 10},
                {"Rank": "11th", "Player": "Paul Hindle", "Final Tokens": 6},
                {"Rank": "12th", "Player": "Liam Murphy", "Final Tokens": 0},
            ]
            df_2024 = pd.DataFrame(data_2024)
            st.dataframe(df_2024, use_container_width=True, hide_index=True)
            
        else:
            st.markdown(f"""
                <div class="champion-card">
                    <div style="font-size: 20px; letter-spacing: 2px;">👑 2023 SEASON CHAMPION</div>
                    <div style="font-size: 48px; font-weight: 900; margin: 8px 0;">Ed McKenna (117 🪙)</div>
                    <div style="font-size: 16px;">Crowned the ultimate Touchdown Tokens victor of the 2023 campaign!</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📜 2023 Official Season Final Standings")
            st.caption("Complete historical results from the 2023 Touchdown Tokens leaderboard.")
            
            data_2023 = [
                {"Rank": "🥇", "Player": "Ed McKenna", "Final Tokens": 117},
                {"Rank": "🥈", "Player": "Suzie McKenna", "Final Tokens": 87},
                {"Rank": "🥉", "Player": "Gary Shaw", "Final Tokens": 76},
                {"Rank": "4th", "Player": "Adam Volpin", "Final Tokens": 67},
                {"Rank": "5th", "Player": "Tom Wood", "Final Tokens": 49},
                {"Rank": "6th", "Player": "Jay Kewley-Joy", "Final Tokens": 48},
                {"Rank": "7th", "Player": "Will Granger", "Final Tokens": 47},
                {"Rank": "8th", "Player": "John Willis", "Final Tokens": 28},
                {"Rank": "9th", "Player": "Patrick Smith", "Final Tokens": 4},
                {"Rank": "10th", "Player": "Ethan Lewis", "Final Tokens": 3},
            ]
            df_2023 = pd.DataFrame(data_2023)
            st.dataframe(df_2023, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # TAB 7: ADMIN CONTROL
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            
            admin_sec = st.radio("Select Action", ["Manage Questions", "Auto-Lockout Scheduler", "Grade Week & Calculate Points", "Bulk Token Adjuster", "Export League Data (CSV)", "League Chat Announcement", "Archive & Reset Season", "Season Champion Banner"], horizontal=True)
            
            # COMBINED & PERSISTENT QUESTION MANAGEMENT
            if admin_sec == "Manage Questions":
                st.subheader("📋 Manage & Edit Weekly Questions & Matchups")
                st.caption("Select a week below to view, publish, or edit questions and matchups dynamically. They will stay right here for ongoing edits!")
                
                # Fetch all existing weeks in database + allow selecting a new/next week
                all_db_weeks = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute().data
                db_week_nums = sorted(list(set([r["week_number"] for r in all_db_weeks]))) if all_db_weeks else []
                next_suggested_week = (db_week_nums[-1] + 1) if db_week_nums else 1
                
                week_options = db_week_nums + [next_suggested_week] if next_suggested_week not in db_week_nums else db_week_nums
                selected_manage_week = st.selectbox("Select Week to Manage", week_options, index=len(week_options)-1, key="admin_manage_week_sel")
                
                # Load existing questions for this week
                existing_week_qs = supabase.table("weekly_questions").select("*").eq("week_number", selected_manage_week).order("question_number").execute().data
                real_existing_qs = {q["question_number"]: q for q in existing_week_qs if q.get("question_number", 0) <= 10}
                
                if st.button("📋 Load 10 Default Question Templates"):
                    for i in range(1, 11):
                        st.session_state[f"manage_prompt_w{selected_manage_week}_q{i}"] = DEFAULT_QUESTION_TEMPLATES[i-1]
                    st.success("Default templates loaded into inputs below!")
                    st.rerun()

                with st.form(key=f"manage_questions_form_week_{selected_manage_week}"):
                    question_payloads = []
                    
                    for i in range(1, 11):
                        st.markdown(f"#### Question {i}")
                        
                        # Extract existing data if present in DB
                        q_obj = real_existing_qs.get(i, {})
                        raw_txt = q_obj.get("question_text", "")
                        
                        existing_prompt = raw_txt.split(" | MATCHUP: ")[0] if " | MATCHUP: " in raw_txt else raw_txt
                        if not existing_prompt and f"manage_prompt_w{selected_manage_week}_q{i}" in st.session_state:
                            existing_prompt = st.session_state[f"manage_prompt_w{selected_manage_week}_q{i}"]
                            
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
                            
                        prompt_val = st.text_input(f"Question {i} Prompt", value=existing_prompt, key=f"m_prompt_w{selected_manage_week}_q{i}")
                        
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
                                    # Update existing question so it stays persistent and editable
                                    supabase.table("weekly_questions").update({
                                        "question_text": combined_text
                                    }).eq("id", item["db_id"]).execute()
                                else:
                                    # Insert new question if it didn't exist yet
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
                    st.caption("Pull live game scores from ESPN to verify outcomes before grading below.")
                    if st.button("🔄 Fetch Live Scores Now"):
                        try:
                            espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                            resp = requests.get(espn_url, timeout=10)
                            if resp.status_code == 200:
                                data = resp.json()
                                events = data.get("events", [])
                                st.success(f"Connected to ESPN! Found {len(events)} games.")
                                
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
                            else:
                                st.error("Failed to reach ESPN scoreboard API.")
                        except Exception as e:
                            st.error(f"API Error: {e}")
                            
                    if "espn_fetched_scores" in st.session_state:
                        st.write("**Live API Game Status Feed:**")
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
                        st.caption("Check the box next to any player who successfully scored a TD (+5 bonus tokens).")
                        
                        td_picks_data = supabase.table("touchdown_picks").select("*").eq("week_number", grade_week).execute().data
                        all_profiles = supabase.table("profiles").select("id, full_name").execute().data
                        profile_dict = {p["id"]: p["full_name"] for p in all_profiles}
                        
                        td_winners = []
                        if not td_picks_data:
                            st.info("No Touchdown picks submitted for this week.")
                        else:
                            for td in td_picks_data:
                                player_user_name = profile_dict.get(td["user_id"], "Unknown Player")
                                is_winner = st.checkbox(
                                    f"**{player_user_name}** picked: *{td['player_name']}*", 
                                    value=bool(td.get("is_correct")),
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
                st.subheader("👥 Bulk Player Token Adjuster & Reset Wizard")
                st.caption("Select multiple players at once and apply a token adjustment or reset.")
                
                all_profiles_bulk = supabase.table("profiles").select("id, full_name, tokens, favorite_team").order("tokens", desc=True).execute().data
                
                if not all_profiles_bulk:
                    st.info("No players found.")
                else:
                    with st.form("bulk_token_form"):
                        st.markdown("#### Select Players")
                        selected_user_ids = []
                        
                        for p in all_profiles_bulk:
                            is_checked = st.checkbox(f"**{p['full_name']}** (Current Balance: `{p['tokens']} 🪙` | Team: {p['favorite_team']})", key=f"bulk_chk_{p['id']}")
                            if is_checked:
                                selected_user_ids.append(p['id'])
                                
                        st.divider()
                        st.markdown("#### Action to Apply")
                        col_ba1, col_ba2 = st.columns(2)
                        with col_ba1:
                            action_type = st.selectbox("Operation", ["Add Tokens", "Subtract Tokens", "Set Exact Token Balance"])
                        with col_ba2:
                            token_amount_val = st.number_input("Token Value Amount", min_value=0, value=5, step=1)
                            
                        submit_bulk = st.form_submit_button("Apply Bulk Adjustment ⚡", type="primary")
                        
                        if submit_bulk:
                            if not selected_user_ids:
                                st.warning("Please check off at least one player above.")
                            else:
                                for u_id in selected_user_ids:
                                    p_curr = supabase.table("profiles").select("tokens").eq("id", u_id).single().execute().data.get("tokens", 0)
                                    
                                    if action_type == "Add Tokens":
                                        new_bal = p_curr + token_amount_val
                                    elif action_type == "Subtract Tokens":
                                        new_bal = max(0, p_curr - token_amount_val)
                                    else:
                                        new_bal = token_amount_val
                                        
                                    supabase.table("profiles").update({"tokens": new_bal}).eq("id", u_id).execute()
                                    
                                st.balloons()
                                st.success(f"Successfully updated tokens for {len(selected_user_ids)} players!")
                                st.rerun()

            elif admin_sec == "Export League Data (CSV)":
                st.subheader("📥 Export League Data to CSV")
                st.caption("Download full database dumps for Excel or record archives.")
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    bets_data = supabase.table("user_bets").select("*").execute().data
                    if bets_data:
                        df_bets = pd.DataFrame(bets_data)
                        st.download_button(
                            label="Download All User Bets (CSV)",
                            data=df_bets.to_csv(index=False),
                            file_name="touchdown_tokens_all_bets.csv",
                            mime="text/csv"
                        )
                
                with col_exp2:
                    users_data = supabase.table("profiles").select("full_name, tokens, favorite_team, bio").order("tokens", desc=True).execute().data
                    if users_data:
                        df_users = pd.DataFrame(users_data)
                        st.download_button(
                            label="Download Standings & Tokens (CSV)",
                            data=df_users.to_csv(index=False),
                            file_name="touchdown_tokens_standings.csv",
                            mime="text/csv"
                        )

            elif admin_sec == "League Chat Announcement":
                st.subheader("📢 Pre-Formatted League Announcement Generator")
                st.caption("Copy and paste this message directly into your WhatsApp or group chat!")
                
                ann_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="admin_ann_week")
                
                graded_q_badge_ann = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
                
                top_winner_str = "TBD"
                biggest_loser_str = "TBD"
                
                if graded_q_badge_ann:
                    ann_graded_w = graded_q_badge_ann[0]["week_number"]
                    w_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("week_number", ann_graded_w).execute().data
                    w_tds = supabase.table("touchdown_picks").select("*").eq("week_number", ann_graded_w).eq("is_correct", True).execute().data
                    
                    u_net = {}
                    for b in w_bets:
                        u = b['user_id']
                        w_ans = b.get("weekly_questions", {}).get("winning_answer")
                        if u not in u_net: u_net[u] = 0
                        if w_ans in ["Yes", "No"]:
                            if b['pick'] == w_ans: u_net[u] += b['wager_amount']
                            else: u_net[u] -= b['wager_amount']
                    for td in w_tds:
                        u = td['user_id']
                        u_net[u] = u_net.get(u, 0) + 5
                        
                    if u_net:
                        best_u_id = max(u_net, key=u_net.get)
                        worst_u_id = min(u_net, key=u_net.get)
                        
                        b_prof = supabase.table("profiles").select("full_name").eq("id", best_u_id).single().execute().data
                        w_prof = supabase.table("profiles").select("full_name").eq("id", worst_u_id).single().execute().data
                        
                        if b_prof and u_net[best_u_id] > 0:
                            top_winner_str = f"{b_prof['full_name']} (+{u_net[best_u_id]} tokens)"
                        if w_prof and u_net[worst_u_id] < 0:
                            biggest_loser_str = f"{w_prof['full_name']} ({u_net[worst_u_id]} tokens)"

                top_player_res = supabase.table("profiles").select("full_name, tokens").order("tokens", desc=True).limit(1).execute().data
                leader_str = f"{top_player_res[0]['full_name']} ({top_player_res[0]['tokens']} Tokens)" if top_player_res else "TBD"
                
                announcement_template = f"""🏈 *TOUCHDOWN TOKENS - WEEK {ann_week} IS LIVE!* 🏈

👑 *Current League Leader:* {leader_str}
🚀 *Biggest Winner Last Week:* {top_winner_str}
📉 *Wall Street Bets Award (Biggest Loss):* {biggest_loser_str}

⏰ *Kickoff Cutoff:* Sunday before 1st Kickoff

👉 Place your wagers and TD scorer pick now on Touchdown Tokens!
Good luck this week! 🔥"""
                
                st.code(announcement_template, language="markdown")

            elif admin_sec == "Archive & Reset Season":
                st.subheader("🧹 End-of-Season Reset & Archive Utility")
                st.caption("Archive final season standings and reset all active player balances back to 10 tokens for a fresh pre-season launch.")
                st.warning("⚠️ Action Warning: This will reset all active user token totals to 10!")
                
                season_label = st.text_input("Season Label", value="2026 Season Archive")
                confirm_check = st.checkbox("I confirm I wish to reset all user balances to 10 tokens for the new season.")
                
                if st.button("Archive & Reset Balances Now 🔄", type="primary", disabled=not confirm_check):
                    try:
                        all_profiles = supabase.table("profiles").select("id, full_name, tokens, favorite_team").order("tokens", desc=True).execute().data
                        
                        df_archive = pd.DataFrame(all_profiles)
                        df_archive["season_label"] = season_label
                        
                        for p in all_profiles:
                            supabase.table("profiles").update({"tokens": 10}).eq("id", p["id"]).execute()
                            
                        st.success("All player balances have been reset to 10 tokens! Season archived.")
                        st.download_button(
                            label="📥 Download Archived Season Summary (CSV)",
                            data=df_archive.to_csv(index=False),
                            file_name=f"{season_label.lower().replace(' ', '_')}_final.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error resetting season: {e}")

            elif admin_sec == "Season Champion Banner":
                st.subheader("🏆 End-of-Season Celebration Banner")
                st.caption("Enable this banner to show confetti and a gold Champion card on the Home tab when the season ends.")
                
                all_players = supabase.table("profiles").select("full_name").order("tokens", desc=True).execute().data
                player_names = [p["full_name"] for p in all_players] if all_players else ["Player"]
                
                champ_row = supabase.table("weekly_questions").select("*").eq("week_number", 999).execute().data
                current_state = champ_row[0]["winning_answer"] if champ_row else "OFF"
                current_champ = champ_row[0]["question_text"] if champ_row else player_names[0]
                
                banner_toggle = st.toggle("Enable Season Champion Banner", value=(current_state == "ON"))
                selected_champion = st.selectbox("Select Season Winner", player_names, index=player_names.index(current_champ) if current_champ in player_names else 0)
                
                if st.button("Save Champion Banner Settings 🏆"):
                    state_str = "ON" if banner_toggle else "OFF"
                    supabase.table("weekly_questions").delete().eq("week_number", 999).execute()
                    supabase.table("weekly_questions").insert({
                        "week_number": 999,
                        "question_number": 1,
                        "question_text": selected_champion,
                        "winning_answer": state_str
                    }).execute()
                    st.success("Updated Season Champion Banner settings!")
                    st.rerun()
