import streamlit as st
import requests
import time
from urllib.parse import urlparse

# Configure the page
st.set_page_config(
    page_title="YouTube to Blog Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    .main {
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def validate_youtube_url(url):
    """Validate if the URL is a proper YouTube URL."""
    try:
        parsed_url = urlparse(url)
        return any(domain in parsed_url.netloc for domain in ['youtube.com', 'youtu.be', 'www.youtube.com', 'www.youtu.be'])
    except:
        return False

# Title and description
st.title("🎥 YouTube Video to Blog Generator")
st.markdown("""
    Transform your favorite YouTube videos into well-structured blog posts! 
    Simply paste a YouTube URL below and let our AI do the magic.
""")

# Input section
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a valid YouTube video URL here"
        )
    with col2:
        generate_button = st.button("Generate Blog Post", type="primary")

# Main processing section
if generate_button:
    if not youtube_url:
        st.warning("⚠️ Please enter a YouTube video URL")
    elif not validate_youtube_url(youtube_url):
        st.error("❌ Invalid YouTube URL format. Please enter a valid YouTube video URL")
    else:
        try:
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("🔄 Connecting to server...")
            progress_bar.progress(10)
            
            # Send request to backend
            response = requests.post(
                "http://localhost:5000/generate_blog",
                json={"url": youtube_url, "language": "en"},
                timeout=300  # 5-minute timeout
            )
            
            progress_bar.progress(30)
            status_text.text("🎥 Processing video content...")
            
            if response.status_code == 200:
                data = response.json()
                blog_content = data.get("blog_content", "")
                used_language = data.get("used_language", "en")
                
                progress_bar.progress(100)
                status_text.text("✅ Blog post generated successfully!")
                
                # Display the blog content
                st.markdown("---")
                st.subheader("📝 Generated Blog Post")
                st.markdown(blog_content)
                
                # Add download button
                st.download_button(
                    label="📥 Download Blog Post",
                    data=blog_content,
                    file_name="generated_blog.md",
                    mime="text/markdown"
                )
                
            else:
                error_message = response.json().get("error", "Unknown error occurred")
                st.error(f"❌ Error: {error_message}")
                progress_bar.empty()
                status_text.empty()
                
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. The video might be too long or the server is busy.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Could not connect to the server. Please make sure the server is running.")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
        finally:
            # Clean up progress indicators if they exist
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()

# Add footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ using Streamlit and Agno Framework</p>
    </div>
""", unsafe_allow_html=True)
