# main.py
import streamlit as st

css_file = "./static/style.css"

def load_css(file_name):
    with open(file_name, "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Load external CSS file
load_css(css_file)

# Create the sidebar menu
menu_options = ["SideBar1", "SideBar2", "SideBar3"]
selected_option = st.sidebar.radio("Navigation", menu_options)

# Define the content for each section
if selected_option == "SideBar1":
    st.title("Welcome to the Streamlit App")
    st.write("Navigate to different sections using the sidebar.")

elif selected_option == "SideBar2":
    st.title("Resume Analysis")
    st.write("Upload a resume file for analysis.")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file:
        st.write(f"File uploaded: {uploaded_file.name}")
        # Add your analysis logic here

elif selected_option == "SideBar3":
    st.title("Search for Values")
    search_query = st.text_input("Enter your search query")
    if st.button("Search"):
        st.write(f"Results for: {search_query}")
        # Add your search logic here
