# app.py

import json
import streamlit as st
from classify import classify_ticket
from rag import answer_query
from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------------
# Load sample tickets for Bulk Dashboard
# -------------------------------
def load_sample_tickets():
    try:
        file_path = os.path.join("data", "sample_tickets.jsonl")
        tickets = []
        with open(file_path, "r") as f:
            for line in f:
                tickets.append(json.loads(line))
        return tickets
    except FileNotFoundError:
        st.warning(f"⚠️ {file_path} not found.")
        return []

# -------------------------------
# App UI
# -------------------------------
st.set_page_config(page_title="Customer Support Copilot", layout="wide")
st.title("🤖 Customer Support Copilot — Intern Prototype")

# Tabs for Bulk Dashboard & Interactive Agent
tab1, tab2 = st.tabs(["📊 Bulk Ticket Dashboard", "💬 Interactive Agent"])

# -------------------------------
# Bulk Ticket Dashboard
# -------------------------------
with tab1:
    st.header("📊 Bulk Ticket Classification Dashboard")
    tickets = load_sample_tickets()
    
    if tickets:
        rows = []
        for t in tickets:
            text = t.get("body", t.get("text",""))
            short = text if len(text) < 100 else text[:97] + "..."
            cl = classify_ticket(text)
            rows.append({
                "ID": t.get("id", ""),
                "Subject": t.get("subject", ""),
                "Text": short,
                "Topic": cl.get("topic"),
                "Sentiment": cl.get("sentiment"),
                "Priority": cl.get("priority"),
                "Confidence": cl.get("confidence", "")
            })

        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No sample tickets found.")

# -------------------------------
# Interactive Agent
# -------------------------------
with tab2:
    st.header("💬 Interactive Ticket / Question")
    col1, col2 = st.columns([2,1])

    with col1:
        user_text = st.text_area("Paste a ticket or question here:", height=220)
        if st.button("Analyze & Respond"):
            if not user_text.strip():
                st.warning("Write a ticket first.")
            else:
                analysis = classify_ticket(user_text)
                st.session_state["analysis"] = analysis
                st.session_state["last_text"] = user_text
                st.success("✅ Analysis Complete")

    with col2:
        st.subheader("🧾 Internal Analysis View")
        if st.session_state.get("analysis"):
            st.json(st.session_state["analysis"])
        else:
            st.info("Analyze a ticket to see the JSON classification.")

    st.markdown("---")
    st.subheader("🎯 Final Response View")
    if st.session_state.get("analysis"):
        topic = st.session_state["analysis"].get("topic")
        q = st.session_state.get("last_text","")

        if topic in ["How-to", "Product", "Best practices", "API/SDK", "SSO"]:
            result = answer_query(q)
            st.markdown("**Answer:**")
            st.write(result.get("answer",""))
            st.markdown("**Sources:**")
            for src in result.get("sources", []):
                st.write(f"- {src}")
        else:
            st.info(f"This ticket has been classified as a **{topic}** issue and routed to the appropriate team.")

