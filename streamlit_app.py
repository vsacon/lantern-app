import streamlit as st
import requests
import json
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Author Search | Open Library",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTitle {
        color: #1E3D59;
        font-size: 3rem !important;
        padding-bottom: 2rem;
    }
    .author-details {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E3D59;
    }
    .author-bio {
        margin-top: 1rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.title("📚 Author Search")
st.markdown("""
    <p style='font-size: 1.2rem; color: #666;'>
        Search for authors in the Open Library database
    </p>
""", unsafe_allow_html=True)

# Create a text input for author search
author_name = st.text_input("Enter author name:", placeholder="e.g., J.K. Rowling, Stephen King")

# Function to get author details
def get_author_details(author_key):
    try:
        author_url = f"https://openlibrary.org/authors/{author_key}.json"
        response = requests.get(author_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

# Search for authors when there's input
if author_name:
    with st.spinner('Searching for authors...'):
        try:
            # Create the search URL
            search_url = f"https://openlibrary.org/search/authors.json?q={author_name}"
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()
            
            # Check if any authors were found
            if data["numFound"] > 0:
                # Initialize session state for expanded rows if not exists
                if 'expanded_rows' not in st.session_state:
                    st.session_state.expanded_rows = set()
                
                # Display authors
                for author in data["docs"]:
                    author_key = author["key"].split("/")[-1]
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                    
                    with col1:
                        st.write("**ID:**", author_key)
                    with col2:
                        st.write("**Name:**", author["name"])
                    with col3:
                        st.write("**Most Popular Work:**", author.get("top_work", "N/A"))
                    with col4:
                        st.write("**Works:**", author.get("work_count", "N/A"))
                    
                    # Add expand/collapse button
                    if st.button("Show Details" if author_key not in st.session_state.expanded_rows else "Hide Details", 
                               key=f"btn_{author_key}"):
                        if author_key in st.session_state.expanded_rows:
                            st.session_state.expanded_rows.remove(author_key)
                        else:
                            st.session_state.expanded_rows.add(author_key)
                    
                    # Show author details if expanded
                    if author_key in st.session_state.expanded_rows:
                        author_data = get_author_details(author_key)
                        if author_data:
                            st.markdown("<div class='author-details'>", unsafe_allow_html=True)
                            
                            # Basic Information
                            if 'birth_date' in author_data:
                                st.write(f"**Birth Date:** {author_data['birth_date']}")
                            if 'death_date' in author_data:
                                st.write(f"**Death Date:** {author_data['death_date']}")
                            
                            # Bio
                            if 'bio' in author_data:
                                bio_text = author_data['bio']
                                if isinstance(bio_text, dict) and 'value' in bio_text:
                                    bio_text = bio_text['value']
                                st.markdown("<div class='author-bio'>", unsafe_allow_html=True)
                                st.write("**Biography:**")
                                st.write(bio_text)
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # External Links
                            if 'links' in author_data and author_data['links']:
                                st.write("**External Links:**")
                                for link in author_data['links']:
                                    if 'url' in link and 'title' in link:
                                        st.markdown(f"- [{link['title']}]({link['url']})")
                            
                            # Wikipedia URL
                            if 'wikipedia' in author_data:
                                st.markdown(f"[View on Wikipedia]({author_data['wikipedia']})")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error("Could not fetch author details")
                    
                    st.markdown("---")
                
                st.caption(f"Found {data['numFound']} author(s)")
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")
