import streamlit as st
import pandas as pd
from datetime import datetime
import os
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="📋 FO Leaderboard Snapshot", layout="centered")
st.title("📋 FO Leaderboard Generator")

st.markdown("Upload a CSV file containing the leaderboard data. The app will generate a ranked leaderboard and provide a snapshot to download.")

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

def render_and_capture(html):
    with open("rendered.html", "w") as f:
        f.write(html)

    output_path = "output.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + os.path.abspath("rendered.html"))
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    if not os.path.exists(output_path):
        raise FileNotFoundError("Screenshot failed. 'output.png' not found.")

    return output_path

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Keep relevant columns and rename for consistency with HTML template
    df = df[["FO Name", "Total Collection Updates", "Collected"]]
    df.rename(columns={"Collected": "Loans Collected"}, inplace=True)

    # Rank and sort
    df = df.sort_values(by="Total Collection Updates", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df)+1))

    # Top 5 for display
    top_df = df.head(5)

    today = datetime.today().strftime("%d %b %Y")
    html = generate_html(top_df, today)
    output_path = render_and_capture(html)

    with open(output_path, "rb") as img_file:
        st.image(img_file.read(), caption="Leaderboard Snapshot")

    st.download_button(
        label="📥 Download Leaderboard Snapshot",
        data=open(output_path, "rb"),
        file_name="fo_leaderboard.png",
        mime="image/png"
    )
