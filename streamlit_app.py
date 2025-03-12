import streamlit as st
import requests
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
    </style>
""", unsafe_allow_html=True)

# App header
st.title("📚 Author Search")
st.markdown("""
    <p style='font-size: 1.2rem; color: #666;'>
        Search for authors in the Open Library database
    </p>
""", unsafe_allow_html=True)

# Function to fetch author details
def get_author_details(author_id):
    url = f"https://openlibrary.org/authors/{author_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

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
                for index, author in enumerate(data["docs"]):
                    author_key = author["key"].split("/")[-1]
                    
                    table_data.append({
                        "Author ID": author_key,
                        "Author Name": author["name"],
                        "Most Popular Work": author.get("top_work", "N/A"),
                        "Number of Works": author.get("work_count", "N/A"),
                        "View Details": f"view_{index}"  # Using index to ensure uniqueness
                    })
                
                # Create a DataFrame
                df = pd.DataFrame(table_data)
                
                # Display the table using st.data_editor with action buttons
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Author ID": st.column_config.TextColumn("Author ID", width="small"),
                        "Author Name": st.column_config.TextColumn("Author Name", width="medium"),
                        "Most Popular Work": st.column_config.TextColumn("Most Popular Work", width="medium"),
                        "Number of Works": st.column_config.NumberColumn("Number of Works", width="small"),
                        "View Details": st.column_config.TextColumn("Click Below")
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="author_table"
                )
                
                # Ensure unique keys for buttons
                selected_author_id = None
                for index, row in df.iterrows():
                    if st.button("View Details", key=f"view_btn_{index}"):
                        selected_author_id = row["Author ID"]
                        st.session_state["selected_author"] = selected_author_id
                
                # Retrieve details if an author was selected
                if "selected_author" in st.session_state:
                    selected_author_id = st.session_state["selected_author"]
                    author_details = get_author_details(selected_author_id)
                    if author_details:
                        st.subheader(f"Details for {author_details.get('name', 'Unknown Author')}")
                        st.markdown(f"**Birth Date:** {author_details.get('birth_date', 'N/A')}")
                        st.markdown(f"**Death Date:** {author_details.get('death_date', 'N/A')}")
                        st.markdown(f"**Top Work:** {author_details.get('top_work', 'N/A')}")
                        st.markdown(f"**Work Count:** {author_details.get('work_count', 'N/A')}")
                        st.markdown(f"**Bio:** {author_details.get('bio', 'N/A')}")
                    else:
                        st.warning("Could not retrieve author details.")
                
                st.caption(f"Found {data['numFound']} author(s)")
            
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")
