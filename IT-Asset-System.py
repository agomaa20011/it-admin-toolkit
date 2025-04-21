import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────────────── PAGE SETUP ─────────────────────────────
st.set_page_config(page_title="IT Admin Toolkit", page_icon="🛠️", layout="wide")

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["IT Asset Tracker", "Onboarding Checklist", "Password Reset Guide"])

# ────────────────────── PAGE 1: IT ASSET TRACKER ───────────────
if page == "IT Asset Tracker":
    st.title("🖥️ IT Asset Tracker")
    st.markdown("Track, register, and visualize your IT assets like a pro.")

    # Load data
    csv_file = 'IT-Asset Tracker.csv'
    try:
        raw = pd.read_csv(csv_file)
    except FileNotFoundError:
        raw = pd.DataFrame()

    # Clean columns
    raw = raw.rename(columns={"Device type": "Device Type", "Date issued": "Date Issued"})
    raw = raw.loc[:, ~raw.columns.duplicated()]

    expected_cols = [
        "Asset ID", "Device Type", "Brand & Model", "Serial Number", "Assigned To",
        "Department", "Date Issued", "Condition", "Accessories Included", "Return Date", "Notes"
    ]
    for col in expected_cols:
        if col not in raw.columns:
            raw[col] = None
    df = raw[expected_cols].copy()

    # Filters
    st.sidebar.subheader("Filters")
    dept_filter = st.sidebar.selectbox("Department", ["All"] + sorted(df["Department"].dropna().unique()))
    cond_filter = st.sidebar.selectbox("Condition", ["All"] + sorted(df["Condition"].dropna().unique()))

    df_filtered = df.copy()
    if dept_filter != "All":
        df_filtered = df_filtered[df_filtered["Department"] == dept_filter]
    if cond_filter != "All":
        df_filtered = df_filtered[df_filtered["Condition"] == cond_filter]

    # Display table
    st.subheader("📋 Current Asset Inventory")
    st.dataframe(df_filtered, use_container_width=True)

    # Charts
    # definding colors 
    condition_colors = {
        "New": "#2ecc71",      # Green
        "Good": "#3498db",     # Blue
        "Used": "#e67e22",     # Orange
        "Damaged": "#e74c3c"   # Red
    }

    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Assets by Department")
        if not df.empty:
            dept_data = df_filtered["Department"].value_counts().reset_index()
            dept_data.columns = ["Department", "Count"]
            fig1 = px.bar(dept_data, x="Department", y="Count", color="Department", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📈 Condition Distribution")
        if not df.empty:
            fig2 = px.pie(df_filtered, names="Condition", hole=0.4, title="Asset Condition Overview", color="Condition",
                          color_discrete_map=condition_colors)
            st.plotly_chart(fig2, use_container_width=True)

    # Asset Entry Form
    st.subheader("➕ Register a New Asset")
    with st.form("add_asset"):
        asset_id = st.text_input("Asset ID")
        device_type = st.selectbox("Device Type", ["Laptop", "Monitor", "Mouse", "Keyboard", "Headset"])
        brand_model = st.text_input("Brand & Model")
        serial = st.text_input("Serial Number")
        assigned = st.text_input("Assigned To")
        dept = st.text_input("Department")
        date_in = st.date_input("Date Issued")
        condition = st.selectbox("Condition", ["New", "Good", "Used", "Damaged"])
        accessories = st.text_input("Accessories Included")
        return_dt = st.date_input("Return Date")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Asset")

        if submitted:
            new = {
                "Asset ID": asset_id,
                "Device Type": device_type,
                "Brand & Model": brand_model,
                "Serial Number": serial,
                "Assigned To": assigned,
                "Department": dept,
                "Date Issued": date_in,
                "Condition": condition,
                "Accessories Included": accessories,
                "Return Date": return_dt,
                "Notes": notes
            }
            df = pd.concat([pd.DataFrame([new]), df], ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.success("✅ New asset added! Refresh to see it.")

# ────────────────────── PAGE 2: password reset guide ───────────────
elif page == "Password Reset Guide":
    st.title("🔐 Password Reset Guide")
    st.markdown("Follow these steps to reset a user’s password securely in Microsoft 365:")

    steps = [
        "Log into Microsoft 365 Admin Center",
        "Go to users then active users",
        "Search and select the employee's name",
        "Click 'Reset password'",
        "Auto generate a temporary password",
        "Require password change at next login",
        "Share password securely (email/phone)",
        "Confirm login to Outlook or Teams",
        "Document password reset internally"
    ]

    for i, step in enumerate(steps, 1):
        st.markdown(f"**Step {i}:** {step}")
        
# ────────────────────── PAGE 3: ONBOARDING CHECKLIST ───────────────
elif page == "Onboarding Checklist":
    import os

    st.title("📝 Onboarding Checklist Manager")
    st.markdown("Manage onboarding steps for each new employee using checkboxes.")

    # Define standard checklist tasks
    checklist_tasks = [
        "Create user account",
        "Assign Microsoft license (Office, Outlook, Teams)",
        "Add to Teams groups: Admissions, All staff",
        "Create Zoom account",
        "Set up laptop with apps (Office, Zoom, Chrome, Adobe)",
        "Log asset in tracker (laptop, charger, mouse)",
        "Schedule onboarding Zoom call",
        "Send credentials securely",
        "Walk user through login",
        "Mark checklist complete"
    ]

    checklist_file = 'onboarding_checklist.csv'

    # Load or initialize checklist data
    if os.path.exists(checklist_file):
        data = pd.read_csv(checklist_file)
    else:
        data = pd.DataFrame(columns=["Employee", "Task", "Status"])

    # Form to add a new employee
    with st.form("add_new_employee"):
        new_emp = st.text_input("Enter new employee name")
        submit = st.form_submit_button("Add Employee")
        if submit and new_emp:
            if new_emp in data["Employee"].unique():
                st.warning("Employee already exists.")
            else:
                new_rows = pd.DataFrame({
                    "Employee": [new_emp] * len(checklist_tasks),
                    "Task": checklist_tasks,
                    "Status": ["Pending"] * len(checklist_tasks)
                })
                data = pd.concat([data, new_rows], ignore_index=True)
                data.to_csv(checklist_file, index=False)
                st.success(f"Checklist created for {new_emp}!")

    # Select employee to view/edit
    employees = sorted(data["Employee"].unique())
    if employees:
        selected_emp = st.selectbox("Select an employee", employees)

        emp_tasks = data[data["Employee"] == selected_emp].reset_index(drop=True)
        edited = False

        st.write("### Checklist for:", selected_emp)

        for i, row in emp_tasks.iterrows():
            col1, col2 = st.columns([0.75, 0.25])
            col1.write(f"**{row['Task']}**")
            is_done = True if row["Status"] == "Done" else False
            updated = col2.checkbox("Done", value=is_done, key=f"{selected_emp}_{i}")
            new_status = "Done" if updated else "Pending"
            if new_status != row["Status"]:
                data.loc[
                    (data["Employee"] == selected_emp) & (data["Task"] == row["Task"]),
                    "Status"
                ] = new_status
                edited = True

        if edited:
            data.to_csv(checklist_file, index=False)
            st.success("✅ Checklist updated successfully!")
    else:
        st.info("No employees yet. Add one using the form above.")