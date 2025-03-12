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
    .author-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
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

# Function to display author details
def show_author_details(author_key):
    try:
        # Get detailed author information
        author_url = f"https://openlibrary.org/authors/{author_key}.json"
        response = requests.get(author_url)
        response.raise_for_status()
        author_data = response.json()
        
        # Display author details in an expander
        with st.expander(f"Details for {author_data.get('name', 'Unknown Author')}"):
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
                st.write("**Biography:**")
                st.write(bio_text)
                
            # Personal URLs
            if 'links' in author_data and author_data['links']:
                st.write("**External Links:**")
                for link in author_data['links']:
                    if 'url' in link and 'title' in link:
                        st.markdown(f"- [{link['title']}]({link['url']})")
            
            # Wikipedia URL
            if 'wikipedia' in author_data:
                st.markdown(f"[View on Wikipedia]({author_data['wikipedia']})")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching author details: {str(e)}")

# Search for authors when there's input
if author_name:
    with st.spinner('Searching for authors...'):
        # Create the search URL
        search_url = f"https://openlibrary.org/search/authors.json?q={author_name}"
        
        try:
            # Make the API request
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()
            
            # Check if any authors were found
            if data["numFound"] > 0:
                # Create a list to store the table data
                table_data = []
                
                # Collect data for each author
                for author in data["docs"]:
                    # Extract author key from the full key (e.g., "/authors/OL23919A" -> "OL23919A")
                    author_key = author["key"].split("/")[-1]
                    
                    table_data.append({
                        "Author ID": author_key,
                        "Author Name": author["name"],
                        "Most Popular Work": author.get("top_work", "N/A"),
                        "Number of Works": author.get("work_count", "N/A")
                    })
                
                # Create a DataFrame
                df = pd.DataFrame(table_data)
                
                # Create session state for clicked author
                if 'clicked_author' not in st.session_state:
                    st.session_state.clicked_author = None
                
                # Display the table with clickable Author IDs
                clicked = st.dataframe(
                    df,
                    hide_index=True,
                    column_config={
                        "Author ID": st.column_config.TextColumn(
                            "Author ID",
                            width="small",
                            help="Click on ID to view details"
                        ),
                        "Author Name": st.column_config.TextColumn(
                            "Author Name",
                            width="medium"
                        ),
                        "Most Popular Work": st.column_config.TextColumn(
                            "Most Popular Work",
                            width="medium"
                        ),
                        "Number of Works": st.column_config.NumberColumn(
                            "Number of Works",
                            width="small"
                        )
                    }
                )
                
                # Handle clicks on Author IDs
                for idx, row in df.iterrows():
                    author_key = row['Author ID']
                    if st.button(f"View {author_key}", key=f"btn_{author_key}"):
                        show_author_details(author_key)
                
                st.caption(f"Found {data['numFound']} author(s)")
            
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")
