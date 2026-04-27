import streamlit as st
import pandas as pd
import random
import time

# SetUp Done
st.set_page_config(
    page_title="UCL Oracle & Chatbot",
    layout="centered"
)

# Data Done
@st.cache_data
def load_data():
        return pd.read_csv("ucl_stats.csv")
data = load_data()

# Prediction DONE
def simulate_match(t1_name, t2_name):
    t1 = data[data["Team"] == t1_name].iloc[0]
    t2 = data[data["Team"] == t2_name].iloc[0]
    # Weighted formula: attack + form bonus - opponent defense penalty + randomness
    score1 = max(0, round(
        t1["Avg_Goals"]
        + (t1["Current_Form"] * 0.1)
        - (t2["Defense_Rating"] * 0.02)
        + random.uniform(-1, 1)
    ))
    score2 = max(0, round(
        t2["Avg_Goals"]
        + (t2["Current_Form"] * 0.1)
        - (t1["Defense_Rating"] * 0.02)
        + random.uniform(-1, 1)
    ))
    return score1, score2

# Question Options DONE
SUPPORT_QUESTIONS = {
    " Pick a question": "pick",
    " How does the predictor work?": "how does it work",
    " Where does the data come from?": "data source",
    " How accurate is the model?": "accuracy",
    " Which teams are supported?": "which teams",
    " Who has won UCL titles recently?": "titles",
    " Which team has the best defense?": "best defense",
    " Which team has the best attack?": "best attack",
    " Which team is in the best form?": "best form",
}

def get_support_response(question):
    q = question.lower()
    if any(w in q for w in ["pick", "chosse", "choice"]):
        return " Pick a question from the dropdown to learn about how this app works, the data, or which teams are supported."

    elif any(w in q for w in ["data", "source", "stats", "where"]):
        return (
            " The database covers 2016–2026 UCL performance across 10 top clubs.\n\n"
            "Each club has: average goals per game, win rate, current form (1–10), "
            "defensive rating, and titles won in the last 10 years."
        )

    elif any(w in q for w in ["accura", "reliab", "trust", "real"]):
        return (
            " The model is stats-based, but shouldnt be taken as face. A randomness factor is included "
            "in every simulation to reflect the unpredictable nature of soccer. "
            "Think of results as probabilities, not guarantees anything can happen."
        )

    elif any(w in q for w in ["team", "club", "which", "list"]):
        teams_list = ", ".join(data["Team"].tolist())
        return f"️ Supported clubs: **{teams_list}**"

    elif any(w in q for w in ["title", "champion", "winner", "trophy"]):
        return (
            " Over the last 10 years:\n\n"
            "- Real Madrid — 4 titles (most dominant)\n"
            "- Man City, Bayern, Liverpool, PSG, Chelsea — 1 title each\n"
            "- Inter, Dortmund, Barcelona, Arsenal — still trying to win their next UCL Championship"
        )

    elif any(w in q for w in ["defense", "defensive", "best defend"]):
        best = data.loc[data["Defense_Rating"].idxmax()]
        return f"️ {best['Team']} has the highest defensive rating at **{int(best['Defense_Rating'])}** — Theyb have very good defense."

    elif any(w in q for w in ["attack", "goals", "offensive", "best scor"]):
        best = data.loc[data["Avg_Goals"].idxmax()]
        return f" {best['Team']} averages the most goals at **{best['Avg_Goals']} per game** — They have a very strong Offence."

    elif any(w in q for w in ["form", "current form", "best form"]):
        best = data.loc[data["Current_Form"].idxmax()]
        return f" {best['Team']} is in the best current form with a score of **{int(best['Current_Form'])}/10**."
    else:
        return "I'm not sure about that one. Pick a question from the dropdown above."

#Sidebar DONE
st.sidebar.title("Control Panel")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Choose mode",
    ["Match Predictor", "Support Chatbot"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Database Preview")
st.sidebar.dataframe(
    data[["Team", "Win_Rate", "Current_Form", "Defense_Rating"]].rename(columns={
        "Win_Rate": "Win %",
        "Current_Form": "Form",
        "Defense_Rating": "Defense"
    }),
    hide_index=True,
    use_container_width=True
)


# Match Predictor DONE
if app_mode == "Match Predictor":
    st.title("UCL Oracle")
    st.info("Pick two clubs from the dropdowns below and hit **Predict Match** to simulate a game.")

    team_list = data["Team"].tolist()

    col1, col2 = st.columns(2)
    with col1:
        t1 = st.selectbox("Home team", team_list, index=0, key="team1")
    with col2:
        default_idx = 1 if len(team_list) > 1 else 0
        t2 = st.selectbox("Away team", team_list, index=default_idx, key="team2")

    predict = st.button("Predict Match", use_container_width=True, type="primary")

    if predict:
        if t1 == t2:
            st.warning("Please pick two different teams.")
        else:
            with st.spinner(f"Simulating {t1} vs {t2}..."):
                time.sleep(1.0)
                score1, score2 = simulate_match(t1, t2)

            if score1 > score2:
                decision = f"**{t1}** is predicted to win!"
            elif score2 > score1:
                decision = f"**{t2}** is predicted to win!"
            else:
                decision = "This match is predicted to end in a **Draw**!"

            score_col1, score_col_mid, score_col2 = st.columns([2, 1, 2])
            with score_col1:
                st.metric(label=t1, value=score1)
            with score_col2:
                st.metric(label=t2, value=score2)
            st.success(decision)
            st.caption("Based on 10 years of UCL data + a match-day randomness factor.")

# Chatbot Done
else:
    st.title("Project Support")
    st.write("Pick a question from the dropdown below to learn how this app was built, where the data comes from, or which clubs are supported.")

    question_picked = st.selectbox(
        "Choose a question:",
        list(SUPPORT_QUESTIONS.keys()),
        index=0,
        key="support_question"
    )

    if st.button("Find Answer", use_container_width=True, type="primary"):
        q = SUPPORT_QUESTIONS[question_picked]
        with st.spinner("Thinking..."):
            time.sleep(0.5)
        st.markdown(f"**Q:** {question_picked}")
        st.markdown("---")
        st.markdown(get_support_response(q))
