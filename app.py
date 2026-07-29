import streamlit as st
from supabase import create_client, Client

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Touchdown Tokens", page_icon="🏈", layout="centered")

st.title("🏈 Touchdown Tokens")

# --- AUTHENTICATION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN / SIGNUP INTERFACE ---
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    with tab1:
        st.subheader("Player Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab2:
        st.subheader("Register New Account")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        full_name = st.text_input("Full Name")
        if st.button("Sign Up"):
            try:
                res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                if res.user:
                    # Create profile with default 10 tokens
                    supabase.table("profiles").insert({
                        "id": res.user.id,
                        "email": new_email,
                        "full_name": full_name,
                        "tokens": 10,
                        "is_admin": False
                    }).execute()
                    st.success("Account created! You can now log in.")
            except Exception as e:
                st.error(f"Sign up failed: {e}")

# --- MAIN LOGGED-IN DASHBOARD ---
else:
    user_id = st.session_state.user.id
    
    # Fetch User Profile & Tokens
    profile_data = supabase.table("profiles").select("*").eq("id", user_id).single().execute().data
    
    st.sidebar.write(f"Logged in as: **{profile_data.get('full_name', 'Player')}**")
    st.sidebar.metric(label="Current Token Balance", value=f"{profile_data['tokens']} 🪙")
    
    if st.sidebar.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # App Navigation Tabs
    menu = st.tabs(["🎯 Place Bets", "📜 My History", "🏆 Leaderboard"])
    
    if profile_data.get("is_admin"):
        admin_tab = st.sidebar.expander("⚙️ Admin Panel")
        with admin_tab:
            st.write("Manage weekly questions, enter results, and override player tokens.")

    # TAB 1: BETTING FORM
    with menu[0]:
        st.header("Weekly Picks")
        st.info(f"You have **{profile_data['tokens']} tokens** available to wager this week.")
        
        # Pull Active Questions for the Current Week
        # (Form fields and wagering logic render here)

    # TAB 2: HISTORY
    with menu[1]:
        st.header("Your Past Bets & Results")
        
    # TAB 3: LEADERBOARD
    with menu[2]:
        st.header("Player Standings")
        leaders = supabase.table("profiles").select("full_name, tokens").order("tokens", desc=True).execute().data
        st.table(leaders)
