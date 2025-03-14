import streamlit as st
import requests

# Set page config
#test commit
st.set_page_config(
    page_title="Author Details | Open Library",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        section[data-testid="stSidebar"] {display: none;}
        
        .block-container {
            max-width: 1000px !important;
            padding-top: 2rem !important;
            padding-right: 2rem !important;
            padding-left: 2rem !important;
            margin: 0 auto;
        }
        
        .author-bio {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .author-details {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Get author_id from URL parameters
author_id = st.query_params.get("author_id", None)

if author_id:
    try:
        # Fetch author details
        response = requests.get(f"https://openlibrary.org/authors/{author_id}.json")
        response.raise_for_status()
        author_data = response.json()
        
        # Display author information
        st.title(f"📚 {author_data.get('name', 'Unknown Author')}")
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Biography section
            if "bio" in author_data:
                st.subheader("Biography")
                st.markdown(f'<div class="author-bio">{author_data["bio"]}</div>', unsafe_allow_html=True)
            
            # Works section
            if "remote_ids" in author_data:
                st.subheader("External Links")
                st.markdown('<div class="author-details">', unsafe_allow_html=True)
                for source, id in author_data["remote_ids"].items():
                    st.write(f"**{source.title()}:** {id}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Author details card
            st.markdown('<div class="author-details">', unsafe_allow_html=True)
            
            if "birth_date" in author_data:
                st.write("**Birth Date:**", author_data["birth_date"])
            
            if "death_date" in author_data:
                st.write("**Death Date:**", author_data["death_date"])
            
            if "fuller_name" in author_data:
                st.write("**Full Name:**", author_data["fuller_name"])
                
            if "wikipedia" in author_data:
                st.write("**Wikipedia:**", author_data["wikipedia"])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Raw JSON data in expander
            with st.expander("View Raw JSON Data"):
                st.json(author_data)
        
        # Back button
        if st.button("← Back to Search"):
            st.switch_page("Main_Page.py")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching author details: {str(e)}")
        if st.button("← Back to Search"):
            st.switch_page("Main_Page.py")
else:
    st.error("No author ID provided")
    if st.button("← Back to Search"):
        st.switch_page("Main_Page.py") 