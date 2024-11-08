import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

# Hash function to securely store passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
def init_db():
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    reg_number TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL)''')
    # Biological data table
    c.execute('''CREATE TABLE IF NOT EXISTS biological_data (
                    record_id INTEGER PRIMARY KEY,
                    sample_name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    collection_date TEXT,
                    collected_by TEXT,
                    description TEXT)''')
    # Access logs table
    c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
                    log_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    access_time TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id))''')
    conn.commit()
    conn.close()

# Register a new user
def register_user(name, reg_number, password, role):
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    password_hash = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('INSERT INTO users (name, reg_number, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)', 
                  (name, reg_number, password_hash, role, created_at))
        conn.commit()
        st.success("\U0001F973 Account created successfully!")
    except sqlite3.IntegrityError:
        st.error("\u26A0 Registration number already exists. Please use a different one.")
    conn.close()

# Authenticate a user
def authenticate_user(reg_number, password):
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('SELECT * FROM users WHERE reg_number = ? AND password_hash = ?', (reg_number, password_hash))
    user = c.fetchone()
    conn.close()
    return user

# Log user access
def log_access(user_id, activity):
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO access_logs (user_id, access_time, activity) VALUES (?, ?, ?)', (user_id, access_time, activity))
    conn.commit()
    conn.close()

# Add biological data
def add_biological_data(sample_name, species, collection_date, collected_by, description):
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    c.execute('INSERT INTO biological_data (sample_name, species, collection_date, collected_by, description) VALUES (?, ?, ?, ?, ?)',
              (sample_name, species, collection_date, collected_by, description))
    conn.commit()
    conn.close()

# View biological data
def view_biological_data():
    conn = sqlite3.connect('biological_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM biological_data')
    data = c.fetchall()
    conn.close()
    return data

# Streamlit application UI
st.markdown("""
    <style>
        .reportview-container {
            background: #f7f7f7;
        }
        .sidebar .sidebar-content {
            background: #2f4f4f;
            color: white;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("\U0001F33F Angela's Biological Database")

st.markdown("""
### About Angela's Biological Database
Angela's Biological Database is a secure platform designed to facilitate the collection, storage, and management of biological data. The application is intended for research partners and general users who are interested in working with biological samples and related metadata.

**Features of the App:**
- **User Registration and Authentication**: Users can create accounts, log in securely, and access data based on their roles.
- **Data Management**: Research partners can add biological data, including information such as sample name, species, collection date, and more.
- **Data Access**: General users can view the collected data, while research partners have additional privileges to add new entries.
- **Access Logging**: All user activities are logged to ensure accountability and security.

**Database Type**: The app uses an SQLite database, which is lightweight and ideal for small to medium-sized applications. It helps store user details, biological data, and access logs efficiently.

The goal of this application is to provide a user-friendly and accessible tool for researchers to collaborate and share biological information in a structured manner.
""")

# Database initialization
init_db()

# Sidebar for user authentication and registration
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("📋 Menu", menu)

if choice == "Register":
    st.sidebar.markdown("### \👤 Create a New Account")
    name = st.sidebar.text_input("Name")
    reg_number = st.sidebar.text_input("Registration Number")
    password = st.sidebar.text_input("Password", type='password')
    role = st.sidebar.selectbox("Role", ["Research Partner", "General User"])
    if st.sidebar.button("Register"):
        if name and reg_number and password:
            register_user(name, reg_number, password, role)
        else:
            st.sidebar.error("\u26A0 Please fill in all fields.")

elif choice == "Login":
    if not st.session_state.authenticated:
        st.sidebar.markdown("### 🔒 Login to Your Account")
        reg_number = st.sidebar.text_input("Registration Number")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            user = authenticate_user(reg_number, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success(f"\U0001F44B Welcome, {user[1]}!")
                log_access(user[0], "Login")
            else:
                st.sidebar.error("\u26A0 Invalid credentials. Please try again.")

if st.session_state.authenticated:
    user = st.session_state.user
    if user[4] == "Research Partner":
        st.subheader("📄 Add Biological Data")
        sample_name = st.text_input("Sample Name")
        species = st.text_input("Species")
        collection_date = st.date_input("Collection Date")
        collected_by = st.text_input("Collected By")
        description = st.text_area("Description")
        if st.button("Add Data"):
            if sample_name and species:
                add_biological_data(sample_name, species, collection_date, collected_by, description)
                st.success("\U00002705 Data added successfully!")
            else:
                st.error("\u26A0 Please fill in all mandatory fields.")
        
        # View Biological Data for Research Partner
        st.subheader("📋 View Biological Data")
        data = view_biological_data()
        df = pd.DataFrame(data, columns=["Record ID", "Sample Name", "Species", "Collection Date", "Collected By", "Description"])
        st.table(df)
    else:
        st.subheader("\U0001F4D2 View Biological Data")
        data = view_biological_data()
        df = pd.DataFrame(data, columns=["Record ID", "Sample Name", "Species", "Collection Date", "Collected By", "Description"])
        st.table(df)

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.sidebar.success("\U00002705 Logged out successfully!")

st.sidebar.markdown("---")
if st.sidebar.button("🔑 Forgot Password?"):
    st.sidebar.write("Feature to reset password coming soon!")
