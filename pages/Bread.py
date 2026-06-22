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

    # --- Supplier filter ---
    suppliers = st.session_state.bread_data["Supplier"].dropna().unique().tolist()
    supplier_filter = st.selectbox("Filter by supplier", ["All"] + suppliers)

    # --- Search bar ---
    search_term = st.text_input("Search bread name")

    # --- Filtered DataFrame ---
    df = st.session_state.bread_data.copy()

    # Apply supplier filter
    if supplier_filter != "All":
        df = df[df["Supplier"] == supplier_filter]

    # Apply search filter
    if search_term.strip():
        df = df[df["Name"].str.contains(search_term, case=False, na=False)]

    # --- Calculate expiry and best consumed ---
    df["Expiry"] = (pd.to_datetime(selected_date) + timedelta(days=5)).date()
    df["Best Consumed"] = (pd.to_datetime(selected_date) + timedelta(days=2)).date()


# --- Sort alphabetically by bread name ---
    # df = df.sort_values(by="Name", ascending=True)

    # --- Display as cards instead of table ---
    for _, row in df.iterrows():
        st.markdown("---")
        cols = st.columns([1, 2])
        with cols[0]:
            if isinstance(row["ImageRelative"], str) and row["ImageRelative"]:
                st.image(row["ImageRelative"], width=150)
            else:
                st.write("No image available")
        with cols[1]:
            st.subheader(row["Name"])
            st.write(f"**Supplier:** {row['Supplier']}")
            st.write(f"**Expiry:** {row['Expiry']}")
            st.write(f"**Production Day:** {row['Production Day']}")
            st.write(f"**Best Consumed:** {row['Best Consumed']}")
