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
                        "Number of Works": author.get("work_count", "N/A"),
                        "View Author Details": f"https://openlibrary.org/authors/{author_key}"
                    })
                
                # Create a DataFrame
                df = pd.DataFrame(table_data)

                # Display the table
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config={
                        "Author ID": st.column_config.TextColumn(
                            "Author ID",
                            width="small"
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
                        ),
                        "View Author Details": st.column_config.LinkColumn(
                            "View Author Details",
                            width="small",
                            help="Click to view author details on Open Library"
                        )
                    }
                )
                
                st.caption(f"Found {data['numFound']} author(s)")
            
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")
