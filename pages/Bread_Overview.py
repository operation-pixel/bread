import streamlit as st
import pandas as pd

st.title("Manage Bread")

# --- Table at the top ---
sample_data = pd.DataFrame({
    "Image": ["🍞", "🥖"],
    "Name": ["Sourdough", "Baguette"],
    "Supplier": ["Local Mill", "French Bakery"],
    "Production Date": ["2026-06-15", "2026-06-16"],
    "Expiry": ["2026-06-18", "2026-06-17"],
    "Remark": ["Popular", "Crispy crust"]
})
st.dataframe(sample_data)

# --- Buttons layout ---
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    add_btn = st.button("➕ Add Bread")
with col2:
    search_btn = st.button("🔍 Search Bread")
with col3:
    delete_btn = st.button("🗑️ Delete Bread")
with col4:
    export_btn = st.button("⬇️ Export (CSV/Excel)")
with col5:
    import_btn = st.button("⬆️ Import (CSV/Excel)")

# --- Add bread form ---
if add_btn:
    st.subheader("Add New Bread Entry")
    image = st.file_uploader("Upload bread image (optional)", type=["png","jpg","jpeg"])
    name = st.text_input("Bread name *")
    supplier = st.text_input("Supplier (optional)")
    production_date = st.date_input("Production date (optional)")
    expiry = st.date_input("Expiry date *")
    remark = st.text_area("Remark (optional)")
    if st.button("Save Entry"):
        if not name or not expiry:
            st.error("Bread name and expiry are required.")
        else:
            st.success(f"Added {name} with expiry {expiry}")

# --- Search bread ---
if search_btn:
    st.subheader("Search Bread")
    query = st.text_input("Enter bread name to search")
    if query:
        results = sample_data[sample_data["Name"].str.contains(query, case=False)]
        st.write("Search results:")
        st.dataframe(results)

# --- Delete bread ---
if delete_btn:
    st.subheader("Delete Bread")
    delete_name = st.text_input("Enter bread name to delete")
    if st.button("Confirm Delete"):
        st.warning(f"{delete_name} deleted (demo only).")

# --- Export / Import ---
if export_btn:
    st.download_button("Download bread data (CSV)", 
                       data=sample_data.to_csv(index=False), 
                       file_name="bread_data.csv")

if import_btn:
    uploaded_file = st.file_uploader("Upload bread data (CSV/Excel)", type=["csv","xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write("Imported data:")
        st.dataframe(df)
