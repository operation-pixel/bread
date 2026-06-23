import os
import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "bread_data.csv")

st.title("Bread Calendar View")

# --- Ensure bread data exists ---
if "bread_data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.bread_data = pd.read_csv(DB_FILE)
    else:
        st.error("No bread data found. Please add bread items on the Manage Bread page first.")

if "bread_data" in st.session_state:
    # --- Calendar date picker ---
    selected_date = st.date_input("Select a production date")

    # --- Supplier filter ---
    suppliers = st.session_state.bread_data["Supplier"].dropna().unique().tolist()
    supplier_filter = st.selectbox("Filter by supplier", ["All"] + suppliers)

    # --- Search bar ---
    search_term = st.text_input("Search bread name")

    # --- Filtered DataFrame ---
    df = st.session_state.bread_data.copy()

    if supplier_filter != "All":
        df = df[df["Supplier"] == supplier_filter]

    if search_term.strip():
        df = df[df["Name"].str.contains(search_term, case=False, na=False)]

    # --- Calculate expiry and best consumed ---
    df["Production Day"] = pd.to_datetime(selected_date)
    df["Expiry"] = df["Production Day"] + pd.to_timedelta(df["Expiry Days"], unit="D")

    # ⚠️ Careful: "Ordering Lead Time" is text in your DB, not numeric.
    # If you want numeric days, store them separately (e.g. "Lead Day").
    df["Ordering Lead Time"] = df["Production Day"] - pd.to_timedelta(df["Lead Day"], unit="D")

    # If you want "Best Consumed", make sure you have a numeric column for buffer days.
    # Example: df["Best Consumed"] = df["Expiry"] - pd.to_timedelta(df["ConsumeBufferDays"], unit="D")



# --- Sort alphabetically by bread name ---
    # df = df.sort_values(by="Name", ascending=True)

    # --- Display as cards instead of table ---

# --- Display as cards instead of table ---
    for _, row in df.iterrows():
        st.markdown("---")
        cols = st.columns([1, 2])
        with cols[0]:
            img_displayed = False

            # Try relative path first
            if isinstance(row.get("ImageRelative"), str) and row["ImageRelative"]:
                try:
                    st.image(row["ImageRelative"], width=150)
                    img_displayed = True
                except Exception:
                    img_displayed = False

            # Fallback to absolute path
            if not img_displayed and isinstance(row.get("ImageAbsolute"), str) and row["ImageAbsolute"]:
                try:
                    st.image(row["ImageAbsolute"], width=150)
                    img_displayed = True
                except Exception:
                    img_displayed = False

            # Final fallback: blank placeholder image
            if not img_displayed:
                st.image("static/images/blank.png", width=150)

        with cols[1]:
            st.subheader(row["Name"])
            st.write(f"**Supplier:** {row['Supplier']}")
            st.write(f"**Expiry:** {row['Expiry']}")
            st.write(f"**Production Day:** {row['Production Day']}")
            st.write(f"**Best Consumed:** {row['Best Consumed']}")

