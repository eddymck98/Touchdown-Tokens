import streamlit as st
import pandas as pd
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

# Fetch current user team for theme colors if logged in
user_team_color = "#fbbf24"
if st.session_state.user:
    try:
        res = supabase.table("profiles").select("favorite_team").eq("id", st.session_state.user.id).single().execute()
        if res.data:
            t_name = res.data.get("favorite_team", "🏈 Free Agent / Neutral")
            user_team_color = NFL_TEAM_DATA.get(t_name, {}).get("color", "#fbbf24")
    except Exception:
        pass

# Dynamic Styling injection
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Teko:wght@700&display=swap');

    .stApp, div[data-testid="stAppViewContainer"] {{
        background: 
            radial-gradient(circle at 50% 20%, rgba(15, 23, 42, 0.8), rgba(7, 13, 25, 0.96)),
            url('https://images.unsplash.com/photo-1566577739112-5180d4bf9390?auto=format&fit=crop&w=1920&q=80') center center / cover no-repeat fixed !important;
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: #030712 !important;
        border-right: 3px solid {user_team_color} !important;
    }}
    
    .nfl-header {{ text-align: center; padding: 10px 0 5px 0; }}
    .nfl-title {{
        font-family: 'Bebas Neue', cursive, sans-serif !important;
        font-size: 64px !important;
        letter-spacing: 4px;
        text-transform: uppercase;
        background: linear-gradient(180deg, #ffffff 20%, {user_team_color} 70%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px {user_team_color}88;
        margin: 0;
        line-height: 1.0;
    }}
    .nfl-subtitle {{
        font-family: 'Teko', sans-serif;
        font-size: 22px;
        letter-spacing: 3px;
        color: #93c5fd;
        text-transform: uppercase;
        margin-top: -5px;
    }}
    .header-logo {{
        width: 90px;
        filter: drop-shadow(0px 6px 15px {user_team_color}aa);
    }}
    
    @keyframes teamPulse {{
        0% {{ box-shadow: 0 0 10px {user_team_color}33; }}
        50% {{ box-shadow: 0 0 25px {user_team_color}99; }}
        100% {{ box-shadow: 0 0 10px {user_team_color}33; }}
    }}

    .big-token-card {{
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.95) 0%, rgba(6, 10, 18, 0.95) 100%);
        padding: 30px;
        border-radius: 18px;
        color: #ffffff !important;
        text-align: center;
        border: 2px solid {user_team_color};
        margin-bottom: 25px;
        backdrop-filter: blur(8px);
        animation: teamPulse 3.5s infinite ease-in-out;
    }}
    .big-token-number {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 68px;
        letter-spacing: 2px;
        margin: 0;
        color: {user_team_color} !important;
        text-shadow: 0px 4px 15px {user_team_color}88;
    }}

    .champion-card {{
        background: linear-gradient(135deg, #78350f 0%, #b45309 50%, #f59e0b 100%);
        padding: 30px;
        border-radius: 16px;
        color: #ffffff !important;
        text-align: center;
        border: 3px solid #fbbf24;
        margin-bottom: 30px;
        animation: teamPulse 2s infinite ease-in-out;
    }}

    .matchup-card {{
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #334155;
        border-left: 5px solid {user_team_color};
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }}

    .trophy-card-unlocked {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 2px solid {user_team_color};
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 0 12px {user_team_color}44;
    }}

    .trophy-card-locked {{
        background: rgba(15, 23, 42, 0.5);
        border: 1px dashed #475569;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        opacity: 0.55;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] > label {{
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        margin-right: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
        border-color: {user_team_color} !important;
        box-shadow: 0 0 10px {user_team_color}55 !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {{
        background: linear-gradient(135deg, {user_team_color}33 0%, rgba(15,23,42,0.9) 100%) !important;
        border: 2px solid {user_team_color} !important;
        box-shadow: 0 0 12px {user_team_color}aa !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] * {{
        color: #ffffff !important;
        font-weight: 800 !important;
    }}

    .matchup-team-title {{
        font-family: 'Teko', sans-serif;
        font-size: 20px;
        letter-spacing: 1px;
        color: #fbbf24;
        text-transform: uppercase;
    }}

    .timer-card {{
        background: rgba(15, 23, 42, 0.9);
        border: 2px solid {user_team_color};
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }}

    .badge-pill {{
        display: inline-block;
        background-color: #1e293b;
        color: {user_team_color};
        border: 1px solid {user_team_color};
        border-radius: 20px;
        padding: 5px 12px;
        font-size: 13px;
        font-weight: 700;
        margin: 3px;
    }}
    
    .consensus-badge {{
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }}
    
    .chat-bubble {{
        background-color: rgba(15, 23, 42, 0.9);
        border-left: 5px solid #fbbf24;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}

    .summary-box {{
        background-color: rgba(15, 23, 42, 0.9) !important;
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
        padding: 10px 18px !important;
        margin-right: 4px !important;
    }}
    button[data-baseweb="tab"] * {{
        font-family: 'Teko', sans-serif !important;
        font-size: 18px !important;
        letter-spacing: 1px !important;
        color: #cbd5e1 !important;
    }}
    button[aria-selected="true"] {{
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important;
        border: 2px solid {user_team_color} !important;
        box-shadow: 0 4px 15px {user_team_color}66 !important;
    }}
    button[aria-selected="true"] * {{
        color: {user_team_color} !important;
    }}

    div.stButton > button[kind="primary"], div.stFormSubmitButton > button {{
        background: linear-gradient(135deg, {user_team_color} 0%, #d97706 100%) !important;
        color: #000000 !important;
        font-family: 'Teko', sans-serif !important;
        font-size: 22px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease-in-out !important;
    }}
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 18px {user_team_color}88 !important;
    }}

    .stTextInput > label, .stNumberInput > label, .stRadio > label, .stSelectbox > label {{
        color: #f8fafc !important;
        font-weight: 700 !important;
    }}
    .stTextInput input, .stNumberInput input {{
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Header NFL Shield Banner
st.markdown("""
    <div class="nfl-header">
        <img src="https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg" class="header-logo" alt="NFL Logo" />
        <h1 class="nfl-title">TOUCHDOWN TOKENS</h1>
        <div class="nfl-subtitle">Weekly NFL Predictions & Wagers</div>
    </div>
""", unsafe_allow_html=True)
st.write("")

# Helper function to compute player badges
def get_user_badges(target_user_id):
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
    
    st.sidebar.title(f"{user_avatar} {profile['full_name']}")
    st.sidebar.image(team_data["logo"], width=55)
    st.sidebar.caption(f"Team: {user_team}")
    st.sidebar.metric(label="Available Tokens", value=f"{profile['tokens']} 🪙")
    
    if profile.get("is_admin"):
        st.sidebar.success("👑 Admin Mode Active")
        
    if st.sidebar.button("Log Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Reordered Tabs with original descriptive names
    if profile.get("is_admin"):
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_trophies, tab_admin = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏆 Trophy Cabinet", "⚙️ Admin Control"]
        )
    else:
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_trophies = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "🏆 Trophy Cabinet"]
        )

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
                    <div style="font-size: 20px; letter-spacing: 2px; text-transform: uppercase;">🏆 LEAGUE CHAMPION DECLARED 🏆</div>
                    <div style="font-size: 48px; font-weight: 900; margin: 10px 0;">{champ_name}</div>
                    <div style="font-size: 16px;">Congratulations to the Touchdown Tokens Champion! 👑</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"## Welcome back, {profile['full_name']}! 👋")
        
        st.markdown(f"""
            <div class="big-token-card">
                <div style="font-size: 16px; letter-spacing: 2px; text-transform: uppercase; color: #93c5fd;">Current Balance</div>
                <div class="big-token-number">{profile['tokens']} 🪙</div>
                <div style="font-size: 14px; color: #cbd5e1;">Touchdown Tokens</div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📊 Last Week's Performance Summary")
        
        graded_q_badge = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
        
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
    # TAB 1: PROFILE
    # ------------------------------------------
    with tab_profile:
        st.header("👤 Customize Profile")
        st.caption("Personalize how your profile appears on the Leaderboard and Trash Talk feed!")
        
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

        weeks_res = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute()
        available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
        
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
                
                with st.form("weekly_bet_form"):
                    wagers = {}
                    picks = {}
                    
                    st.markdown("### 10 Weekly Questions")
                    st.caption("Double your betted tokens if correct! Lose betted tokens if wrong.")
                    
                    for q in questions:
                        if q.get("winning_answer", "").startswith("LOCKTIME:"):
                            continue
                            
                        st.markdown('<div class="matchup-card">', unsafe_allow_html=True)
                        
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

                        col_away_logo, col_matchup_txt, col_home_logo = st.columns([1, 4, 1])
                        with col_away_logo:
                            st.image(away_info["logo"], width=45)
                        with col_matchup_txt:
                            st.markdown(f"""
                                <div style="text-align:center; padding-top:4px;">
                                    <span class="matchup-team-title">{away_team_name}</span>
                                    <span style="color:#cbd5e1; font-weight:bold; margin: 0 8px;">@</span>
                                    <span class="matchup-team-title">{home_team_name}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_home_logo:
                            st.image(home_info["logo"], width=45)

                        q_bets = [b for b in all_week_bets if b['question_id'] == q['id']]
                        if q_bets:
                            yes_cnt = sum(1 for b in q_bets if b['pick'] == "Yes")
                            pct_yes = int((yes_cnt / len(q_bets)) * 100)
                            st.markdown(f'<span class="consensus-badge">📊 League Pick: {pct_yes}% YES ({len(q_bets)} votes)</span>', unsafe_allow_html=True)

                        st.markdown(f"**Q{q['question_number']}: {prompt_text}**")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            picks[q['id']] = st.radio(
                                f"Pick for Q{q['question_number']}", 
                                ["Yes", "No"], 
                                key=f"pick_{q['id']}", 
                                horizontal=True,
                                disabled=is_locked
                            )
                        with col2:
                            wagers[q['id']] = st.number_input(
                                f"Wager (Tokens) Q{q['question_number']}", 
                                min_value=0, 
                                max_value=profile['tokens'], 
                                value=0, 
                                key=f"wager_{q['id']}",
                                disabled=is_locked
                            )
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                    st.caption("Name 1 player to score a TD this week (Rushing/Receiving only!). Correct pick = Bonus Tokens!")
                    
                    existing_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", selected_week).execute().data
                    default_td = existing_td[0]["player_name"] if existing_td else ""
                    
                    td_pick = st.text_input("Player Name (e.g., Patrick Mahomes)", value=default_td, key="td_scorer", disabled=is_locked)
                    
                    total_wagered = sum(wagers.values())
                    max_available = max(1, profile['tokens'])
                    progress_val = min(1.0, total_wagered / max_available)
                    pct_str = int(progress_val * 100)
                    
                    st.progress(
                        progress_val, 
                        text=f"**Tokens Wagered:** `{total_wagered}` / `{profile['tokens']}` Tokens ({pct_str}%)"
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
                                
                            st.success("Your bets and touchdown pick have been submitted!")

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
            leader_data = []
            
            for idx, p in enumerate(leader_res):
                av = p.get("avatar_emoji") or "🏈"
                team_name = p.get("favorite_team") or "🏈 Free Agent / Neutral"
                t_info = NFL_TEAM_DATA.get(team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                
                p_badges = get_user_badges(p["id"])
                badge_str = f"🏆 {len(p_badges)} Badges"
                
                leader_data.append({
                    "Rank": f"#{idx + 1}",
                    "Logo": t_info["logo"],
                    "Player": f"{av} {p['full_name']}",
                    "Team": team_name,
                    "Trophies": badge_str,
                    "Tokens": f"{p['tokens']} 🪙",
                    "Catchphrase": p.get("bio", "")
                })
                
            st.dataframe(
                pd.DataFrame(leader_data),
                column_config={"Logo": st.column_config.ImageColumn("Badge", width="small")},
                use_container_width=True,
                hide_index=True
            )

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
                <div class="chat-bubble" style="border-left-color: {t_info['color']};">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <img src="{t_info['logo']}" style="width:28px; height:28px;" />
                        <b>{author_av} {author_name}</b> <small style="opacity:0.7;">({author_team})</small>
                    </div>
                    <div style="margin-top:6px;">{c['message']}</div>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 6: TROPHY CABINET
    # ------------------------------------------
    with tab_trophies:
        st.header("🏆 League Virtual Trophy Cabinet")
        st.caption("Inspect badge collections across the league and unlock dynamic silverware!")
        
        all_league_profiles = supabase.table("profiles").select("id, full_name, avatar_emoji, favorite_team").execute().data
        user_name_map = {p["full_name"]: p for p in all_league_profiles}
        
        selected_player_name = st.selectbox("Select Player Trophy Showcase", list(user_name_map.keys()))
        selected_player = user_name_map[selected_player_name]
        
        selected_badges = get_user_badges(selected_player["id"])
        selected_team_info = NFL_TEAM_DATA.get(selected_player.get("favorite_team"), NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
        
        col_t_logo, col_t_info = st.columns([1, 4])
        with col_t_logo:
            st.image(selected_team_info["logo"], width=70)
        with col_t_info:
            st.markdown(f"### {selected_player.get('avatar_emoji', '🏈')} {selected_player['full_name']}'s Showcase")
            st.markdown(f"**Unlocked:** `{len(selected_badges)}` / `{len(MASTER_BADGES)}` Badges")
        
        st.divider()
        
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
    # TAB 7: ADMIN CONTROL
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            
            admin_sec = st.radio("Select Action", ["Create Questions", "Set Lockout Timer", "Grade Week & Calculate Points", "Adjust User Tokens", "Export League Data (CSV)", "League Chat Announcement", "Archive & Reset Season", "Season Champion Banner"], horizontal=True)
            
            # Sub-Section A: Enter Questions with Matchup Dropdowns
            if admin_sec == "Create Questions":
                st.subheader("Add 10 New Weekly Questions")
                new_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="admin_week_selector")
                
                if st.button("📋 Load 10 Default Question Templates"):
                    for i, t_q in enumerate(DEFAULT_QUESTION_TEMPLATES):
                        st.session_state[f"q_prompt_w{new_week}_q{i+1}"] = t_q
                    st.success("Default templates loaded! Customize them below.")

                existing_qs = supabase.table("weekly_questions").select("id").eq("week_number", new_week).execute().data
                
                if existing_qs:
                    st.warning(f"⚠️ Questions for Week {new_week} have already been published! ({len(existing_qs)} questions found)")
                    if st.button("Delete Week Questions to Start Fresh"):
                        supabase.table("weekly_questions").delete().eq("week_number", new_week).execute()
                        st.success(f"Cleared Week {new_week} questions.")
                        st.rerun()
                else:
                    with st.form(key=f"create_questions_form_week_{new_week}"):
                        q_data_to_save = []
                        
                        for i in range(1, 11):
                            st.markdown(f"#### Question {i}")
                            col_m1, col_m2 = st.columns(2)
                            with col_m1:
                                away_t = st.selectbox(f"Q{i} Away Team", NFL_TEAMS, key=f"q{i}_away_team_sel")
                            with col_m2:
                                home_t = st.selectbox(f"Q{i} Home Team", NFL_TEAMS, key=f"q{i}_home_team_sel")
                                
                            def_val = st.session_state.get(f"q_prompt_w{new_week}_q{i}", "")
                            prompt_val = st.text_input(f"Question {i} Prompt", value=def_val, key=f"q_prompt_input_w{new_week}_q{i}")
                            
                            q_data_to_save.append({
                                "prompt": prompt_val.strip(),
                                "away": away_t,
                                "home": home_t
                            })
                            st.divider()
                        
                        submit_qs = st.form_submit_button("Publish All 10 Questions 🚀")
                    
                    if submit_qs:
                        valid_items = [q for q in q_data_to_save if q["prompt"]]
                        if len(valid_items) == 0:
                            st.error("Please enter at least one question prompt before publishing.")
                        else:
                            for idx, q_item in enumerate(q_data_to_save):
                                if q_item["prompt"]:
                                    full_combined_str = f"{q_item['prompt']} | MATCHUP: {q_item['away']} @ {q_item['home']}"
                                    supabase.table("weekly_questions").insert({
                                        "week_number": new_week,
                                        "question_number": idx + 1,
                                        "question_text": full_combined_str,
                                        "winning_answer": "Pending"
                                    }).execute()
                            st.success(f"Successfully published questions for Week {new_week}!")
                            st.rerun()

            # Sub-Section B: Set Lockout Timer
            elif admin_sec == "Set Lockout Timer":
                st.subheader("⏳ Set Weekly Kickoff Lockout Time")
                lock_week = st.number_input("Select Week", min_value=1, max_value=24, step=1, key="admin_lock_week")
                
                lock_date = st.date_input("Lockout Date")
                lock_time = st.time_input("Lockout Time (UTC / Kickoff Cutoff)")
                
                if st.button("Save Lockout Cutoff 🔒"):
                    combined_dt = datetime.combine(lock_date, lock_time).isoformat()
                    supabase.table("weekly_questions").delete().eq("week_number", lock_week).eq("question_number", 99).execute()
                    supabase.table("weekly_questions").insert({
                        "week_number": lock_week,
                        "question_number": 99,
                        "question_text": "WEEK LOCKOUT TIMESTAMP",
                        "winning_answer": f"LOCKTIME:{combined_dt}"
                    }).execute()
                    st.success(f"Lockout set for Week {lock_week} at {combined_dt} UTC!")

            # Sub-Section C: Grade Week & Calculate Points
            elif admin_sec == "Grade Week & Calculate Points":
                st.subheader("Grade Weekly Results")
                grade_week = st.number_input("Select Week to Grade", min_value=1, max_value=24, step=1, key="grade_week_num")
                
                week_q = supabase.table("weekly_questions").select("*").eq("week_number", grade_week).order("question_number").execute().data
                
                if not week_q:
                    st.warning("No questions found for this week.")
                else:
                    with st.form("grade_form"):
                        answers = {}
                        for q in week_q:
                            if q.get("winning_answer", "").startswith("LOCKTIME:"):
                                continue
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
                                
                            st.success("Scores graded and user token balances updated!")

            # Sub-Section D: Manual Token Overrides
            elif admin_sec == "Adjust User Tokens":
                st.subheader("Manual Token Override")
                all_users = supabase.table("profiles").select("id, full_name, tokens").execute().data
                
                user_dict = {u["full_name"]: u for u in all_users}
                selected_user_name = st.selectbox("Select Player", list(user_dict.keys()))
                
                if selected_user_name:
                    target_user = user_dict[selected_user_name]
                    st.write(f"Current Token Total: **{target_user['tokens']}**")
                    new_token_val = st.number_input("Set New Token Total", min_value=0, value=target_user["tokens"])
                    
                    if st.button("Update Player Tokens"):
                        supabase.table("profiles").update({"tokens": new_token_val}).eq("id", target_user["id"]).execute()
                        st.success(f"Updated {selected_user_name}'s tokens to {new_token_val}!")

            # Export League Data (CSV)
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

            # Pre-Formatted WhatsApp / League Chat Announcement
            elif admin_sec == "League Chat Announcement":
                st.subheader("📢 Pre-Formatted League Announcement Generator")
                st.caption("Copy and paste this message directly into your WhatsApp or group chat!")
                
                ann_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="ann_week_input")
                top_player_res = supabase.table("profiles").select("full_name, tokens").order("tokens", desc=True).limit(1).execute().data
                leader_str = f"{top_player_res[0]['full_name']} ({top_player_res[0]['tokens']} Tokens)" if top_player_res else "TBD"
                
                announcement_template = f"""🏈 *TOUCHDOWN TOKENS - WEEK {ann_week} IS LIVE!* 🏈

🪙 *Current League Leader:* {leader_str}
⏰ *Kickoff Cutoff:* Sunday before 1st Kickoff

👉 Place your wagers and TD scorer pick now on Touchdown Tokens!
Good luck this week! 🚀"""
                
                st.code(announcement_template, language="markdown")

            # One-Click Season Reset / Archive Tool
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

            # Sub-Section G: Champion Banner Toggle
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
