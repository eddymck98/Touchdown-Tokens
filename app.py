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

DEFAULT_QUESTION_TEMPLATES = [
    "Will QB 1 throw for over 250+ passing yards?",
    "Will RB 1 rush for 75+ rushing yards?",
    "Will WR 1 catch 6 or more receptions?",
    "Will Team A score a touchdown in the 1st quarter?",
    "Will there be a successful 50+ yard Field Goal kicked in Game A?",
    "Will Game B have over 45.5 combined points scored?",
    "Will any Defense record a pick-six or fumble recovery touchdown?",
    "Will TE 1 score a rushing or receiving touchdown?",
    "Will Game C go into Overtime?",
    "Will Team B record 3 or more sacks against Team C?"
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

    if profile.get("is_admin"):
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders, tab_admin = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "⚙️ Admin Control"]
        )
    else:
        tab_home, tab_profile, tab_rules, tab_bet, tab_history, tab_leaders = st.tabs(
            ["🏠 Home", "👤 Profile", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard"]
        )

    # ------------------------------------------
    # TAB 0: HOME
    # ------------------------------------------
    with tab_home:
        st.markdown(f"## Welcome back, {profile['full_name']}! 👋")
        
        st.markdown(f"""
            <div class="big-token-card">
                <div style="font-size: 16px; letter-spacing: 2px; text-transform: uppercase; color: #93c5fd;">Current Balance</div>
                <div class="big-token-number">{profile['tokens']} 🪙</div>
                <div style="font-size: 14px; color: #cbd5e1;">Touchdown Tokens</div>
            </div>
        """, unsafe_allow_html=True)

        user_bets_all = supabase.table("user_bets").select("*").eq("user_id", user_id).execute().data
        user_td_all = supabase.table("touchdown_picks").select("*").eq("user_id", user_id).eq("is_correct", True).execute().data
        
        earned_badges = []
        if profile['tokens'] >= 30:
            earned_badges.append("🚀 Token Tycoon")
        if any(b['wager_amount'] >= 10 for b in user_bets_all):
            earned_badges.append("🎯 High Roller")
        if len(user_td_all) >= 2:
            earned_badges.append("🏈 TD Guru")
        if profile['tokens'] == 0:
            earned_badges.append("📉 Down Bad")
            
        if earned_badges:
            st.markdown("#### Your Earned Badges")
            badges_html = "".join([f'<span class="badge-pill">{b}</span>' for b in earned_badges])
            st.markdown(badges_html, unsafe_allow_html=True)
            st.write("")

        st.divider()
        st.subheader("📊 Last Week's Performance Summary")
        
        graded_q = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
        
        if not graded_q:
            st.info("No weeks have been graded yet. Place your bets for Week 1 to get started!")
        else:
            latest_graded_week = graded_q[0]["week_number"]
            lw_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", user_id).eq("week_number", latest_graded_week).execute().data
            lw_td = supabase.table("touchdown_picks").select("*").eq("user_id", user_id).eq("week_number", latest_graded_week).execute().data
            
            if lw_bets or lw_td:
                bet_gains = sum(b["wager_amount"] for b in lw_bets if b.get("weekly_questions", {}).get("winning_answer") == b["pick"])
                bet_losses = sum(b["wager_amount"] for b in lw_bets if b.get("weekly_questions", {}).get("winning_answer") in ["Yes", "No"] and b.get("weekly_questions", {}).get("winning_answer") != b["pick"])
                td_bonus = 5 if (lw_td and lw_td[0].get("is_correct")) else 0
                net_total = bet_gains - bet_losses + td_bonus
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Net Tokens Earned", f"{'+' if net_total >= 0 else ''}{net_total} 🪙")
                col2.metric("Question Wins", f"+{bet_gains} 🪙")
                col3.metric("TD Scorer Bonus", f"+{td_bonus} 🪙")

    # ------------------------------------------
    # TAB 1: PROFILE
    # ------------------------------------------
    with tab_profile:
        st.header("👤 Customize Profile")
        
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
    # TAB 2: RULES
    # ------------------------------------------
    with tab_rules:
        st.header("📖 Rules & Information")
        st.write("""
        Each week I will release a new form with 10 scenarios. Each player starts with 10 tokens. 
        Winning bets double your wager, while wrong bets lose the tokens placed.
        Tokens are cumulative across the season!
        """)

    # ------------------------------------------
    # TAB 3: BETTING FORM & LOCKOUT TIMER
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        st.link_button("🏈 View NFL Scores, Lines & Fixtures ↗️", "https://www.espn.com/nfl/schedule", use_container_width=True)
        st.write("")

        weeks_res = supabase.table("weekly_questions").select("week_number").neq("week_number", 999).execute()
        available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
        
        if not available_weeks:
            st.info("No active questions available yet.")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            # Lockout Countdown Timer Check
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
                        st.error("🔒 Entries for this week are locked! The deadline has passed.")
                    else:
                        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        st.markdown(f"""
                            <div class="timer-card">
                                ⏳ <b>KICKOFF LOCKOUT COUNTDOWN:</b> <span style="font-size:20px; font-weight:bold; color:#fbbf24;">{hours}h {minutes}m {seconds}s remaining</span>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception:
                    pass
            
            if any(q.get("winning_answer") == "LOCKED" for q in questions):
                is_locked = True
                st.error("🔒 Entries for this week have been manually locked by the Admin.")

            if questions:
                all_week_bets = supabase.table("user_bets").select("question_id, pick").eq("week_number", selected_week).execute().data
                
                with st.form("weekly_bet_form"):
                    wagers = {}
                    picks = {}
                    st.markdown("### 10 Weekly Questions")
                    
                    for q in questions:
                        if q.get("winning_answer", "").startswith("LOCKTIME:"):
                            continue
                            
                        q_bets = [b for b in all_week_bets if b['question_id'] == q['id']]
                        if q_bets:
                            yes_cnt = sum(1 for b in q_bets if b['pick'] == "Yes")
                            pct_yes = int((yes_cnt / len(q_bets)) * 100)
                            st.markdown(f'<span class="consensus-badge">📊 League Pick: {pct_yes}% YES ({len(q_bets)} votes)</span>', unsafe_allow_html=True)

                        st.write(f"**Q{q['question_number']}: {q['question_text']}**")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            picks[q['id']] = st.radio(f"Pick Q{q['question_number']}", ["Yes", "No"], key=f"pick_{q['id']}", horizontal=True, disabled=is_locked)
                        with col2:
                            wagers[q['id']] = st.number_input(f"Wager Q{q['question_number']}", min_value=0, max_value=profile['tokens'], value=0, key=f"wager_{q['id']}", disabled=is_locked)
                        st.divider()

                    st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                    existing_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", selected_week).execute().data
                    default_td = existing_td[0]["player_name"] if existing_td else ""
                    td_pick = st.text_input("Player Name (e.g., Patrick Mahomes)", value=default_td, key="td_scorer", disabled=is_locked)
                    
                    total_wagered = sum(wagers.values())
                    st.progress(min(1.0, total_wagered / max(1, profile['tokens'])), text=f"**Tokens Wagered:** `{total_wagered}` / `{profile['tokens']}` Tokens")
                    
                    submit_bet = st.form_submit_button("Submit Weekly Bets 🚀", type="primary", use_container_width=True, disabled=is_locked)
                    
                    if submit_bet and not is_locked:
                        if total_wagered > profile['tokens']:
                            st.error(f"Cannot wager {total_wagered} tokens! Balance: {profile['tokens']} tokens.")
                        else:
                            for q_id, pick_val in picks.items():
                                supabase.table("user_bets").delete().eq("user_id", user_id).eq("question_id", q_id).execute()
                                supabase.table("user_bets").insert({"user_id": user_id, "week_number": selected_week, "question_id": q_id, "pick": pick_val, "wager_amount": wagers[q_id]}).execute()
                            if td_pick:
                                supabase.table("touchdown_picks").delete().eq("user_id", user_id).eq("week_number", selected_week).execute()
                                supabase.table("touchdown_picks").insert({"user_id": user_id, "week_number": selected_week, "player_name": td_pick}).execute()
                            st.success("Bets submitted successfully!")

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
                formatted_data.append({
                    "Week": b["week_number"],
                    "Question": q_info.get("question_text", "N/A"),
                    "Your Pick": b["pick"],
                    "Wager": b["wager_amount"],
                    "Result": "✅ Won" if b["pick"] == w_ans else ("❌ Lost" if w_ans in ["Yes", "No"] else "Pending")
                })
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 5: LEADERBOARD & TRASH TALK
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 Player Standings")
        leader_res = supabase.table("profiles").select("full_name, tokens, favorite_team, bio, avatar_emoji").order("tokens", desc=True).execute().data
        
        if leader_res:
            leader_data = []
            for idx, p in enumerate(leader_res):
                av = p.get("avatar_emoji") or "🏈"
                team_name = p.get("favorite_team") or "🏈 Free Agent / Neutral"
                t_info = NFL_TEAM_DATA.get(team_name, NFL_TEAM_DATA["🏈 Free Agent / Neutral"])
                leader_data.append({"Rank": f"#{idx + 1}", "Logo": t_info["logo"], "Player": f"{av} {p['full_name']}", "Team": team_name, "Tokens": f"{p['tokens']} 🪙", "Catchphrase": p.get("bio", "")})
            
            st.dataframe(pd.DataFrame(leader_data), column_config={"Logo": st.column_config.ImageColumn("Badge", width="small")}, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("💬 League Trash Talk Feed")
        with st.form("trash_talk_form"):
            chat_msg = st.text_input("Post a message...", key="chat_input")
            if st.form_submit_button("Post Message 💬") and chat_msg.strip():
                supabase.table("trash_talk").insert({"user_id": user_id, "message": chat_msg.strip()}).execute()
                st.rerun()

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
    # TAB 6: ADMIN CONTROL
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            admin_sec = st.radio("Select Action", ["Create Questions", "Set Lockout Timer", "Grade Week & Calculate Points", "Adjust User Tokens"], horizontal=True)
            
            # A. Create Questions with Template Auto-Fill
            if admin_sec == "Create Questions":
                st.subheader("Add 10 New Weekly Questions")
                new_week = st.number_input("Week Number", min_value=1, max_value=24, step=1)
                
                if st.button("📋 Load 10 Default Question Templates"):
                    for i, t_q in enumerate(DEFAULT_QUESTION_TEMPLATES):
                        st.session_state[f"q_input_w{new_week}_q{i+1}"] = t_q
                    st.success("Default templates loaded! Customize them below.")

                with st.form(key=f"create_qs_form_{new_week}"):
                    q_inputs = []
                    for i in range(1, 11):
                        def_val = st.session_state.get(f"q_input_w{new_week}_q{i}", "")
                        q_inputs.append(st.text_input(f"Question {i}", value=def_val, key=f"q_input_field_{i}"))
                    
                    if st.form_submit_button("Publish Questions 🚀"):
                        for idx, q_text in enumerate(q_inputs):
                            if q_text.strip():
                                supabase.table("weekly_questions").insert({"week_number": new_week, "question_number": idx + 1, "question_text": q_text.strip(), "winning_answer": "Pending"}).execute()
                        st.success(f"Published Week {new_week} questions!")
                        st.rerun()

            # B. Admin Lockout Timer Control
            elif admin_sec == "Set Lockout Timer":
                st.subheader("⏳ Set Weekly Kickoff Lockout Time")
                lock_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="admin_lock_week")
                
                lock_date = st.date_input("Lock Date")
                lock_time = st.time_input("Lock Time (UTC / EST Cutoff)")
                
                if st.button("Save Lockout Time 🔒"):
                    combined_dt = datetime.combine(lock_date, lock_time).isoformat()
                    supabase.table("weekly_questions").delete().eq("week_number", lock_week).eq("question_number", 99).execute()
                    supabase.table("weekly_questions").insert({
                        "week_number": lock_week,
                        "question_number": 99,
                        "question_text": "WEEK LOCKOUT TIMESTAMP",
                        "winning_answer": f"LOCKTIME:{combined_dt}"
                    }).execute()
                    st.success(f"Week {lock_week} lockout set for {combined_dt}!")

            # C. Grade Week & Calculate Points
            elif admin_sec == "Grade Week & Calculate Points":
                st.subheader("Grade Weekly Results")
                grade_week = st.number_input("Week Number to Grade", min_value=1, max_value=24, step=1)
                week_q = supabase.table("weekly_questions").select("*").eq("week_number", grade_week).order("question_number").execute().data
                
                if week_q:
                    with st.form("grade_form"):
                        answers = {}
                        for q in week_q:
                            if q.get("winning_answer", "").startswith("LOCKTIME:"):
                                continue
                            answers[q["id"]] = st.selectbox(f"Q{q['question_number']}: {q['question_text']}", ["Pending", "Yes", "No"], key=f"ans_{q['id']}")
                        
                        if st.form_submit_button("Calculate & Process Payouts 🏆"):
                            for q_id, ans in answers.items():
                                supabase.table("weekly_questions").update({"winning_answer": ans}).eq("id", q_id).execute()
                            st.success("Graded successfully!")

            # D. Manual Token Overrides
            elif admin_sec == "Adjust User Tokens":
                st.subheader("Manual Token Override")
                all_users = supabase.table("profiles").select("id, full_name, tokens").execute().data
                user_dict = {u["full_name"]: u for u in all_users}
                selected_user_name = st.selectbox("Select Player", list(user_dict.keys()))
                
                if selected_user_name:
                    target_user = user_dict[selected_user_name]
                    new_token_val = st.number_input("Set Token Total", min_value=0, value=target_user["tokens"])
                    if st.button("Update Tokens"):
                        supabase.table("profiles").update({"tokens": new_token_val}).eq("id", target_user["id"]).execute()
                        st.success("Tokens updated!")
