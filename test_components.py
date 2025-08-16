#!/usr/bin/env python3
"""
Simple test script to verify all components are working
"""

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
    
    try:
        from utils.text_processing import TextProcessor
        print("✅ TextProcessor imported")
    except Exception as e:
        print(f"❌ TextProcessor import failed: {e}")
    
    try:
        from utils.audio_utils import AudioProcessor
        print("✅ AudioProcessor imported")
    except Exception as e:
        print(f"❌ AudioProcessor import failed: {e}")
    
    try:
        from pdf_to_audio import PDFToAudioConverter
        print("✅ PDFToAudioConverter imported")
    except Exception as e:
        print(f"❌ PDFToAudioConverter import failed: {e}")
    
    try:
        from persona_search import PersonaSearch
        print("✅ PersonaSearch imported")
    except Exception as e:
        print(f"❌ PersonaSearch import failed: {e}")
    
    try:
        from storybook_generator import StorybookGenerator
        print("✅ StorybookGenerator imported")
    except Exception as e:
        print(f"❌ StorybookGenerator import failed: {e}")

def test_text_processing():
    """Test text processing functionality"""
    print("\nTesting text processing...")
    
    try:
        from utils.text_processing import TextProcessor
        processor = TextProcessor()
        
        # Test text cleaning
        dirty_text = "This   is   a   test   text   with   extra   spaces."
        cleaned = processor.clean_text(dirty_text)
        print(f"✅ Text cleaning: '{dirty_text}' -> '{cleaned}'")
        
        # Test text segmentation
        test_text = "This is a test. It has multiple sentences. We will process it."
        segments = processor.segment_text_for_audio(test_text, 50)
        print(f"✅ Text segmentation: {len(segments)} segments created")
        
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")

def test_persona_search():
    """Test persona search functionality"""
    print("\nTesting persona search...")
    
    try:
        from persona_search import PersonaSearch
        search = PersonaSearch()
        
        print(f"✅ PersonaSearch initialized with {len(search.personas)} personas")
        
        # Test search
        results = search.search_personas("AI researcher", top_k=3)
        print(f"✅ Search test: Found {len(results)} results")
        
    except Exception as e:
        print(f"❌ Persona search test failed: {e}")

def test_storybook_generator():
    """Test storybook generator functionality"""
    print("\nTesting storybook generator...")
    
    try:
        from storybook_generator import StorybookGenerator
        generator = StorybookGenerator()
        
        test_story = "This is a test story. It has multiple sentences. We will create a storybook from it."
        pages = generator.generate_story_pages(test_story, 2)
        print(f"✅ Storybook generation: Created {len(pages)} pages")
        
    except Exception as e:
        print(f"❌ Storybook generator test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing AI-Powered Multi-Tool Application Components")
    print("=" * 60)
    
    test_imports()
    test_text_processing()
    test_persona_search()
    test_storybook_generator()
    
    print("\n" + "=" * 60)
    print("🎉 Component testing completed!")
    print("\nTo run the full application:")
    print("streamlit run main.py")

if __name__ == "__main__":
    main()
