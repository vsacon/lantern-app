import streamlit as st
import requests
import json

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
        Discover authors and their works using the Open Library database.
        Enter an author's name below to begin your search.
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
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            
            # Check if any authors were found
            if data["numFound"] > 0:
                st.success(f"Found {data['numFound']} author(s) matching your search!")
                
                # Display each author's information
                for author in data["docs"]:
                    with st.container():
                        st.markdown("""
                            <div class="author-card">
                        """, unsafe_allow_html=True)
                        
                        # Author name with larger font
                        st.markdown(f"### {author['name']}")
                        
                        # Create two columns for better organization
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if "birth_date" in author:
                                st.markdown(f"**Birth Date:** {author['birth_date']}")
                            if "top_work" in author:
                                st.markdown(f"**Most Popular Work:** {author['top_work']}")
                            if "work_count" in author:
                                st.markdown(f"**Number of Works:** {author['work_count']}")
                        
                        with col2:
                            if "alternate_names" in author and author["alternate_names"]:
                                st.markdown("**Also known as:**")
                                st.markdown("- " + "\n- ".join(author["alternate_names"]))
                            
                            if "top_subjects" in author and author["top_subjects"]:
                                st.markdown("**Top Subjects:**")
                                st.markdown("- " + "\n- ".join(author["top_subjects"][:5]))  # Limit to top 5 subjects
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            else:
                st.warning("No authors found matching your search. Please try a different name.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while searching for authors: {str(e)}")
            st.info("Please check your internet connection and try again.")

# Add footer
st.markdown("""
    <div style='margin-top: 3rem; text-align: center; color: #666;'>
        <p>Powered by Open Library API</p>
    </div>
""", unsafe_allow_html=True)
