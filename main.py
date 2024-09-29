import streamlit as st
from model import Chatbot  # Import the Chatbot class from model.py
import sqlite3
from datetime import datetime
import pandas as pd #type:ignore
import os

# Initialize the chatbot
chatbot = Chatbot()

# Create directory for file uploads if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Inject custom CSS to style the app with a modern look
def apply_custom_css():
    st.markdown(
        """
        <style>
        /* General styling */
        body {
            background-color: #f5f7fa;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
        }

        /* Header styling */
        .header {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 28px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        }

        /* Subheader styling */
        .subheader {
            font-size: 20px;
            color: #6a11cb;
            margin-bottom: 10px;
            font-weight: bold;
            text-align: center;
        }

        /* Card styling for dashboard */
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }

        /* Button styling */
        .stButton button {
            background-color: #2575fc;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 20px;
            border: none;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease-in-out;
            margin-top: 10px;
            cursor: pointer;
        }

        .stButton button:hover {
            background-color: #6a11cb;
            transform: translateY(-2px);
        }

        /* Input field styling */
        textarea, input {
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 8px;
            width: 100%;
            margin-bottom: 10px;
            box-sizing: border-box;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #888;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Initialize the SQLite database
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Create tables for user data
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT DEFAULT 'user'  -- Roles: 'user' or 'admin'
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS user_activity (
        username TEXT,
        activity TEXT,
        timestamp TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS quiz_scores (
        username TEXT,
        score INTEGER,
        date TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS user_inputs (
        username TEXT,
        input_text TEXT,
        timestamp TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')
conn.commit()

# Function to verify login credentials
def verify_login(username, password):
    # Checks if the username and password match an existing user in the database
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone() is not None

# Function to check user role
def get_user_role(username):
    # Fetches the role of the user (e.g., 'user' or 'admin') from the database
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    return result[0] if result else None

# Function to create a new user
def create_user(username, password, role='user'):
    # Attempts to create a new user in the database
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # User already exists

# Function to log user activity
def log_activity(username, activity):
    # Logs user activities such as logins and quiz attempts
    c.execute("INSERT INTO user_activity (username, activity, timestamp) VALUES (?, ?, ?)",
              (username, activity, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# Function to save quiz score
def save_quiz_score(username, score):
    # Saves the user's quiz score to the database
    c.execute("INSERT INTO quiz_scores (username, score, date) VALUES (?, ?, ?)",
              (username, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# Main Chatbot Interaction
def chatbot_interaction():
    st.subheader("🤖 Chatbot Assistant")
    user_input = st.text_input("Ask a question or type 'quiz' to start:", "")
    
    if user_input:
        # Interacts with the chatbot: teaching or quizzing based on user input
        response = chatbot.chat(user_input)
        if response["type"] == "teach":
            st.write("Bot:", response["response"])
        elif response["type"] == "quiz":
            st.write("Bot: Let's start a quiz!")
            st.write(f"**Question:** {response['question']}")
            user_answer = st.text_input("Your answer:", "")
            if user_answer:
                correct, feedback = chatbot.evaluate_quiz_answer(user_answer, response["answer"])
                st.write("Bot:", feedback)

# PDF Upload for Knowledge Extraction
def pdf_upload():
    st.subheader("📤 Upload Textbook")
    uploaded_file = st.file_uploader("Upload a PDF file:", type=["pdf"])
    
    if uploaded_file:
        # Saves the uploaded PDF and extracts content to build the chatbot's knowledge base
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        response = chatbot.extract_text_from_pdf(file_path)
        st.success(response)

# Login and Sign-Up Pages
def login_page():
    st.markdown("<div class='header'>🔐 Login</div>", unsafe_allow_html=True)
    username = st.text_input("Username", key='login_username', help="Enter your username.")
    password = st.text_input("Password", type="password", key='login_password', help="Enter your password.")
    
    # Place the Login and Sign Up buttons side by side
    col1, col2 = st.columns([1, 1])  # Equal width columns to place buttons side by side
    
    with col1:
        if st.button("Login", key='login_button'):
            if verify_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = get_user_role(username)
                log_activity(username, "Logged in")
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")

    with col2:
        if st.button("Sign Up", key='signup_button'):
            st.session_state.page = "signup"

def signup_page():
    st.markdown("<div class='header'>📝 Sign Up</div>", unsafe_allow_html=True)
    username = st.text_input("Choose a Username", key='signup_username', help="Choose a unique username.")
    password = st.text_input("Choose a Password", type="password", key='signup_password', help="Create a secure password.")
    if st.button("Sign Up", key='create_account_button'):
        if create_user(username, password):
            st.success("Sign up successful! You can now log in.")
            st.session_state.page = "login"
        else:
            st.error("Username already exists. Please choose a different one.")

# Main App Layout with Authentication
def main_app():
    st.markdown("<div class='header'>🎓 AI-Powered IT Education Platform</div>", unsafe_allow_html=True)

    # Sidebar for navigation with icons
    st.sidebar.title("📚 Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Chatbot", "Upload PDF", "Log Out"],
        index=0,
        format_func=lambda x: f"➡️ {x}"
    )

    # Load the selected section based on user choice
    if app_mode == "Chatbot":
        chatbot_interaction()
    elif app_mode == "Upload PDF":
        pdf_upload()
    elif app_mode == "Log Out":
        log_activity(st.session_state.username, "Logged out")
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.success("You have been logged out.")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "role" not in st.session_state:
    st.session_state.role = None

# Apply custom CSS styling
apply_custom_css()

# App Navigation based on authentication
if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
