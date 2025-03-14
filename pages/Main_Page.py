import streamlit as st
import requests
import json
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Author Search | Open Library",
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
        
        /* Container and table styling */
        .block-container {
            max-width: 1000px !important;
            padding-top: 2rem !important;
            padding-right: 2rem !important;
            padding-left: 2rem !important;
            margin: 0 auto;
        }
        
        [data-testid="stDataFrame"] {
            width: 100% !important;
            min-height: 110px !important;
        }
        
        [data-testid="stDataFrame"] > div {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
        }
        
        /* Table header styling */
        [data-testid="stDataFrame"] thead tr th {
            background-color: #1E3D59 !important;
            color: white !important;
            padding: 12px !important;
            height: 50px !important;
            line-height: 25px !important;
        }
        
        /* Table row styling */
        [data-testid="stDataFrame"] tbody tr {
            height: 50px !important;
            line-height: 50px !important;
        }
        
        [data-testid="stDataFrame"] tbody td {
            padding: 8px 12px !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        
        [data-testid="stDataFrame"] tbody tr:nth-of-type(odd) {
            background-color: #ffffff;
        }
        
        [data-testid="stDataFrame"] tbody tr:nth-of-type(even) {
            background-color: #f0f2f5;
        }
        
        [data-testid="stDataFrame"] tbody tr:hover {
            background-color: #e9ecef;
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
                
                # Collect data for each author with filtering
                for author in data["docs"]:
                    # Skip authors with no works or no birth date
                    work_count = author.get("work_count", 0)
                    birth_date = author.get("birth_date")
                    
                    if work_count >= 1 and birth_date:
                        author_key = author["key"].split("/")[-1]
                        table_data.append({
                            "Author ID": author_key,
                            "Author Name": author["name"],
                            "Most Popular Work": author.get("top_work", "N/A"),
                            "Number of Works": work_count,
                            "Details": f"/Author_Details?author_id={author_key}"
                        })
                
                # Create a DataFrame and display it as a table if there are filtered results
                if table_data:
                    df = pd.DataFrame(table_data)
                    
                    st.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True,
                        height=min(len(df) * 50 + 70, 400),
                        column_config={
                            "Author ID": st.column_config.TextColumn(
                                "Author ID",
                                width=None,
                            ),
                            "Author Name": st.column_config.TextColumn(
                                "Author Name",
                                width=None,
                            ),
                            "Most Popular Work": st.column_config.TextColumn(
                                "Most Popular Work",
                                width=None,
                            ),
                            "Number of Works": st.column_config.NumberColumn(
                                "Number of Works",
                                width=None,
                            ),
                            "Details": st.column_config.LinkColumn(
                                "Details",
                                width=None,
                                help="Click to view author details",
                                display_text="View Details"
                            )
                        }
                    )
                    
                    st.caption(f"Found {len(table_data)} author(s) with works and birth date information")
                else:
                    st.warning("No authors found matching your criteria (must have works and birth date information)")
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")
