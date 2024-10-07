import streamlit as st
import sqlite3
import hashlib

# Database Functions
def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def create_admintable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins(username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

def add_admin(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO admins(username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

def get_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

def get_admin(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
    admin = c.fetchone()
    conn.close()
    return admin

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT rowid, * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def update_user(rowid, username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET username = ?, password = ? WHERE rowid = ?', (username, password, rowid))
    conn.commit()
    conn.close()

def delete_user(rowid):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE rowid = ?', (rowid,))
    conn.commit()
    conn.close()

# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Sign Up Page
def signup():
    st.subheader("Sign Up")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    if st.button("Sign Up"):
        if new_user and new_password:
            hashed_password = hash_password(new_password)
            add_user(new_user, hashed_password)
            st.success("You have successfully signed up!")
        else:
            st.error("Please enter both username and password.")

# Login Page
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        hashed_password = hash_password(password)
        
        user = get_user(username, hashed_password)
        admin = get_admin(username, hashed_password)
        
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = "user"
            st.success("Logged in successfully!")
            st.experimental_rerun()
        elif admin:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = "admin"
            st.success("Admin logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password.")

# Admin Page
def admin():
    st.subheader("Admin Panel")
    users = get_all_users()
    if users:
        for user in users:
            rowid, username, password = user
            st.write(f"UserID: {rowid}, Username: {username}")
            
            new_username = st.text_input(f"Update Username for {rowid}", value=username)
            new_password = st.text_input(f"Update Password for {rowid}", type='password')
            if st.button(f"Update User {rowid}"):
                update_user(rowid, new_username, hash_password(new_password))
                st.success("User updated successfully.")
                st.experimental_rerun()
            
            if st.button(f"Delete User {rowid}"):
                delete_user(rowid)
                st.success("User deleted successfully.")
                st.experimental_rerun()
    else:
        st.write("No users found.")

# Main App Function
def main():
    st.title("Streamlit App with Separate Admin Table")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    menu = ["Home", "Login", "Sign Up", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    create_usertable()
    create_admintable()

    if choice == "Home":
        st.write("Welcome to the app!")
        if st.session_state["logged_in"]:
            st.write(f"Hello, {st.session_state['username']}!")
        else:
            st.write("Please login or sign up.")
            
    elif choice == "Login":
        login()
        
    elif choice == "Sign Up":
        signup()

    elif choice == "Admin":
        if st.session_state["logged_in"] and st.session_state["role"] == "admin":
            admin()
        else:
            st.error("Admin access only.")

if __name__ == '__main__':
    main()

