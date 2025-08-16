import streamlit as st
from pdf_to_audio import PDFToAudioConverter
from persona_search import PersonaSearch
from storybook_generator import StorybookGenerator

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Powered Multi-Tool Application",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application with navigation between features"""
    
    # Sidebar navigation
    st.sidebar.title("🚀 AI Tools")
    st.sidebar.markdown("---")
    
    # Navigation options
    page = st.sidebar.selectbox(
        "Choose a tool:",
        ["🏠 Home", "📚 PDF to Audiobook", "🔍 Persona Search", "📖 Storybook Generator"],
        help="Select which AI tool you want to use"
    )
    
    # Home page
    if page == "🏠 Home":
        st.markdown('<h1 class="main-header">AI-Powered Multi-Tool Application</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.2rem; color: #666;'>
                Transform your content with cutting-edge AI tools for audio, search, and storytelling
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title">📚 PDF to Audiobook</div>
                <div class="feature-description">
                    Convert PDF documents into high-quality audiobooks with natural-sounding voices. 
                    Choose from 4 voice options and export as MP3 files.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title">📖 Storybook Generator</div>
                <div class="feature-description">
                    Create beautiful storybooks with alternating text and AI-generated images. 
                    Customize formatting and export as professional PDFs.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title">🔍 Persona Search</div>
                <div class="feature-description">
                    Find compatible people using natural language queries with AI-powered matching. 
                    Get compatibility scores and actionable insights.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <div class="feature-title">🤖 AI-Powered</div>
                <div class="feature-description">
                    All tools leverage advanced AI technologies including natural language processing, 
                    vector databases, and machine learning for optimal results.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick start guide
        st.markdown("---")
        st.subheader("🚀 Quick Start Guide")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📚 PDF to Audiobook
            1. Upload your PDF file
            2. Choose your preferred voice
            3. Adjust processing settings
            4. Convert and download MP3
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 Persona Search
            1. Enter your search query
            2. Set preferences and exclusions
            3. Get matched personas
            4. Review insights and action points
            """)
        
        with col3:
            st.markdown("""
            ### 📖 Storybook Generator
            1. Input your story text
            2. Customize layout and style
            3. Generate images and PDF
            4. Download your storybook
            """)
        
        # Technical features
        st.markdown("---")
        st.subheader("🔧 Technical Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Text Processing:**
            - Advanced PDF parsing with multiple engines
            - Natural language processing and text cleaning
            - Intelligent sentence segmentation
            - Keyword extraction and analysis
            
            **Audio Processing:**
            - High-quality TTS with multiple voice options
            - Audio optimization and normalization
            - MP3 export with configurable quality
            - Chunk-based processing for large documents
            """)
        
        with col2:
            st.markdown("""
            **AI & Machine Learning:**
            - Vector database for semantic search
            - Sentence transformers for embeddings
            - Compatibility scoring algorithms
            - Natural language query processing
            
            **Document Generation:**
            - Professional PDF layout engine
            - Customizable typography and styling
            - Image generation and integration
            - Multi-format export capabilities
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem 0;'>
            <p>Built with ❤️ using Streamlit, Python, and cutting-edge AI technologies</p>
            <p>Transform your content creation workflow with these powerful AI tools</p>
        </div>
        """, unsafe_allow_html=True)
    
    # PDF to Audiobook page
    elif page == "📚 PDF to Audiobook":
        converter = PDFToAudioConverter()
        converter.render_interface()
    
    # Persona Search page
    elif page == "🔍 Persona Search":
        search = PersonaSearch()
        search.render_interface()
    
    # Storybook Generator page
    elif page == "📖 Storybook Generator":
        generator = StorybookGenerator()
        generator.render_interface()

if __name__ == "__main__":
    main()
