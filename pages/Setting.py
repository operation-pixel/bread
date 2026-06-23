import streamlit as st
import pandas as pd
import re
import os
import io
from datetime import datetime, time, timedelta
from PIL import Image

# Define a password (better: use st.secrets)
SETTINGS_PASSWORD = "bread123"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.is_admin:
    st.title("Manage Bread")
    pwd = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        if pwd == SETTINGS_PASSWORD:
            st.session_state.is_admin = True
            st.success("Login successful! You can now manage bread.")
        else:
            st.error("Incorrect password")
else:

    # --- ALL your existing bread management code goes here ---
    # (everything you pasted: add/update/delete/import/export forms)

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
                "ImageRelative": [],
                "ImageAbsolute": [],
                "Name": [],
                "Supplier": [],
                "Production Day": [],
                "Expiry Days": [],
                "Expiry": [],
                "Ordering Lead Time": [],
                "Lead Day": [],
                "Lead Time": [],
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

    # Build a list of columns excluding ImageAbsolute
    cols = [c for c in st.session_state.bread_data.columns if c not in ["ImageAbsolute","Expiry Days","Lead Day","Lead Time"]]

    # Move ImageRelative to the end
    cols = [c for c in cols if c != "ImageRelative"] + ["ImageRelative"]

    # Render only the selected columns
    st.dataframe(
        st.session_state.bread_data[cols],
        column_config={
            "ImageRelative": st.column_config.TextColumn("Relative Path")
        },
        hide_index=True
    )

    # --- Helper to reset flags ---
    def reset_forms():
        st.session_state.show_add_form = False
        st.session_state.show_search_form = False
        st.session_state.show_delete_form = False
        st.session_state.show_export = False
        st.session_state.show_import = False

    # --- Buttons layout with persistent state ---
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    with col1:
        if st.button("➕ Add Bread"):
            reset_forms()
            st.session_state.show_add_form = True
    with col2:
        if st.button("🔍 Update Bread Details"):
            reset_forms()
            st.session_state.show_search_form = True
    with col3:
        if st.button("🗑️ Delete Bread"):
            reset_forms()
            st.session_state.show_delete_form = True
    with col4:
        if st.button("⬇️ Export (CSV/Excel)"):
            reset_forms()
            st.session_state.show_export = True
    with col5:
        if st.button("⬆️ Import (CSV/Excel)"):
            reset_forms()
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
            f"{lead_days} days, {lead_cutoff.strftime('%H:%M:%S')} cut-off"
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
                relative_path = None

                if image is not None and name:
                    safe_name = re.sub(r'[\\/*?:"<>|]', "_", name) 
                    base_filename = safe_name.replace(" ", "_").lower()
                    file_ext = os.path.splitext(image.name)[1]
                    final_filename = f"{base_filename}{file_ext}"
                    final_path = os.path.join(image_dir, final_filename)

                    os.makedirs(image_dir, exist_ok=True)
                    counter = 1
                    while os.path.exists(final_path):
                        final_filename = f"{base_filename}_{counter}{file_ext}"
                        final_path = os.path.join(image_dir, final_filename)
                        counter += 1

                    with open(final_path, "wb") as f:
                        f.write(image.getbuffer())

                    # image_path = os.path.relpath(final_path, APP_DIR)
                    image_path = final_path
                    relative_path = os.path.relpath(final_path, APP_DIR).replace("\\", "/")

                    
                new_row = {
                    "ImageRelative": relative_path if relative_path else "🍞",
                    "ImageAbsolute": image_path if image_path else None,
                    "Name": name,
                    "Supplier": supplier,
                    "Production Day": ", ".join([d.strip() for d in production_day]),
                    "Expiry Days": expiry_days,
                    "Expiry": expiry_text,
                    "Lead Day": lead_days,
                    "Lead Time": lead_cutoff.strftime('%H:%M:%S') if lead_cutoff else pd.NA,
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

    # --- Import form ---
    if st.session_state.get("show_import", False):
        st.subheader("Import Bread Database")

        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                # Read based on file type
                if uploaded_file.name.endswith(".csv"):
                    imported_df = pd.read_csv(uploaded_file)
                else:
                    imported_df = pd.read_excel(uploaded_file)

                # Only these two are compulsory
                required_cols = ["Name", "Expiry"]

                # Check for missing compulsory columns
                missing = [c for c in required_cols if c not in imported_df.columns]
                if missing:
                    st.error(f"Missing compulsory columns: {', '.join(missing)}")
                else:
                    # Ensure all other expected columns exist (fill with None if missing)
                    expected_cols = [
                        "ImageRelative", "ImageAbsolute", "Supplier",
                        "Production Day", "Expiry Days", "Expiry", "Lead Day", "Lead Time", "Ordering Lead Time", "Remark/Update (If Any)"
                    ]
                    for col in expected_cols:
                        if col not in imported_df.columns:
                            imported_df[col] = None

                    # Remove rows from imported_df where Name already exists in bread_data
                    existing_names = set(st.session_state.bread_data["Name"].tolist())
                    imported_df = imported_df[~imported_df["Name"].isin(existing_names)]

                    # Merge with existing data
                    st.session_state.bread_data = pd.concat(
                        [st.session_state.bread_data, imported_df],
                        ignore_index=True
                    )

                    # Save back to disk
                    
                    st.session_state.bread_data.to_csv(DB_FILE, index=False)
                    st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)

                    st.success("Import successful! Data merged into bread database.")
                    st.session_state.show_import = False

            except Exception as e:
                st.error(f"Error importing file: {e}")

    # --- Update/Search Bread form ---
    if st.session_state.get("show_search_form", False):
        # --- Update/Search Bread form ---



        st.subheader("Update Bread Details")

        # Dropdown to select bread
        bread_to_edit = st.selectbox("Select bread to edit", st.session_state.bread_data["Name"].tolist())
        if bread_to_edit:
            idx = st.session_state.bread_data[st.session_state.bread_data["Name"] == bread_to_edit].index[0]

            # --- Bread name ---
            raw_name = st.session_state.bread_data.at[idx, "Name"]
            name_default = "" if pd.isna(raw_name) else str(raw_name)
            new_name = st.text_input("Bread Name", value=name_default)

            # --- Current image preview + delete option ---
            current_image_path = st.session_state.bread_data.at[idx, "ImageAbsolute"]
            if isinstance(current_image_path, str) and current_image_path and os.path.exists(current_image_path):
                st.image(current_image_path, caption=f"Current image for {bread_to_edit}", width=200)
                if st.button("🗑️ Delete Current Image", key=f"delete_image_{idx}"):
                    st.session_state.bread_data.at[idx, "ImageRelative"] = None
                    st.session_state.bread_data.at[idx, "ImageAbsolute"] = None
                    st.session_state.bread_data.to_csv(DB_FILE, index=False)
                    st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)
                    st.success(f"Image deleted for {bread_to_edit}")

            # --- Upload new image (preview only, commit on save) ---
            new_image = st.file_uploader("Upload new image", type=["png","jpg","jpeg"], key=f"upload_image_{idx}")
            if new_image:
                st.image(new_image, caption="New image preview", width=200)

            # --- Supplier ---
            raw_supplier = st.session_state.bread_data.at[idx, "Supplier"]
            supplier_default = "" if pd.isna(raw_supplier) else str(raw_supplier)
            new_supplier = st.text_input("Supplier", value=supplier_default)

            # --- Production Days ---
            raw_days = st.session_state.bread_data.at[idx, "Production Day"]
            default_days = [] if pd.isna(raw_days) or not str(raw_days).strip() else [
                d.strip() for d in str(raw_days).split(",") if d.strip() in
                ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            ]
            new_days = st.multiselect("Production Days",
                                    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                                    default=default_days)

            # --- Expiry ---
            # new_expiry = st.text_input("Best Consumed", value=st.session_state.bread_data.at[idx, "Expiry"])
            # --- Expiry ---
            raw_expiry_days = st.session_state.bread_data.at[idx, "Expiry Days"]
            index_val = int(raw_expiry_days) if pd.notna(raw_expiry_days) else 0  # default to 4

            new_expiry_days = st.selectbox(
                "Best Consumed (Production Day + x days)",
                options=list(range(0, 15)),
                index=index_val
            )

            # Build the friendly text for display
            new_expiry = f"Production Day + {new_expiry_days} days"

            
            # --- Lead time with optional cutoff ---
            raw_lead_days = st.session_state.bread_data.at[idx, "Lead Day"]
            raw_cutoff = st.session_state.bread_data.at[idx, "Lead Time"]

            index_val = int(raw_lead_days) if pd.notna(raw_lead_days) else 0
            new_lead_days = st.selectbox("Lead Days (optional)", options=list(range(0, 15)), index=index_val)

            use_cutoff = st.checkbox("Specify cutoff time?", value=pd.notna(raw_cutoff))
            if use_cutoff:
                cutoff_val = datetime.strptime(raw_cutoff, "%H:%M:%S").time() if pd.notna(raw_cutoff) else time(0,0)
                new_cutoff = st.time_input("Cutoff Time", value=cutoff_val)
            else:
                new_cutoff = None

            # --- Remarks ---
            raw_remark = st.session_state.bread_data.at[idx, "Remark/Update (If Any)"]
            remark_default = "" if pd.isna(raw_remark) else str(raw_remark)
            new_remark = st.text_area("Remarks", value=remark_default)

            # --- Save Updates ---
            if st.button("💾 Save Updates", key=f"save_updates_{idx}"):
                if not new_name.strip():
                    st.error("Bread name cannot be empty.")
                elif new_name in st.session_state.bread_data["Name"].tolist() and new_name != raw_name:
                    st.error("Duplicate bread name detected. Please choose a unique name.")
                else:
                    # Update DataFrame fields
                    st.session_state.bread_data.at[idx, "Name"] = new_name
                    st.session_state.bread_data.at[idx, "Supplier"] = pd.NA if not new_supplier.strip() else new_supplier
                    st.session_state.bread_data.at[idx, "Production Day"] = ",".join(new_days)
                    st.session_state.bread_data.at[idx, "Expiry Days"] = new_expiry_days
                    st.session_state.bread_data.at[idx, "Expiry"] = new_expiry
                    lead_time_text = f"{new_lead_days} days" + (
        f", {new_cutoff.strftime('%H:%M:%S')} cut-off" if new_cutoff else ""
    )
                    # st.session_state.bread_data.at[idx, "Ordering Lead Time"] = lead_time_text
                    # # Optional: track cutoff separately so you can distinguish "no cutoff" with NA
                    # st.session_state.bread_data.at[idx, "Ordering Cutoff"] = (
                    # new_cutoff.strftime("%H:%M:%S") if new_cutoff else pd.NA)
                    # st.session_state.bread_data.at[idx, "LeadTimeDays"] = new_lead_days

                    st.session_state.bread_data.at[idx, "Lead Day"] = new_lead_days
                    st.session_state.bread_data.at[idx, "Lead Time"] = new_cutoff.strftime("%H:%M:%S") if new_cutoff else pd.NA
                    st.session_state.bread_data.at[idx, "Ordering Lead Time"] = f"{new_lead_days} days" + (f", {new_cutoff.strftime('%H:%M:%S')} cut-off" if new_cutoff else "")
                    st.session_state.bread_data.at[idx, "Remark/Update (If Any)"] = pd.NA if not new_remark.strip() else new_remark

                    # Handle new image replacement here
                    if new_image is not None:
                        saved_name = st.session_state.bread_data.at[idx, "Name"]
                        base_filename = saved_name.replace(" ", "_").lower()
                        file_ext = os.path.splitext(new_image.name)[1]
                        final_filename = f"{base_filename}_replaced{file_ext}"
                        final_path = os.path.join(image_dir, final_filename)
                        with open(final_path, "wb") as f:
                            f.write(new_image.getbuffer())
                        relative_path = os.path.relpath(final_path, APP_DIR).replace("\\", "/")
                        st.session_state.bread_data.at[idx, "ImageRelative"] = relative_path
                        st.session_state.bread_data.at[idx, "ImageAbsolute"] = final_path

                    # Persist changes
                    st.session_state.bread_data.to_csv(DB_FILE, index=False)
                    st.session_state.bread_data.to_excel(EXCEL_FILE, index=False)

                    st.success(f"Details updated for {new_name}")
