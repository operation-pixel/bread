import streamlit as st
import pandas as pd
from datetime import timedelta

st.title("Bread Calendar View")

# --- Ensure bread data exists ---
if "bread_data" not in st.session_state:
    st.error("No bread data found. Please add bread items on the Manage Bread page first.")
else:
    # --- Calendar date picker ---
    selected_date = st.date_input("Select a production date")

    # --- Extract relevant columns ---
    df = st.session_state.bread_data[["Image", "Name", "Supplier"]].copy()

    # --- Calculate expiry and best consumed ---
    # Example rules: expiry = +5 days, best consumed = +2 days
    df["Expiry"] = (pd.to_datetime(selected_date) + timedelta(days=5)).date()
    df["Date can be ordered"] = (pd.to_datetime(selected_date) + timedelta(days=2)).date()

    # --- Display table ---
    st.dataframe(df)
