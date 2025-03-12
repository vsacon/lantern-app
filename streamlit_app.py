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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .author-name {
        color: #1E3D59;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .author-metadata {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .author-bio {
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 1.5rem 0;
    }
    .external-links {
        background-color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    .back-button {
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'search'
if 'author_key' not in st.session_state:
    st.session_state.author_key = None

def show_author_details(author_key):
    try:
        # Get detailed author information
        author_url = f"https://openlibrary.org/authors/{author_key}.json"
        response = requests.get(author_url)
        response.raise_for_status()
        author_data = response.json()
        
        # Back button
        if st.button("← Back to Search", key="back_button"):
            st.session_state.page = 'search'
            st.rerun()
        
        # Author name header
        st.markdown(f"<h1 class='author-name'>{author_data.get('name', 'Unknown Author')}</h1>", unsafe_allow_html=True)
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Author metadata
            metadata = []
            if 'birth_date' in author_data:
                metadata.append(f"Born: {author_data['birth_date']}")
            if 'death_date' in author_data:
                metadata.append(f"Died: {author_data['death_date']}")
            
            if metadata:
                st.markdown(f"<div class='author-metadata'>{' | '.join(metadata)}</div>", unsafe_allow_html=True)
            
            # Biography
            if 'bio' in author_data:
                bio_text = author_data['bio']
                if isinstance(bio_text, dict) and 'value' in bio_text:
                    bio_text = bio_text['value']
                st.markdown("<div class='author-card'>", unsafe_allow_html=True)
                st.markdown("### Biography")
                st.markdown(f"<div class='author-bio'>{bio_text}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # External Links Card
            st.markdown("<div class='author-card'>", unsafe_allow_html=True)
            st.markdown("### External Links")
            
            if 'wikipedia' in author_data:
                st.markdown(f"🌐 [Wikipedia]({author_data['wikipedia']})")
            
            if 'links' in author_data and author_data['links']:
                for link in author_data['links']:
                    if 'url' in link and 'title' in link:
                        st.markdown(f"🔗 [{link['title']}]({link['url']})")
            
            # Open Library Link
            st.markdown(f"📚 [Open Library Profile](https://openlibrary.org/authors/{author_key})")
            st.markdown("</div>", unsafe_allow_html=True)
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching author details: {str(e)}")
        if st.button("← Back to Search"):
            st.session_state.page = 'search'
            st.rerun()

def show_search_page():
    # App header
    st.title("📚 Author Search")
    st.markdown("""
        <p style='font-size: 1.2rem; color: #666;'>
            Search for authors in the Open Library database
        </p>
    """, unsafe_allow_html=True)

    # Create a text input for author search
    author_name = st.text_input("Enter author name:", placeholder="e.g., J.K. Rowling, Stephen King")

    if author_name:
        with st.spinner('Searching for authors...'):
            search_url = f"https://openlibrary.org/search/authors.json?q={author_name}"
            
            try:
                response = requests.get(search_url)
                response.raise_for_status()
                data = response.json()
                
                if data["numFound"] > 0:
                    table_data = []
                    
                    for author in data["docs"]:
                        author_key = author["key"].split("/")[-1]
                        
                        table_data.append({
                            "Author ID": author_key,
                            "Author Name": author["name"],
                            "Most Popular Work": author.get("top_work", "N/A"),
                            "Number of Works": author.get("work_count", "N/A")
                        })
                    
                    df = pd.DataFrame(table_data)
                    
                    # Display the table with clickable Author IDs
                    selected_rows = st.data_editor(
                        df,
                        hide_index=True,
                        column_config={
                            "Author ID": st.column_config.LinkColumn(
                                "Author ID",
                                width="small",
                                help="Click to view details"
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
                    
                    # If a row is selected, navigate to author details
                    if selected_rows is not None and len(selected_rows) > 0:
                        selected_author_key = selected_rows.iloc[0]["Author ID"]
                        st.session_state.author_key = selected_author_key
                        st.session_state.page = 'author_details'
                        st.rerun()
                    
                    st.caption(f"Found {data['numFound']} author(s)")
                
                else:
                    st.warning("No authors found matching your search. Please try a different name.")
                
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while searching for authors: {str(e)}")
                st.info("Please check your internet connection and try again.")

# Main app routing
if st.session_state.page == 'search':
    show_search_page()
elif st.session_state.page == 'author_details' and st.session_state.author_key:
    show_author_details(st.session_state.author_key)
