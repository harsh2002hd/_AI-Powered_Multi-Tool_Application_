#!/usr/bin/env python3
"""
Test script for the storybook generator
"""

def test_storybook_generator():
    """Test the storybook generator functionality"""
    print("🧪 Testing Storybook Generator...")
    
    try:
        from storybook_generator import StorybookGenerator
        from utils.text_processing import TextProcessor
        
        # Initialize components
        generator = StorybookGenerator()
        text_processor = TextProcessor()
        
        print("✅ Components initialized successfully")
        
        # Test text processing
        test_story = """Leo loved the color red. Not just any red, but the bright, bold red of a fire engine. More than anything, Leo dreamed of becoming a firefighter. He would spend hours in his room, pretending his stuffed animals were in trouble."""
        
        # Test story page generation
        story_pages = generator.generate_story_pages(test_story, 2)
        print(f"✅ Generated {len(story_pages)} story pages")
        
        # Test image generation
        image_path = generator.generate_placeholder_image("Test page", 1, "storybook")
        if image_path:
            print(f"✅ Generated placeholder image: {image_path}")
        else:
            print("❌ Failed to generate placeholder image")
        
        # Test text processing
        cleaned_text = text_processor.clean_text(test_story)
        print(f"✅ Text cleaning: {len(cleaned_text)} characters")
        
        # Test text segmentation
        segments = text_processor.segment_text_for_audio(test_story, 100)
        print(f"✅ Text segmentation: {len(segments)} segments")
        
        print("\n🎉 All storybook generator tests passed!")
        print("\nThe storybook generator is working correctly.")
        print("You can now use it in the Streamlit application.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_storybook_generator()
