import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="📋 FO Leaderboard Snapshot", layout="centered")
st.title("📋 FO Leaderboard Generator")

st.markdown("Upload a CSV file containing the leaderboard data. The app will generate a ranked leaderboard and display it below.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def generate_html(top_df, today):
    def style_rank(rank):
        if rank == 1:
            return "<b style='color:gold'>🥇 1</b>"
        elif rank == 2:
            return "<b style='color:silver'>🥈 2</b>"
        elif rank == 3:
            return "<b style='color:#cd7f32'>🥉 3</b>"
        else:
            return str(rank)

    row_html = "\n".join(
        f"<tr><td>{style_rank(r['Rank'])}</td><td>{r['FO Name']}</td><td>{r['Total Collection Updates']}</td><td>{r['Loans Collected']}</td></tr>"
        for _, r in top_df.iterrows()
    )

    with open("leaderboard_template.html", "r") as f:
        html_template = f.read()

    return html_template.replace("{{rows}}", row_html).replace("{{date}}", today)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Keep relevant columns and rename for consistency with HTML template
    df = df[["FO Name", "Total Collection Updates", "Collected"]]
    df.rename(columns={"Collected": "Loans Collected"}, inplace=True)

    # Rank and sort
    df = df.sort_values(by="Total Collection Updates", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))

    # Top 5 for display
    top_df = df.head(5)

    today = datetime.today().strftime("%d %b %Y")
    html = generate_html(top_df, today)

    # Show HTML directly in Streamlit
    components.html(html, height=600, scrolling=True)

