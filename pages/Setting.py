import streamlit as st
import pandas as pd
import re
import os
import io
from datetime import datetime, timedelta

# Path to save file in the same directory as app.py
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "bread_data.csv")
EXCEL_FILE = os.path.join(APP_DIR, "bread_data.xlsx")
image_dir = os.path.join(APP_DIR, "static", "images")
os.makedirs(image_dir, exist_ok=True)

st.title("Manage Bread")

# --- Initialize session state ---
if "bread_data" not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.bread_data = pd.read_csv(DB_FILE)
    else:
        # Start with an empty DataFrame (no sample rows)
        st.session_state.bread_data = pd.DataFrame({
            "Image": [],
            "Name": [],
            "Supplier": [],
            "Production Day": [],
            "Expiry": [],
            "Ordering Lead Time": [],
            "Remark/Update (If Any)": [],
        })
        # Save both CSV and Excel locally
        st.session_state.bread_data.to_csv(DB_FILE, index=False)
        st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)  # save initial file


# --- Hidden numeric storage ---
if "expiry_days_list" not in st.session_state:
    st.session_state.expiry_days_list = []   # numeric expiry values
if "lead_time_days_list" not in st.session_state:
    st.session_state.lead_time_days_list = []  # numeric lead time values

# --- Display table ---
rows = len(st.session_state.bread_data)
st.dataframe(
    st.session_state.bread_data,
    column_config={
        "Image": st.column_config.ImageColumn("Bread Image", width="small")
    },
    # height=rows*35+100
)

# --- Buttons layout with persistent state ---
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    if st.button("➕ Add Bread"):
        st.session_state.show_add_form = True
with col2:
    if st.button("🔍 Search Bread"):
        st.session_state.show_search_form = True
with col3:
    if st.button("🗑️ Delete Bread"):
        st.session_state.show_delete_form = True
with col4:
    if st.button("⬇️ Export (CSV/Excel)"):
        st.session_state.show_export = True
with col5:
    if st.button("⬆️ Import (CSV/Excel)"):
        st.session_state.show_import = True

# --- Add bread form ---
if st.session_state.get("show_add_form", False):
    st.subheader("Add New Bread Entry")
    image = st.file_uploader("Upload bread image (optional)", type=["png","jpg","jpeg"])
    if image:
        st.image(image, caption="Preview")
    name = st.text_input("Bread name *")
    supplier = st.text_input("Supplier (optional)")
    production_day = st.multiselect("Production days (optional)",
                                    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    expiry_days = st.selectbox("Best Consumed (e.g. 'Production Day + 5 days')*", options=list(range(0,15)), index=0)
    expiry_text = f"Production Day + {expiry_days} days"
    # Lead time field: dropdown + optional text input
    col1, _ = st.columns([1,1])

    with col1:
        use_cutoff = st.checkbox("Specify cut-off lead time?")
        lead_days = st.selectbox("Ordering Lead Days (optional)", options=list(range(0, 15)), index=0)
        lead_cutoff = None
        if use_cutoff:
            # 👇 Appears right below the Days dropdown
            lead_cutoff = st.time_input("Cut-off lead-time (optional)")

    # Build the friendly text
    lead_time_text = (
        f"{lead_days} days, {lead_cutoff.strftime('%I:%M %p')} cut-off"
        if lead_cutoff
        else f"{lead_days} days"
    )

    update = st.text_area("Remark/Update (if any, optional)")

        # 👇 Add image saving logic here
    if st.button("Save Entry", key="save_entry_button"):
        if not name or not expiry_text:
            st.error("Bread name and expiry are required.")
        else:
            # Save image only when entry is confirmed
            image_path = None
            if image is not None and name:
                base_filename = name.replace(" ", "_").lower()
                file_ext = os.path.splitext(image.name)[1]
                final_filename = f"{base_filename}{file_ext}"
                final_path = os.path.join(image_dir, final_filename)

                counter = 1
                while os.path.exists(final_path):
                    final_filename = f"{base_filename}_{counter}{file_ext}"
                    final_path = os.path.join(image_dir, final_filename)
                    counter += 1

                with open(final_path, "wb") as f:
                    f.write(image.getbuffer())

                # image_path = os.path.relpath(final_path, APP_DIR)
                image_path = f"/static/images/{final_filename}"

                
            new_row = {
                "Image": image_path if image_path else "🍞",
                "Name": name,
                "Supplier": supplier,
                "Production Day": ", ".join(production_day),
                "Expiry": expiry_text,
                "Ordering Lead Time": lead_time_text,
                "Remark/Update (If Any)": update, # keep consistent with your DataFrame
            }

            st.session_state.bread_data = pd.concat(
                [st.session_state.bread_data, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.session_state.bread_data.to_csv(DB_FILE, index=False)
            st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)

            st.session_state.expiry_days_list.append(expiry_days)
            st.session_state.lead_time_days_list.append(lead_days)

            st.success(f"Added {name} with expiry '{expiry_text}' (numeric {expiry_days})")
            st.session_state.show_add_form = False
        




# --- Delete bread form ---
if st.session_state.get("show_delete_form", False):
    st.subheader("Delete Bread")

    # Show checkboxes for each bread
    delete_selection = st.multiselect(
        "Select bread(s) to delete",
        options=st.session_state.bread_data["Name"].tolist()
    )

    if delete_selection:
        st.warning(f"Are you sure you want to delete: {', '.join(delete_selection)}?")
        if st.button("Confirm Delete"):
            mask = ~st.session_state.bread_data["Name"].isin(delete_selection)
            st.session_state.bread_data = st.session_state.bread_data[mask].reset_index(drop=True)
            st.success(f"Deleted: {', '.join(delete_selection)}")
            st.session_state.show_delete_form = False

st.session_state.bread_data.to_csv(DB_FILE, index=False)
st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)


# --- Export form ---
if st.session_state.get("show_export", False):
    st.subheader("Export Bread Database")

    # Save both CSV and Excel locally in the app.py folder
    APP_DIR = os.path.dirname(__file__)
    CSV_FILE = os.path.join(APP_DIR, "bread_data.csv")
    EXCEL_FILE = os.path.join(APP_DIR, "bread_data.xlsx")

    st.session_state.bread_data.to_csv(CSV_FILE, index=False)
    st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)

    # Offer download buttons
    csv_buffer = io.StringIO()
    st.session_state.bread_data.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download Bread Database (CSV)",
        data=csv_buffer.getvalue(),
        file_name="bread_data.csv",
        mime="text/csv"
    )

    excel_buffer = io.BytesIO()
    st.session_state.bread_data.to_excel(excel_buffer, index=False)
    st.download_button(
        label="Download Bread Database (Excel)",
        data=excel_buffer.getvalue(),
        file_name="bread_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Hide export after showing
    st.session_state.show_export = False
