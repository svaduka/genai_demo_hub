import streamlit as st
import logging
from logger import log_msg,configure_logging  # Assuming logger class is in logger.py

css_file = "./static/style.css"

configure_logging() # DONOT REMOVE

def load_css(file_name):
    """
    Load the CSS file and apply it to the Streamlit app.
    """
    try:
        with open(file_name, "r") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
        log_msg(f"CSS file '{file_name}' loaded successfully.", level=logging.INFO)
    except FileNotFoundError:
        log_msg(f"CSS file '{file_name}' not found.", level=logging.ERROR)
    except Exception as e:
        log_msg(f"Error loading CSS file '{file_name}': {str(e)}", level=logging.ERROR)

# Load external CSS file
load_css(css_file)

# Create the sidebar menu
menu_options = ["SideBar1", "SideBar2", "SideBar3"]
log_msg(f"Sidebar menu created with options: {menu_options}", level=logging.INFO)

selected_option = st.sidebar.radio("Navigation", menu_options)
log_msg(f"User selected sidebar option: {selected_option}", level=logging.INFO)

# Define the content for each section
if selected_option == "SideBar1":
    st.title("Welcome to the Streamlit App")
    st.write("Navigate to different sections using the sidebar.")
    log_msg("Loaded SideBar1: Welcome screen displayed.", level=logging.INFO)

elif selected_option == "SideBar2":
    st.title("Resume Analysis")
    st.write("Upload a resume file for analysis.")
    log_msg("Loaded SideBar2: Resume Analysis section displayed.", level=logging.INFO)

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file:
        st.write(f"File uploaded: {uploaded_file.name}")
        log_msg(f"File uploaded: {uploaded_file.name}", level=logging.INFO)
        # Add your analysis logic here

elif selected_option == "SideBar3":
    st.title("Search for Values")
    st.write("Enter your search query below.")
    log_msg("Loaded SideBar3: Search for Values section displayed.", level=logging.INFO)

    search_query = st.text_input("Enter your search query")
    if st.button("Search"):
        st.write(f"Results for: {search_query}")
        log_msg(f"Search performed with query: '{search_query}'", level=logging.INFO)
        # Add your search logic here