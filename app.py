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

# Custom CSS for UI styling
st.markdown("""
    <style>
    .big-token-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .big-token-number {
        font-size: 52px;
        font-weight: 800;
        margin: 5px 0;
        color: #ffcc00;
    }
    .summary-box {
        background-color: #f8f9fa;
        border-left: 5px solid #2a5298;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .rules-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-top: 15px;
    }
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
    
    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    st.sidebar.title(f"👤 {profile['full_name']}")
    st.sidebar.metric(label="Available Tokens", value=f"{profile['tokens']} 🪙")
    
    if profile.get("is_admin"):
        st.sidebar.success("👑 Admin Mode Active")
        
    if st.sidebar.button("Log Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Dynamic Tabs Layout
    if profile.get("is_admin"):
        tab_home, tab_rules, tab_bet, tab_history, tab_leaders, tab_admin = st.tabs(
            ["🏠 Home", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard", "⚙️ Admin Control"]
        )
    else:
        tab_home, tab_rules, tab_bet, tab_history, tab_leaders = st.tabs(
            ["🏠 Home", "📖 Rules & Info", "🎯 Place Bets", "📜 My History", "🏆 Leaderboard"]
        )

    # ------------------------------------------
    # TAB 0: HOME / DASHBOARD SCREEN
    # ------------------------------------------
    with tab_home:
        st.markdown(f"## Welcome back, {profile['full_name']}! 👋")
        
        # Big Token Balance Hero Display
        st.markdown(f"""
            <div class="big-token-card">
                <div style="font-size: 18px; letter-spacing: 1px; text-transform: uppercase;">Current Balance</div>
                <div class="big-token-number">{profile['tokens']} 🪙</div>
                <div style="font-size: 14px; opacity: 0.8;">Touchdown Tokens</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📊 Last Week's Performance Summary")
        
        # Find the latest graded week
        graded_q = supabase.table("weekly_questions").select("week_number").neq("winning_answer", "Pending").neq("winning_answer", "LOCKED").order("week_number", desc=True).execute().data
        
        if not graded_q:
            st.info("No weeks have been graded yet. Place your bets for Week 1 to get started!")
        else:
            latest_graded_week = graded_q[0]["week_number"]
            
            # Fetch user bets for latest graded week
            lw_bets = supabase.table("user_bets").select("*, weekly_questions(winning_answer)").eq("user_id", user_id).eq("week_number", latest_graded_week).execute().data
            
            # Fetch TD pick for latest graded week
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
                            bet_gains += b["wager_amount"]  # Net profit doubled
                            correct_count += 1
                        else:
                            bet_losses += b["wager_amount"]
                
                # Check Touchdown bonus
                td_bonus = 5 if (lw_td and lw_td[0].get("is_correct")) else 0
                td_player = lw_td[0]["player_name"] if lw_td else "None"
                
                net_total = bet_gains - bet_losses + td_bonus
                
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

    # ------------------------------------------
    # TAB 1: RULES & INFORMATION
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

    # ------------------------------------------
    # TAB 2: BETTING FORM & QUESTION SUBMISSION
    # ------------------------------------------
    with tab_bet:
        st.header("Weekly Predictions & Wagers")
        
        weeks_res = supabase.table("weekly_questions").select("week_number").execute()
        available_weeks = sorted(list(set([r["week_number"] for r in weeks_res.data]))) if weeks_res.data else []
        
        if not available_weeks:
            st.info("No active questions available yet. Check back soon when the Admin posts Week 1!")
        else:
            selected_week = st.selectbox("Select Week:", available_weeks, index=len(available_weeks)-1)
            
            q_res = supabase.table("weekly_questions").select("*").eq("week_number", selected_week).order("question_number").execute()
            questions = q_res.data
            
            is_locked = any(q.get("winning_answer") == "LOCKED" for q in questions)
            
            if is_locked:
                st.error("🔒 Entries for this week are locked! Kickoff deadline has passed.")
            
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
                        st.divider()

                    st.markdown("### 🏈 Bonus Touchdown Scorer Pick")
                    st.caption("Name 1 player to score a TD this week (Rushing/Receiving only!). Correct pick = Bonus Tokens!")
                    
                    existing_td = supabase.table("touchdown_picks").select("player_name").eq("user_id", user_id).eq("week_number", selected_week).execute().data
                    default_td = existing_td[0]["player_name"] if existing_td else ""
                    
                    td_pick = st.text_input("Player Name (e.g., Patrick Mahomes)", value=default_td, key="td_scorer", disabled=is_locked)
                    
                    total_wagered = sum(wagers.values())
                    st.markdown(f"**Total Tokens Wagered:** `{total_wagered}` / `{profile['tokens']}`")
                    
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
    # TAB 3: USER HISTORY
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
                
                if w_ans in ["Pending", "LOCKED"]:
                    outcome = "Pending"
                elif b["pick"] == w_ans:
                    outcome = f"✅ Won (+{b['wager_amount'] * 2} Tokens)"
                else:
                    outcome = f"❌ Lost (-{b['wager_amount']} Tokens)"
                        
                formatted_data.append({
                    "Week": b["week_number"],
                    "Question": q_info.get("question_text", "N/A"),
                    "Your Pick": b["pick"],
                    "Wager": b["wager_amount"],
                    "Winner": w_ans if w_ans not in ["Pending", "LOCKED"] else "Pending",
                    "Result": outcome
                })
            st.dataframe(formatted_data, use_container_width=True)

    # ------------------------------------------
    # TAB 4: LEADERBOARD
    # ------------------------------------------
    with tab_leaders:
        st.header("🏆 Player Standings")
        leader_res = supabase.table("profiles").select("full_name, tokens").order("tokens", desc=True).execute().data
        
        if leader_res:
            st.dataframe(leader_res, use_container_width=True, hide_index=True)

    # ------------------------------------------
    # TAB 5: ADMIN PANEL (ADMINS ONLY)
    # ------------------------------------------
    if profile.get("is_admin"):
        with tab_admin:
            st.header("⚙️ Admin Management Portal")
            
            admin_sec = st.radio("Select Action", ["Create Questions", "Lock/Unlock Week", "Grade Week & Calculate Points", "Adjust User Tokens"], horizontal=True)
            
            # Sub-Section A: Enter Questions
            if admin_sec == "Create Questions":
                st.subheader("Add 10 New Weekly Questions")
                new_week = st.number_input("Week Number", min_value=1, max_value=24, step=1, key="admin_week_selector")
                
                existing_qs = supabase.table("weekly_questions").select("id").eq("week_number", new_week).execute().data
                
                if existing_qs:
                    st.warning(f"⚠️ Questions for Week {new_week} have already been published! ({len(existing_qs)} questions found)")
                    if st.button("Delete Week Questions to Start Fresh"):
                        supabase.table("weekly_questions").delete().eq("week_number", new_week).execute()
                        st.success(f"Cleared Week {new_week} questions.")
                        st.rerun()
                else:
                    with st.form(key=f"create_questions_form_week_{new_week}"):
                        q_inputs = []
                        for i in range(1, 11):
                            val = st.text_input(f"Question {i}", key=f"static_q_input_w{new_week}_q{i}")
                            q_inputs.append(val)
                        
                        submit_qs = st.form_submit_button("Publish All 10 Questions 🚀")
                    
                    if submit_qs:
                        filled_questions = [q.strip() for q in q_inputs if q.strip()]
                        if len(filled_questions) == 0:
                            st.error("Please enter at least one question before publishing.")
                        else:
                            for idx, q_text in enumerate(q_inputs):
                                if q_text.strip():
                                    supabase.table("weekly_questions").insert({
                                        "week_number": new_week,
                                        "question_number": idx + 1,
                                        "question_text": q_text.strip(),
                                        "winning_answer": "Pending"
                                    }).execute()
                            st.success(f"Successfully published questions for Week {new_week}!")
                            st.rerun()

            # Sub-Section B: Lock / Unlock Week
            elif admin_sec == "Lock/Unlock Week":
                st.subheader("🔒 Week Deadline Lock")
                lock_week = st.number_input("Select Week to Lock/Unlock", min_value=1, max_value=24, step=1, key="lock_week_num")
                
                week_qs = supabase.table("weekly_questions").select("*").eq("week_number", lock_week).execute().data
                
                if not week_qs:
                    st.warning("No questions found for this week.")
                else:
                    is_currently_locked = any(q.get("winning_answer") == "LOCKED" for q in week_qs)
                    
                    if is_currently_locked:
                        st.error(f"Week {lock_week} is currently **LOCKED** 🔒")
                        if st.button("Unlock Week for Player Submissions 🔓"):
                            for q in week_qs:
                                if q["winning_answer"] == "LOCKED":
                                    supabase.table("weekly_questions").update({"winning_answer": "Pending"}).eq("id", q["id"]).execute()
                            st.success(f"Week {lock_week} unlocked!")
                            st.rerun()
                    else:
                        st.success(f"Week {lock_week} is currently **OPEN** 🔓")
                        if st.button("Lock Week Now (Disable Submissions) 🔒"):
                            for q in week_qs:
                                if q["winning_answer"] == "Pending":
                                    supabase.table("weekly_questions").update({"winning_answer": "LOCKED"}).eq("id", q["id"]).execute()
                            st.success(f"Week {lock_week} locked!")
                            st.rerun()

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
                            default_val = q["winning_answer"] if q["winning_answer"] in ["Yes", "No"] else "Pending"
                            answers[q["id"]] = st.selectbox(
                                f"Q{q['question_number']}: {q['question_text']}", 
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
