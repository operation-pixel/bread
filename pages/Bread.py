import os
import pandas as pd
import streamlit as st
# import datetime
from datetime import datetime, timedelta, time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "bread_data.csv")
blank_path = os.path.join(APP_DIR, "static", "images", "blank.png")

st.title("Bread Calendar View")

# --- Ensure bread data exists ---
if "bread_data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.bread_data = pd.read_csv(DB_FILE)
    else:
        st.error("No bread data found. Please add bread items on the Manage Bread page first.")

if "bread_data" in st.session_state:
    # --- Calendar date picker ---
    selected_date = st.date_input("Select delivery date")

    # --- Supplier filter ---
    suppliers = st.session_state.bread_data["Supplier"].dropna().unique().tolist()
    supplier_filter = st.selectbox("Filter by supplier", ["All"] + suppliers)

    # --- Search bar ---
    search_term = st.text_input("Search bread name")

    # --- Filtered DataFrame ---
    df = st.session_state.bread_data.copy()


    # # --- Apply search filter ---
    # if search_term:
    #     df = df[df["Name"].str.contains(search_term, case=False, na=False)]
    

    # Replace NaN suppliers with "-"
    df["Supplier"] = df["Supplier"].fillna("-")                                       
    

    # Build supplier list from the cleaned df
    suppliers = df["Supplier"].unique().tolist()

        # Apply supplier filter
    if supplier_filter != "All":
        df = df[df["Supplier"] == supplier_filter]
    
    if search_term:
        df = df[df["Name"].str.contains(search_term, case=False, na=False)]
    
    # Apply delivery date filter
    # Assuming you have a column "Delivery Date" in your CSV
    if "Delivery Date" in df.columns:
        df["Delivery Date"] = pd.to_datetime(df["Delivery Date"])
        df = df[df["Delivery Date"].dt.date == selected_date]

    # supplier_filter = st.selectbox("Filter by supplier", ["All"] + suppliers)

    # --- Handle empty results ---
    if df.empty:
        st.warning("No results found for your filters.")
    else:
    

        def get_production_day(delivery_date, production_days_str):
            if not isinstance(production_days_str, str) or not production_days_str.strip():
                return delivery_date  # fallback if missing data

            production_days = [d.strip() for d in production_days_str.split(",")]
            day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
            prod_days_num = [day_map[d] for d in production_days if d in day_map]

            if not prod_days_num:
                return delivery_date  # fallback if no valid days

            for offset in range(7):
                candidate = delivery_date - timedelta(days=offset)
                if candidate.weekday() in prod_days_num:
                    return candidate

            return delivery_date  # fallback        
            # delivery_num = delivery_date.weekday()
            # possible_days = [d for d in prod_days_num if d <= delivery_num]
            # if possible_days:
            #     chosen_day = max(possible_days)
            #     days_diff = delivery_num - chosen_day
            #     return delivery_date - datetime.timedelta(days=days_diff)
            # else:
            #     # wrap to previous week
            #     chosen_day = max(prod_days_num)
            #     days_diff = (7 - delivery_num) + chosen_day
            #     return delivery_date - datetime.timedelta(days=days_diff)
        def get_order_by(production_date, lead_days, lead_time_str):
        # Subtract lead days
            order_date = production_date - timedelta(days=int(lead_days))

        # If cutoff time exists, attach it
            if pd.notna(lead_time_str):
                cutoff_time = datetime.strptime(str(lead_time_str), "%H:%M:%S").time()
                order_dt = datetime.combine(order_date, cutoff_time)
                return order_dt.strftime("%d %b %Y (%A) %I:%M %p")
            else:
                return order_date.strftime("%d %b %Y (%A)")
        
        # --- Calculate production & expiry ---
        df["General Production Days"] = df["Production Day"]
        df["Production Day"] = df.apply(
            lambda row: get_production_day(selected_date, row.get("Production Day", "")),
            axis=1
        )

        df["Expiry"] = df.apply(
            lambda row: (row["Production Day"] + pd.to_timedelta(row["Expiry Days"], unit="D")).strftime("%d %b %Y (%A)"),
            axis=1
        )

        df["Production Day"] = pd.to_datetime(df["Production Day"])
        df["Production Day Display"] = df["Production Day"].dt.strftime("%d %b %Y (%A)")

        df["Order By"] = df.apply(
        lambda row: get_order_by(row["Production Day"], row["Lead Day"], row["Lead Time"]),
        axis=1
    )

    for _, row in df.iterrows():
        st.markdown("---")
        cols = st.columns([1, 2])
        with cols[0]:
            st.write("🍞")  # placeholder for image
        with cols[1]:
            st.subheader(row["Name"])
            st.write(f"**Supplier:** {row['Supplier']}")
            st.write(f"**Production Date:** {row['Production Day Display']}")
            st.write(f"**Expiry:** {row['Expiry']}")
            st.write(f"**General Production Days:** {row.get('General Production Days', '-')}")

                # --- Highlight Order By if overdue ---
            order_by_str = row["Order By"]

            # Try to parse back into datetime (strip time if needed)
            try:
                # Handle both with and without time
                if ":" in order_by_str:
                    order_dt = datetime.strptime(order_by_str, "%d %b %Y (%A) %I:%M %p")
                else:
                    order_dt = datetime.strptime(order_by_str, "%d %b %Y (%A)")
            except Exception:
                order_dt = None

            if order_dt and order_dt.date() <= datetime.now().date():
                st.markdown(f"<span style='color:red'>**Order By:** {order_by_str}</span>", unsafe_allow_html=True)
            else:
                st.write(f"**Order By:** {order_by_str}")