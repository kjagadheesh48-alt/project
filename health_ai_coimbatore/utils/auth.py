import streamlit as st

def login():
    st.sidebar.subheader("Admin Login")

    user = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if user == "admin" and password == "1234":
        return True
    elif user and password:
        st.sidebar.error("Invalid credentials")
    return False