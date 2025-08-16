#!/usr/bin/env python3
"""
Test suite for AI-Powered Multi-Tool Application
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

# Import our modules
from utils.text_processing import TextProcessor
from utils.audio_utils import AudioProcessor
from pdf_to_audio import PDFToAudioConverter
from persona_search import PersonaSearch
from storybook_generator import StorybookGenerator

class TestTextProcessing(unittest.TestCase):
    """Test text processing utilities"""
    
    def setUp(self):
        self.text_processor = TextProcessor()
        self.sample_text = "This is a test text. It has multiple sentences. We will process it."
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "This   is   dirty   text   with   extra   spaces."
        cleaned = self.text_processor.clean_text(dirty_text)
        self.assertNotIn("   ", cleaned)
        self.assertIn("This is dirty text", cleaned)
    
    def test_segment_text_for_audio(self):
        """Test text segmentation for audio"""
        segments = self.text_processor.segment_text_for_audio(self.sample_text, 50)
        self.assertIsInstance(segments, list)
        self.assertGreater(len(segments), 0)
        for segment in segments:
            self.assertLessEqual(len(segment), 50)
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        keywords = self.text_processor.extract_keywords(self.sample_text, 5)
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 5)
    
    def test_format_text_for_storybook(self):
        """Test storybook text formatting"""
        formatted = self.text_processor.format_text_for_storybook(self.sample_text, 12, 40)
        self.assertIsInstance(formatted, str)
        self.assertIn("\n", formatted)
    
    def test_split_story_into_pages(self):
        """Test story page splitting"""
        pages = self.text_processor.split_story_into_pages(self.sample_text, 2)
        self.assertIsInstance(pages, list)
        self.assertGreater(len(pages), 0)

class TestAudioProcessing(unittest.TestCase):
    """Test audio processing utilities"""
    
    def setUp(self):
        self.audio_processor = AudioProcessor()
        self.test_text = "Hello, this is a test."
    
    def test_voice_options(self):
        """Test voice options configuration"""
        self.assertIn("British Male", self.audio_processor.VOICE_OPTIONS)
        self.assertIn("American Female", self.audio_processor.VOICE_OPTIONS)
        self.assertEqual(len(self.audio_processor.VOICE_OPTIONS), 4)
    
    def test_voice_configuration(self):
        """Test voice configuration structure"""
        for voice_name, config in self.audio_processor.VOICE_OPTIONS.items():
            self.assertIn("lang", config)
            self.assertIn("voice", config)
            self.assertIsInstance(config["lang"], str)
            self.assertIsInstance(config["voice"], str)

class TestPDFToAudioConverter(unittest.TestCase):
    """Test PDF to audio converter"""
    
    def setUp(self):
        self.converter = PDFToAudioConverter()
    
    def test_converter_initialization(self):
        """Test converter initialization"""
        self.assertIsInstance(self.converter.voice_options, list)
        self.assertEqual(len(self.converter.voice_options), 4)
        self.assertIn("British Male", self.converter.voice_options)
    
    def test_text_processor_integration(self):
        """Test integration with text processor"""
        self.assertIsNotNone(self.converter.text_processor)
        self.assertIsNotNone(self.converter.audio_processor)

class TestPersonaSearch(unittest.TestCase):
    """Test persona search functionality"""
    
    def setUp(self):
        self.search = PersonaSearch()
    
    def test_persona_loading(self):
        """Test persona data loading"""
        self.assertIsInstance(self.search.personas, list)
        self.assertGreater(len(self.search.personas), 0)
    
    def test_persona_structure(self):
        """Test persona data structure"""
        if self.search.personas:
            persona = self.search.personas[0]
            required_fields = ['id', 'name', 'age', 'location', 'occupation', 
                             'interests', 'values', 'personality', 'hobbies']
            for field in required_fields:
                self.assertIn(field, persona)
    
    def test_text_representation_creation(self):
        """Test persona text representation creation"""
        if self.search.personas:
            persona = self.search.personas[0]
            text_repr = self.search.create_persona_text_representation(persona)
            self.assertIsInstance(text_repr, str)
            self.assertIn(persona['name'], text_repr)
            self.assertIn(persona['occupation'], text_repr)

class TestStorybookGenerator(unittest.TestCase):
    """Test storybook generator"""
    
    def setUp(self):
        self.generator = StorybookGenerator()
        self.sample_story = "This is a test story. It has multiple sentences. We will create a storybook from it."
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        self.assertIsNotNone(self.generator.text_processor)
        self.assertIsInstance(self.generator.page_width, float)
        self.assertIsInstance(self.generator.page_height, float)
    
    def test_story_page_generation(self):
        """Test story page generation"""
        pages = self.generator.generate_story_pages(self.sample_story, 2)
        self.assertIsInstance(pages, list)
        self.assertGreater(len(pages), 0)
    
    def test_placeholder_image_generation(self):
        """Test placeholder image generation"""
        image_path = self.generator.generate_placeholder_image("Test page", 1, "storybook")
        if image_path:
            self.assertTrue(os.path.exists(image_path))
            # Clean up
            try:
                os.remove(image_path)
            except:
                pass

class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def setUp(self):
        self.text_processor = TextProcessor()
        self.audio_processor = AudioProcessor()
        self.pdf_converter = PDFToAudioConverter()
        self.persona_search = PersonaSearch()
        self.storybook_generator = StorybookGenerator()
    
    def test_text_processing_consistency(self):
        """Test that text processing is consistent across components"""
        test_text = "This is a test text for consistency checking."
        
        # Test across different components
        cleaned1 = self.text_processor.clean_text(test_text)
        cleaned2 = self.pdf_converter.text_processor.clean_text(test_text)
        cleaned3 = self.storybook_generator.text_processor.clean_text(test_text)
        
        self.assertEqual(cleaned1, cleaned2)
        self.assertEqual(cleaned2, cleaned3)
    
    def test_voice_options_consistency(self):
        """Test that voice options are consistent"""
        voices1 = list(self.audio_processor.VOICE_OPTIONS.keys())
        voices2 = self.pdf_converter.voice_options
        
        self.assertEqual(set(voices1), set(voices2))
    
    def test_persona_data_consistency(self):
        """Test that persona data is consistent"""
        self.assertEqual(len(self.persona_search.personas), len(self.persona_search.personas))
        
        if self.persona_search.personas:
            # Check that all personas have required fields
            required_fields = ['id', 'name', 'age', 'location', 'occupation']
            for persona in self.persona_search.personas:
                for field in required_fields:
                    self.assertIn(field, persona)

class TestFileOperations(unittest.TestCase):
    """Test file operations and data handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sample_personas_file(self):
        """Test that sample personas file exists and is valid JSON"""
        personas_file = Path("data/sample_personas.json")
        self.assertTrue(personas_file.exists())
        
        with open(personas_file, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_requirements_file(self):
        """Test that requirements file exists"""
        requirements_file = Path("requirements.txt")
        self.assertTrue(requirements_file.exists())
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        self.assertIn("streamlit", content)
        self.assertIn("chromadb", content)
        self.assertIn("sentence-transformers", content)

def run_tests():
    """Run all tests"""
    print("🧪 Running AI-Powered Multi-Tool Application Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTextProcessing,
        TestAudioProcessing,
        TestPDFToAudioConverter,
        TestPersonaSearch,
        TestStorybookGenerator,
        TestIntegration,
        TestFileOperations
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
