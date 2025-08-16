import re
import PyPDF2
import pdfplumber
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


class TextProcessor:
    """Utility class for text processing and PDF parsing"""
    @staticmethod
    def download_nltk_resources():
        """
        Download required NLTK data if not already present.
        """
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

    def __init__(self):
        TextProcessor.download_nltk_resources()
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """
        Extract text from PDF file using multiple methods for better results
        """
        text = ""
        
        try:
            # Method 1: Using pdfplumber (better for complex layouts)
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If pdfplumber didn't extract much text, try PyPDF2
            if len(text.strip()) < 100:
                pdf_file.seek(0)  # Reset file pointer
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
        
        return text.strip()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and format text for better TTS output
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Add proper spacing after punctuation
        text = re.sub(r'([.,!?;:])\s*([A-Z])', r'\1 \2', text)
        
        # Remove special characters that might cause TTS issues
        text = re.sub(r'[^\w\s.,!?;:()\'"-]', '', text)
        
        return text.strip()
    
    @staticmethod
    def segment_text_for_audio(text: str, max_chunk_size: int = 500) -> List[str]:
        """
        Segment text into chunks suitable for audio processing
        """
        # Split into sentences first
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk + sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text for search and analysis
        """
        # Tokenize and remove stopwords
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        
        # Filter out stopwords and short words
        keywords = [word for word in words if word.isalnum() and 
                   word not in stop_words and len(word) > 2]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(keywords)
        
        # Return most common keywords
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    @staticmethod
    def format_text_for_storybook(text: str, font_size: int = 12, 
                                 max_chars_per_line: int = 80) -> str:
        """
        Format text for storybook layout with proper line breaks
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
    
    @staticmethod
    def split_story_into_pages(story_text: str, sentences_per_page: int = 3) -> List[str]:
        """
        Split a story into meaningful pages for storybook generation
        Creates paragraphs of 3-4 sentences that form complete thoughts
        """
        # Clean the text first
        cleaned_text = TextProcessor.clean_text(story_text)
        
        # Split into sentences
        sentences = sent_tokenize(cleaned_text)
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        pages = []
        current_page = []
        current_length = 0
        
        for sentence in sentences:
            # Add sentence to current page
            current_page.append(sentence)
            current_length += len(sentence)
            
            # Check if we should create a new page
            should_new_page = False
            
            # Create new page if:
            # 1. We have 3-4 sentences (preferred length)
            # 2. Current page is getting too long (>300 characters)
            # 3. We have at least 2 sentences and hit a natural break
            if len(current_page) >= 4:
                should_new_page = True
            elif current_length > 300 and len(current_page) >= 2:
                should_new_page = True
            elif len(current_page) >= 3 and current_length > 200:
                # Check if this is a good breaking point
                last_sentence = sentence.lower()
                if any(word in last_sentence for word in ['but', 'however', 'then', 'so', 'and', 'or', 'finally', 'suddenly']):
                    should_new_page = True
            
            if should_new_page:
                # Create page from current sentences
                page_text = " ".join(current_page)
                pages.append(page_text)
                
                # Reset for next page
                current_page = []
                current_length = 0
        
        # Add remaining sentences as the last page
        if current_page:
            page_text = " ".join(current_page)
            pages.append(page_text)
        
        return pages
