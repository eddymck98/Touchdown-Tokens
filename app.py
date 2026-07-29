import streamlit as st
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

# Custom CSS styling
st.markdown("""
    <style>
    .metric-box { padding: 15px; border-radius: 10px; background-color: #f0f2f6; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🏈 Touchdown Tokens")

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
                        # Initialize user profile with default 10 tokens
                        supabase.table("profiles").insert({
                            "id": res.user.id,
                            "email": reg_email,
                            "full_name": reg_name,
                            "tokens": 10,
                            "is_admin": False
                        }).execute()
                        st.success("Account created! You can now log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

# ==========================================
# 2. MAIN LOGGED-IN GAME PORTAL
# ==========================================
else:
    user_id = st.session_state.user.id
    
    # Fetch user details
    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    # Sidebar Info
    st.sidebar.title(f"👤 {profile['full_name']}")
    st.sidebar.metric(label="Available Tokens", value=f"{profile['tokens']} 🪙")
    
    if profile.get("is_admin"):
        st.sidebar.success("👑 Admin Mode Active")
        
    if st.sidebar.button("Log Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Determine main app tabs
    if profile.get("is_admin"):
        tab_bet, tab_history, tab_leaders, tab_admin = st.tabs(
            ["🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "⚙️ Admin Control"]
        )
    else:
        tab_bet, tab_history, tab_leaders = st.tabs(
            ["🎯 Place Bets", "📜 My History", "🏆 Leaderboard"]
        )

    # ------------------------------------------
    # TAB 1: BETTING FORM & QUESTION SUBMISSION
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        
        # Select active week
        weeks_res = supabase.table("weekly_questions").select("week_number").execute()
        available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
        
        if not available_weeks:
            st.info("No active questions available yet. Check back soon when the Admin posts Week 1!")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            
            # Fetch questions for selected week
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            if not questions:
                st.info("No questions found for this week.")
            else:
                with st.form("weekly_bet_form"):
                    wagers = {}
                    picks = {}
                    
                    st.markdown("### 10 Weekly Questions")
                    st.caption("Double your betted tokens if correct! Lose betted tokens if wrong.")
                    
                    for q in questions:
                        st.write(f"**Q{q['question_number']}: {q['question_text']}**")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            picks[q['id']] = st.radio(
                                f"Pick for Q{q['question_number']}", 
                                ["Yes", "No"], 
                                key=f"pick_{q['id']}", 
                                horizontal=True
                            )
                        with col2:
                            wagers[q['id']] = st.number_input(
                                f"Wager (Tokens) Q{q['question_number']}", 
                                min_value=0, 
                                max_value=profile['tokens'], 
                                value=0, 
                                key=f"wager_{q['id']}"
                            )
                        st.divider()

                    st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                    st.caption("Name 1 player to score a TD this week. Correct pick = +5 Bonus Tokens!")
                    td_pick = st.text_input("Player Name (e.g., Patrick Mahomes)", key="td_scorer")
                    
                    total_wagered = sum(wagers.values())
                    st.markdown(f"**Total Tokens Wagered:** `{total_wagered}` / `{profile['tokens']}`")
                    
                    submit_bet = st.form_submit_button("Submit Weekly Bets 🚀", type="primary", use_container_width=True)
                    
                    if submit_bet:
                        if total_wagered > profile['tokens']:
                            st.error(f"Cannot wager {total_wagered} tokens! You only have {profile['tokens']} tokens available.")
                        else:
                            # Process bets insertion/update
                            for q_id, pick_val in picks.items():
                                w_amt = wagers[q_id]
                                # Clear existing bet for this question
                                supabase.table("user_bets").delete().eq("user_id", user_id).eq("question_id", q_id).execute()
                                # Insert new bet
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
    # TAB 2: USER HISTORY
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
                outcome = "Pending"
                if q_info and q_info.get("winning_answer") != "Pending":
                    if b["pick"] == q_info["winning_answer"]:
                        outcome = f"✅ Won (+{b['wager_amount'] * 2} Tokens)"
                    else:
                        outcome = f"❌ Lost (-{b['wager_amount']} Tokens)"
                        
                formatted_data.append({
                    "Week": b["week_number"],
                    "Question": q_info.get("question_text", "N/A"),
                    "Your Pick": b["pick"],
                    "Wager": b["wager_amount"],
                    "Winner": q_info.get("winning_answer", "Pending"),
                    "Result": outcome
                })
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 3: LEADERBOARD
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 Player Standings")
        leader_res = supabase.table("profiles").select("full_name, tokens").order("tokens", desc=True).execute().data
        
        if leader_res:
            st.dataframe(leader_res, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # TAB 4: ADMIN PANEL (ADMINS ONLY)
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            
            admin_sec = st.radio("Select Action", ["Create Questions", "Grade Week & Calculate Points", "Adjust User Tokens"], horizontal=True)
            
            # Sub-Section A: Enter Questions
            if admin_sec == "Create Questions":
                st.subheader("Add 10 New Weekly Questions")
                new_week = st.number_input("Week Number", min_value=1, max_value=24, step=1)
                
                with st.form("admin_create_questions"):
                    q_inputs = []
                    for i in range(1, 11):
                        q_inputs.append(st.text_input(f"Question {i} Text", key=f"q_text_{i}"))
                    
                    if st.form_submit_button("Publish Questions"):
                        for idx, q_text in enumerate(q_inputs):
                            if q_text:
                                supabase.table("weekly_questions").insert({
                                    "week_number": new_week,
                                    "question_number": idx + 1,
                                    "question_text": q_text,
                                    "winning_answer": "Pending"
                                }).execute()
                        st.success(f"Week {new_week} questions published successfully!")

            # Sub-Section B: Grade & Calculate Scores
            elif admin_sec == "Grade Week & Calculate Points":
                st.subheader("Grade Weekly Results")
                grade_week = st.number_input("Select Week to Grade", min_value=1, max_value=24, step=1)
                
                week_q = supabase.table("weekly_questions").select("*").eq("week_number", grade_week).order("question_number").execute().data
                
                if not week_q:
                    st.warning("No questions found for this week.")
                else:
                    with st.form("grade_form"):
                        answers = {}
                        for q in week_q:
                            answers[q["id"]] = st.selectbox(
                                f"Q{q['question_number']}: {q['question_text']}", 
                                ["Pending", "Yes", "No"], 
                                key=f"ans_{q['id']}"
                            )
                        
                        st.markdown("#### Touchdown Scorer Correct Picks")
                        td_picks_data = supabase.table("touchdown_picks").select("*, profiles(full_name)").eq("week_number", grade_week).execute().data
                        td_winners = []
                        for td in td_picks_data:
                            user_name = td.get("profiles", {}).get("full_name", "User")
                            if st.checkbox(f"{user_name} picked: '{td['player_name']}'", key=f"td_{td['id']}"):
                                td_winners.append(td["user_id"])

                        if st.form_submit_button("Calculate & Process Payouts", type="primary"):
                            # Update winning answers in DB
                            for q_id, ans in answers.items():
                                supabase.table("weekly_questions").update({"winning_answer": ans}).eq("id", q_id).execute()
                            
                            # Fetch all bets for this week
                            week_bets = supabase.table("user_bets").select("*").eq("week_number", grade_week).execute().data
                            
                            # Payout calculations
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
                                        user_token_changes[u_id] += wager # Net profit (doubled bet)
                                    else:
                                        user_token_changes[u_id] -= wager # Lose wagered tokens
                            
                            # Add TD Scorer bonuses (+5 Tokens)
                            for winner_id in td_winners:
                                user_token_changes[winner_id] = user_token_changes.get(winner_id, 0) + 5
                            
                            # Apply balance changes to user profiles
                            for u_id, change in user_token_changes.items():
                                p_data = supabase.table("profiles").select("tokens").eq("id", u_id).single().execute().data
                                new_balance = max(0, p_data["tokens"] + change)
                                supabase.table("profiles").update({"tokens": new_balance}).eq("id", u_id).execute()
                                
                            st.success("Scores graded and user token balances updated!")

            # Sub-Section C: Manual Token Overrides
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
