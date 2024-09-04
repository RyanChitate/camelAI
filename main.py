import streamlit as st
import openai

# OpenAI API Key (Replace with your actual API key)
openai.api_key = "your_openai_api_key"

# Simulated user database (for demonstration purposes)
user_db = {
    "user1": {"password": "password123"},
    "user2": {"password": "pass456"}
}

# Function to verify login credentials
def verify_login(username, password):
    if username in user_db and user_db[username]["password"] == password:
        return True
    return False

# Function to create a new user
def create_user(username, password):
    if username in user_db:
        return False  # User already exists
    user_db[username] = {"password": password}
    return True

# Define functions to interact with the AI model
def generate_answer(question):
    """Generates an AI-based answer to an IT-related question."""
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use appropriate model
        prompt=question,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def it_quiz():
    """A simple IT quiz with multiple choice questions."""
    st.subheader("IT Quiz")

    questions = {
        "What does CPU stand for?": ["Central Processing Unit", "Central Programming Unit", "Central Performance Unit"],
        "Which is a programming language?": ["Python", "Snake", "Tiger"],
        "What does HTTP stand for?": ["HyperText Transfer Protocol", "HighText Transfer Protocol", "HyperTransfer Protocol"]
    }

    score = 0
    for question, options in questions.items():
        answer = st.radio(question, options)
        if (question == "What does CPU stand for?" and answer == "Central Processing Unit") or \
           (question == "Which is a programming language?" and answer == "Python") or \
           (question == "What does HTTP stand for?" and answer == "HyperText Transfer Protocol"):
            score += 1

    if st.button("Submit"):
        st.write(f"Your score: {score}/{len(questions)}")

# Login and Sign-Up Pages
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            if verify_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")
    
    with col2:
        if st.button("Sign Up"):
            st.session_state.page = "signup"

def signup_page():
    st.title("Sign Up")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Sign Up"):
        if create_user(username, password):
            st.success("Sign up successful! You can now log in.")
            st.session_state.page = "login"
        else:
            st.error("Username already exists. Please choose a different one.")

# Main App Layout with Authentication
def main_app():
    st.title("AI-Powered IT Education Platform")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose the app mode", ["Home", "Ask AI", "Take IT Quiz", "Learning Resources", "Log Out"])

    if app_mode == "Home":
        st.write("Welcome to the AI-powered IT education platform. You can explore different IT topics, ask questions, and test your knowledge with quizzes.")

    elif app_mode == "Ask AI":
        st.subheader("Ask AI an IT-related question")

        # Input question
        question = st.text_input("Enter your IT-related question:")
        if st.button("Get Answer"):
            if question:
                with st.spinner("Generating answer..."):
                    answer = generate_answer(question)
                st.write("Answer:", answer)
            else:
                st.write("Please enter a question.")

    elif app_mode == "Take IT Quiz":
        it_quiz()

    elif app_mode == "Learning Resources":
        st.subheader("Learning Resources")
        st.write("Here are some useful IT learning resources:")
        st.write("- [W3Schools](https://www.w3schools.com)")
        st.write("- [Mozilla Developer Network](https://developer.mozilla.org)")
        st.write("- [Khan Academy](https://www.khanacademy.org/computing/computer-programming)")

    elif app_mode == "Log Out":
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("You have been logged out.")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# App Navigation based on authentication
if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
