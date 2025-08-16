#!/usr/bin/env python3
"""
Setup script for AI-Powered Multi-Tool Application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["data", "outputs", "temp", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please edit .env file with your API keys")
    elif env_file.exists():
        print("✅ Environment file already exists")
    else:
        print("⚠️  No environment template found")

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded")
    except Exception as e:
        print(f"⚠️  NLTK data download failed: {e}")

def test_installation():
    """Test if the application can be imported"""
    print("🧪 Testing installation...")
    try:
        import streamlit
        import chromadb
        import sentence_transformers
        import PyPDF2
        import pdfplumber
        import gtts
        import pyttsx3
        import pydub
        import PIL
        import reportlab
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up AI-Powered Multi-Tool Application")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Download NLTK data
    download_nltk_data()
    
    # Test installation
    test_installation()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys (optional)")
    print("2. Run: streamlit run main.py")
    print("3. Open your browser to the provided URL")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
