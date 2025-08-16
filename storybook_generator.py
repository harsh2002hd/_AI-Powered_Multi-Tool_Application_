import streamlit as st
import os
import tempfile
import base64
import requests
import json
from typing import List, Dict, Any, Optional
import time
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from utils.text_processing import TextProcessor
from nltk.tokenize import sent_tokenize

class StorybookGenerator:
    """AI Storybook Generator with alternating text and image pages"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.page_width, self.page_height = A4
        self.margin = 0.5 * inch
    
    def image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string for display"""
        try:
            with open(image_path, "rb") as img_file:
                img_data = img_file.read()
                return base64.b64encode(img_data).decode()
        except Exception as e:
            st.error(f"Error converting image to base64: {e}")
            return ""
    
    def _get_image_html(self, image_path: str, page_num: int, fullscreen: bool = False) -> str:
        """Generate HTML for image display"""
        if not image_path or not os.path.exists(image_path):
            return f'<div style="text-align: center; color: #666; padding: 40px;">No image available for page {page_num}</div>'
        
        try:
            img_base64 = self.image_to_base64(image_path)
            if img_base64:
                if fullscreen:
                    return f"""
                    <img src="data:image/png;base64,{img_base64}" 
                         style="width: 100%; max-width: 500px; height: auto; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);" />
                    """
                else:
                    return f"""
                    <img src="data:image/png;base64,{img_base64}" 
                         style="width: 100%; max-width: 400px; height: auto; border: 2px solid #ddd; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
                    """
            else:
                return f'<div style="text-align: center; color: #666;">Error loading image for page {page_num}</div>'
        except Exception as e:
            return f'<div style="text-align: center; color: #666;">Error displaying image: {e}</div>'
    
    def generate_ai_image(self, page_text: str, page_number: int, image_style: str = "storybook") -> str:
        """Generate AI image using Pollinations AI based on story text"""
        try:
            # Create a prompt based on the story text and style
            prompt = self.create_image_prompt(page_text, image_style)
            
            # Clean prompt for URL (remove special characters and spaces)
            clean_prompt = prompt.replace(' ', '+').replace('"', '').replace("'", '').replace(',', '')
            clean_prompt = ''.join(c for c in clean_prompt if c.isalnum() or c in '+-')
            
            # Call Pollinations AI API with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}"
                    
                    # Download the image with timeout
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Save to temporary file
                        image_path = tempfile.mktemp(suffix=f"_ai_page_{page_number}.png")
                        with open(image_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Verify the image is valid
                        try:
                            img = Image.open(image_path)
                            img.verify()  # Verify it's a valid image
                            img.close()
                            
                            # Reopen and resize
                            img = Image.open(image_path)
                            img = img.resize((800, 600), Image.Resampling.LANCZOS)
                            img.save(image_path)
                            
                            return image_path
                        except Exception as img_error:
                            # If image is corrupted, try again
                            if os.path.exists(image_path):
                                os.remove(image_path)
                            if attempt < max_retries - 1:
                                time.sleep(1)  # Wait before retry
                                continue
                            else:
                                raise img_error
                    else:
                        # If failed, wait and retry
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Wait before retry
                            continue
                        else:
                            st.error(f"Failed to generate AI image: HTTP {img_response.status_code}")
                            return None
                            
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        st.error("AI image generation timed out")
                        return None
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        st.error(f"AI image generation error: {str(e)[:50]}...")
                        return None
            
            return None
                
        except Exception as e:
            st.error(f"Error generating AI image: {e}")
            return None
    
    def create_image_prompt(self, page_text: str, image_style: str) -> str:
        """Create a prompt for Pollinations AI image generation based on story text"""
        # Clean and extract key elements from the text
        text = page_text.strip()
        if len(text) > 200:  # Shorter for URL compatibility
            text = text[:200]
        
        # Extract key words and themes
        words = text.lower().split()
        key_words = [word for word in words if len(word) > 3 and word not in ['the', 'and', 'was', 'had', 'her', 'his', 'they', 'with', 'from', 'that', 'this', 'were', 'been', 'have', 'said', 'will', 'could', 'would']]
        
        # Style-specific modifiers
        style_modifiers = {
            "storybook": "children's book illustration, warm colors, friendly, detailed",
            "modern": "modern digital art, clean lines, contemporary, vibrant",
            "fantasy": "fantasy art, magical, vibrant colors, whimsical"
        }
        
        style_desc = style_modifiers.get(image_style, "beautiful illustration")
        
        # Create a concise prompt for Pollinations AI
        if key_words:
            # Use key words from the text
            key_theme = ' '.join(key_words[:5])  # Use first 5 key words
            prompt = f"{key_theme} {style_desc}"
        else:
            # Fallback to general storybook style
            prompt = f"storybook illustration {style_desc}"
        
        return prompt
        
    def generate_story_pages(self, story_text: str, sentences_per_page: int = 3) -> List[str]:
        """Split story into pages for storybook layout"""
        return self.text_processor.split_story_into_pages(story_text, sentences_per_page)
    
    def generate_placeholder_image(self, page_text: str, page_number: int, 
                                 image_style: str = "storybook") -> str:
        """
        Generate an improved placeholder image based on story text
        This creates text-aware placeholders when AI generation is not available
        """
        try:
            # Create a placeholder image
            width, height = 800, 600
            
            # Create image with background
            if image_style == "storybook":
                bg_color = (255, 248, 220)  # Cream color
                text_color = (70, 130, 180)  # Steel blue
            elif image_style == "modern":
                bg_color = (240, 248, 255)  # Alice blue
                text_color = (25, 25, 112)  # Midnight blue
            else:  # fantasy
                bg_color = (255, 228, 225)  # Misty rose
                text_color = (139, 69, 19)  # Saddle brown
            
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Add decorative border
            border_color = tuple(c - 50 for c in bg_color)
            draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
            
            # Add page number
            draw.text((width-100, 30), f"Page {page_number}", 
                     fill=text_color, font=font)
            
            # Extract key words from text for better placeholders
            words = page_text.lower().split()[:5]  # First 5 words
            key_words = [word for word in words if len(word) > 3]
            
            # Add story title with key words
            title_font = ImageFont.truetype("arial.ttf", 32) if os.path.exists("arial.ttf") else font
            title_text = f"Story: {', '.join(key_words[:3])}" if key_words else "Story Illustration"
            draw.text((width//2-200, 80), title_text, 
                     fill=text_color, font=title_font)
            
            # Add some decorative elements based on text content
            if any(word in page_text.lower() for word in ['star', 'moon', 'night', 'sky']):
                # Space/night theme
                draw.ellipse([100, 200, 200, 300], fill=(255, 255, 0), outline=text_color)  # Moon
                for i in range(5):
                    x = 300 + i * 80
                    y = 200 + (i % 2) * 40
                    draw.ellipse([x, y, x+10, y+10], fill=(255, 255, 255), outline=text_color)  # Stars
            elif any(word in page_text.lower() for word in ['tree', 'forest', 'nature', 'green']):
                # Nature theme
                draw.rectangle([100, 300, 200, 500], fill=(139, 69, 19), outline=text_color)  # Tree trunk
                draw.ellipse([50, 200, 250, 350], fill=(34, 139, 34), outline=text_color)  # Tree top
            elif any(word in page_text.lower() for word in ['house', 'home', 'building']):
                # House theme
                draw.rectangle([200, 300, 400, 450], fill=(160, 82, 45), outline=text_color)  # House
                draw.polygon([(150, 300), (300, 200), (450, 300)], fill=(139, 69, 19), outline=text_color)  # Roof
                draw.rectangle([250, 350, 300, 400], fill=(135, 206, 235), outline=text_color)  # Window
            elif any(word in page_text.lower() for word in ['water', 'ocean', 'sea', 'river']):
                # Water theme
                draw.rectangle([50, 400, width-50, 500], fill=(135, 206, 235), outline=text_color)  # Water
                draw.ellipse([200, 200, 300, 300], fill=(255, 255, 255), outline=text_color)  # Cloud
            else:
                # Default decorative elements based on style
                if image_style == "storybook":
                    draw.ellipse([100, 200, 300, 400], fill=(255, 182, 193), outline=text_color)
                    draw.rectangle([400, 250, 600, 350], fill=(173, 216, 230), outline=text_color)
                elif image_style == "modern":
                    draw.polygon([(200, 200), (300, 150), (400, 200), (300, 250)], 
                               fill=(255, 160, 122), outline=text_color)
                    draw.rectangle([450, 200, 550, 300], fill=(176, 196, 222), outline=text_color)
                else:  # fantasy
                    draw.ellipse([150, 150, 250, 250], fill=(255, 215, 0), outline=text_color)
                    draw.polygon([(400, 200), (500, 150), (600, 200), (500, 300)], 
                               fill=(138, 43, 226), outline=text_color)
            
            # Add text hint
            small_font = ImageFont.truetype("arial.ttf", 16) if os.path.exists("arial.ttf") else font
            draw.text((50, height-100), "Text-aware placeholder illustration", 
                     fill=text_color, font=small_font)
            
            # Save image
            image_path = tempfile.mktemp(suffix=f"_page_{page_number}.png")
            img.save(image_path)
            
            return image_path
            
        except Exception as e:
            st.error(f"Error generating image: {e}")
            return None
    
    def _create_basic_fallback_image(self, page_number: int, image_style: str = "storybook") -> str:
        """Create a basic fallback image when all other methods fail"""
        try:
            # Create a simple image
            width, height = 800, 600
            
            # Choose colors based on style
            if image_style == "storybook":
                bg_color = (255, 248, 220)  # Cream
                text_color = (70, 130, 180)  # Steel blue
            elif image_style == "modern":
                bg_color = (240, 248, 255)  # Alice blue
                text_color = (25, 25, 112)  # Midnight blue
            else:  # fantasy
                bg_color = (255, 228, 225)  # Misty rose
                text_color = (139, 69, 19)  # Saddle brown
            
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Add border
            border_color = tuple(c - 50 for c in bg_color)
            draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
            
            # Add page number
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            draw.text((width//2-50, height//2-50), f"Page {page_number}", 
                     fill=text_color, font=font)
            
            # Add simple decorative element
            if image_style == "storybook":
                draw.ellipse([width//2-100, height//2+50, width//2+100, height//2+150], 
                           fill=(255, 182, 193), outline=text_color)
            elif image_style == "modern":
                draw.rectangle([width//2-100, height//2+50, width//2+100, height//2+150], 
                             fill=(176, 196, 222), outline=text_color)
            else:  # fantasy
                draw.polygon([(width//2-100, height//2+50), (width//2, height//2+150), (width//2+100, height//2+50)], 
                           fill=(255, 215, 0), outline=text_color)
            
            # Save image
            image_path = tempfile.mktemp(suffix=f"_fallback_page_{page_number}.png")
            img.save(image_path)
            
            return image_path
            
        except Exception as e:
            st.error(f"Error creating fallback image: {e}")
            return None
    
    def create_storybook_pdf(self, story_pages: List[str], image_paths: List[str], 
                           title: str, font_size: int = 12, font_family: str = "Helvetica",
                           export_path: str = None) -> str:
        """
        Create a PDF storybook with alternating text and image pages
        """
        try:
            if not export_path:
                export_path = tempfile.mktemp(suffix="_storybook.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(export_path, pagesize=A4,
                                  rightMargin=self.margin, leftMargin=self.margin,
                                  topMargin=self.margin, bottomMargin=self.margin)
            
            # Define styles
            styles = getSampleStyleSheet()
            
            # Custom title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=font_family,
                textColor=colors.darkblue
            )
            
            # Custom text style
            text_style = ParagraphStyle(
                'CustomText',
                parent=styles['Normal'],
                fontSize=font_size,
                spaceAfter=12,
                alignment=TA_LEFT,
                fontName=font_family,
                textColor=colors.black,
                leading=font_size * 1.2
            )
            
            # Build story content
            story_content = []
            
            # Add title page
            story_content.append(Paragraph(title, title_style))
            story_content.append(Spacer(1, 2*inch))
            
            # Add alternating text and image pages
            for i, (page_text, image_path) in enumerate(zip(story_pages, image_paths)):
                if image_path and os.path.exists(image_path):
                    # Add image page
                    img = RLImage(image_path, width=6*inch, height=4.5*inch)
                    img.hAlign = 'CENTER'
                    story_content.append(img)
                    story_content.append(Spacer(1, 0.5*inch))
                
                # Add text page
                formatted_text = self.text_processor.format_text_for_storybook(
                    page_text, font_size, 80
                )
                story_content.append(Paragraph(formatted_text, text_style))
                story_content.append(Spacer(1, 0.5*inch))
            
            # Build PDF
            doc.build(story_content)
            
            return export_path
            
        except Exception as e:
            st.error(f"Error creating PDF: {e}")
            return None
    
    def render_interface(self):
        """Render the Streamlit interface for storybook generation"""
        st.header("📖 AI Storybook Generator")
        st.markdown("Create beautiful storybooks with alternating text and AI-generated images.")
        
        # Sidebar for AI image generation info
        with st.sidebar:
            st.subheader("🤖 AI Image Generation")
            st.info("""
            **Pollinations AI** is used for free AI image generation.
            
            No API key required!
            
            Images are generated based on your story content and chosen style.
            """)
        
        # Clean up old files if needed
        if 'cleanup_files' in st.session_state:
            cleanup_data = st.session_state['cleanup_files']
            if time.time() > cleanup_data['cleanup_time']:
                try:
                    if os.path.exists(cleanup_data['pdf_path']):
                        os.remove(cleanup_data['pdf_path'])
                    for img_path in cleanup_data['image_paths']:
                        if img_path and os.path.exists(img_path):
                            os.remove(img_path)
                    del st.session_state['cleanup_files']
                except:
                    pass
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "PDF Upload"],
            help="Select how you want to provide your story content"
        )
        
        story_text = ""
        
        if input_method == "Text Input":
            # Text input
            st.subheader("📝 Story Content")
            story_text = st.text_area(
                "Enter your story:",
                placeholder="Once upon a time...",
                height=300,
                help="Enter the story text that will be converted into a storybook"
            )
            
            # Show example story option if no text entered
            if not story_text:
                with st.expander("📚 Click here to use the example story"):
                    example_story = """Leo's Big Red Dream

Leo loved the color red. Not just any red, but the bright, bold red of a fire engine. More than anything, Leo dreamed of becoming a firefighter.

He would spend hours in his room, pretending his stuffed animals were in trouble. "Don't worry, brave citizens!" he'd shout, "Firefighter Leo is here to help!"

His favorite book was "Fire Safety for Kids," and he knew all about "Stop, Drop, and Roll." He even helped his mom check the smoke detectors every month.

One sunny afternoon, a real fire engine drove past his house, lights flashing and siren wailing. Leo waved with all his might, his heart thumping with excitement.

"Mom, can we visit the fire station?" he asked, his eyes wide with hope. His mom smiled. "Maybe we can arrange that, Leo."

A few weeks later, a special day arrived! Leo and his mom were at the fire station. The fire engines were even bigger and redder up close!

A kind firefighter, named Captain Eva, showed them around. She let Leo sit in the driver's seat of the big truck! It felt like sitting on top of the world.

Captain Eva explained how all the hoses and tools worked. "Every tool has a job," she said, "just like every firefighter has an important role."

Before they left, Captain Eva handed Leo a shiny red plastic fire hat. "Keep dreaming big, Leo," she said with a wink.

That night, Leo tucked his new hat beside his bed. He knew becoming a firefighter would take hard work and learning, but he was ready. His dream felt closer than ever."""
                    
                    if st.button("Use Example Story"):
                        story_text = example_story
                        st.success("Example story loaded! You can now customize settings and generate the storybook.")
        
        else:
            # PDF upload
            st.subheader("📄 PDF Upload")
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload a PDF file containing your story"
            )
            
            if uploaded_file is not None:
                # Extract text from PDF
                with st.spinner("Extracting text from PDF..."):
                    story_text = self.text_processor.extract_text_from_pdf(uploaded_file)
                    
                    if story_text:
                        st.success(f"Extracted {len(story_text)} characters from PDF")
                        st.text_area("Extracted text:", story_text, height=200, disabled=True)
                        
                        # Auto-generate storybook from PDF
                        st.info("🔄 Automatically generating storybook from PDF...")
                        
                        # Use default settings for PDF generation
                        title = uploaded_file.name.replace('.pdf', '').replace('_', ' ').title()
                        sentences_per_page = 3
                        image_style = "storybook"
                        font_size = 12
                        font_family = "Helvetica"
                        num_pages = 0  # Use full story
                        
                        # Split story into pages
                        story_pages = self.generate_story_pages(story_text, sentences_per_page)
                        
                        if not story_pages:
                            st.error("❌ Failed to process PDF text. Please check your PDF.")
                            return
                        
                        # Show story analysis
                        st.success(f"📖 PDF processed successfully!")
                        st.info(f"📄 Total pages: {len(story_pages)}")
                        st.info(f"📝 Average sentences per page: {sentences_per_page}")
                        
                        # Generate images for each page
                        image_paths = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Use AI generation for PDF
                        use_ai = True
                        
                        for i, page_text in enumerate(story_pages):
                            status_text.text(f"Generating image for page {i+1}/{len(story_pages)}...")
                            
                            # Try AI generation first if enabled
                            image_path = None
                            if use_ai:
                                try:
                                    image_path = self.generate_ai_image(page_text, i+1, image_style)
                                    if image_path and os.path.exists(image_path):
                                        st.success(f"🤖 AI-generated image for page {i+1}")
                                    else:
                                        st.warning(f"⚠️ AI generation failed for page {i+1}, using placeholder")
                                        image_path = None
                                except Exception as e:
                                    st.warning(f"⚠️ AI generation error for page {i+1}: {str(e)[:50]}... using placeholder")
                                    image_path = None
                            
                            # Fall back to improved placeholder if AI fails or is disabled
                            if not image_path or not os.path.exists(image_path):
                                try:
                                    image_path = self.generate_placeholder_image(page_text, i+1, image_style)
                                    if image_path and os.path.exists(image_path):
                                        st.success(f"✅ Generated placeholder for page {i+1}")
                                    else:
                                        st.error(f"❌ Failed to generate placeholder for page {i+1}")
                                        # Create a basic fallback image
                                        image_path = self._create_basic_fallback_image(i+1, image_style)
                                        if image_path:
                                            st.info(f"🔄 Using basic fallback for page {i+1}")
                                except Exception as e:
                                    st.error(f"❌ Error generating placeholder for page {i+1}: {str(e)[:50]}...")
                                    # Create a basic fallback image
                                    image_path = self._create_basic_fallback_image(i+1, image_style)
                                    if image_path:
                                        st.info(f"🔄 Using basic fallback for page {i+1}")
                            
                            # Ensure we have an image path
                            if image_path and os.path.exists(image_path):
                                image_paths.append(image_path)
                            else:
                                st.error(f"❌ No image available for page {i+1}")
                                image_paths.append(None)
                            
                            progress_bar.progress((i + 1) / len(story_pages))
                            time.sleep(0.1)
                        
                        # Create PDF
                        status_text.text("Creating PDF storybook...")
                        pdf_path = self.create_storybook_pdf(
                            story_pages, image_paths, title, font_size, font_family
                        )
                        
                        if pdf_path and os.path.exists(pdf_path):
                            st.success("🎉 Storybook generated successfully from PDF!")
                            
                            # Store storybook data in session state for navigation
                            st.session_state.storybook_data = {
                                'story_pages': story_pages,
                                'image_paths': image_paths,
                                'title': title,
                                'pdf_path': pdf_path
                            }
                            
                            # Reset current page
                            st.session_state.current_preview_page = 1
                            
                            # Show success message and instructions
                            st.balloons()
                            st.success("🎉 Your storybook is ready!")
                            
                            # Add a button to scroll to the preview
                            st.markdown("---")
                            st.markdown("### 📖 **Your Storybook is Ready!**")
                            st.info("🎯 Scroll down below to see your interactive storybook preview with images and text!")
                            
                            # Show a quick summary
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📄 Total Pages", len(story_pages))
                            with col2:
                                st.metric("🎨 Images Generated", len([p for p in image_paths if p]))
                            with col3:
                                st.metric("📚 Title", title)
                        else:
                            st.error("❌ Failed to generate storybook from PDF. Please try again.")
                    else:
                        st.error("No text could be extracted from the PDF.")
        
        # Only show settings and generate button if we have story text
        if story_text and story_text.strip():
            # Check if we have existing storybook data for navigation
            if 'storybook_data' in st.session_state:
                st.success("📖 Storybook data loaded from previous generation")
                
                # Add a clear header for the generated storybook
                st.markdown("---")
                st.markdown("## 🎉 **Your Generated Storybook**")
                st.info("📖 Scroll down to explore your storybook with images and text!")
                
                # Display interactive preview with existing data
                storybook_data = st.session_state.storybook_data
                story_pages = storybook_data['story_pages']
                image_paths = storybook_data['image_paths']
                title = storybook_data['title']
                pdf_path = storybook_data['pdf_path']
                
                st.subheader("📖 Interactive Storybook Preview")
                
                # Page navigation
                total_pages = len(story_pages)
                
                # Initialize current page in session state
                if 'current_preview_page' not in st.session_state:
                    st.session_state.current_preview_page = 1
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("◀️ Previous", disabled=st.session_state.current_preview_page <= 1):
                        st.session_state.current_preview_page = max(1, st.session_state.current_preview_page - 1)
                
                with col2:
                    page_slider = st.slider("📄 Page", 1, total_pages, st.session_state.current_preview_page, 
                                          help=f"Navigate through {total_pages} pages")
                    st.session_state.current_preview_page = page_slider
                
                with col3:
                    if st.button("Next ▶️", disabled=st.session_state.current_preview_page >= total_pages):
                        st.session_state.current_preview_page = min(total_pages, st.session_state.current_preview_page + 1)
                
                # PDF Download button in navigation area
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_file.read(),
                            file_name=f"{title.replace(' ', '_')}_storybook.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                # Get current page content
                current_page_num = st.session_state.current_preview_page
                current_text = story_pages[current_page_num - 1] if current_page_num <= len(story_pages) else ""
                current_image_path = image_paths[current_page_num - 1] if current_page_num <= len(image_paths) else None
                
                # Display current page (normal layout only)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🎨 Page {current_page_num} Image:**")
                    st.markdown(self._get_image_html(current_image_path, current_page_num), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**📝 Page {current_page_num} Text:**")
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff; min-height: 200px;">
                        <p style="font-size: 16px; line-height: 1.6; color: #333; margin: 0;">
                            {current_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Page info
                st.info(f"📊 Showing page {current_page_num} of {total_pages} | {len(sent_tokenize(current_text))} sentences | {len(current_text)} characters")
                
                # Option to generate new storybook
                if st.button("🔄 Generate New Storybook"):
                    # Clear existing data
                    if 'storybook_data' in st.session_state:
                        del st.session_state.storybook_data
                    if 'current_preview_page' in st.session_state:
                        del st.session_state.current_preview_page
                    st.rerun()
                
                # Clean up files after a delay to allow preview
                st.session_state['cleanup_files'] = {
                    'pdf_path': pdf_path,
                    'image_paths': image_paths,
                    'cleanup_time': time.time() + 30  # Clean up after 30 seconds
                }
                
                st.markdown("---")
            
            # Storybook settings
            st.subheader("⚙️ Storybook Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Title
                title = st.text_input(
                    "Storybook Title:",
                    value="Leo's Big Red Dream",
                    help="Enter the title for your storybook"
                )
                
                # Sentences per page
                sentences_per_page = st.slider(
                    "Sentences per page:",
                    min_value=2,
                    max_value=5,
                    value=3,
                    help="3-4 sentences per page creates meaningful paragraphs"
                )
                
                # Image style
                image_style = st.selectbox(
                    "Image Style:",
                    ["storybook", "modern", "fantasy"],
                    help="Choose the visual style for generated images"
                )
            
            with col2:
                # Font size
                font_size = st.slider(
                    "Font Size:",
                    min_value=8,
                    max_value=20,
                    value=12,
                    help="Text size for the storybook"
                )
                
                # Font family
                font_family = st.selectbox(
                    "Font Family:",
                    ["Helvetica", "Times", "Courier", "Arial"],
                    help="Choose the font style for your storybook"
                )
                
                # Number of pages
                num_pages = st.number_input(
                    "Max pages (0 = full story):",
                    min_value=0,
                    max_value=50,
                    value=0,
                    help="0 = use complete story, other values limit pages"
                )
            
            # Generate storybook button
            if st.button("📚 Generate Storybook", type="primary"):
                if story_text.strip():
                    with st.spinner("Generating your storybook..."):
                        # Split story into pages
                        story_pages = self.generate_story_pages(story_text, sentences_per_page)
                        
                        if not story_pages:
                            st.error("❌ Failed to process story text. Please check your input.")
                            return
                        
                        # Show story analysis
                        st.success(f"📖 Story processed successfully!")
                        st.info(f"📄 Total pages: {len(story_pages)}")
                        st.info(f"📝 Average sentences per page: {sentences_per_page}")
                        
                        # Show preview of first few pages
                        with st.expander("👀 Preview first few pages"):
                            for i, page in enumerate(story_pages[:3]):
                                st.write(f"**Page {i+1}:** {page}")
                                st.write(f"*({len(sent_tokenize(page))} sentences, {len(page)} characters)*")
                                st.write("---")
                            if len(story_pages) > 3:
                                st.write(f"... and {len(story_pages) - 3} more pages")
                        
                        # Limit pages if user specified a maximum
                        if num_pages > 0:
                            max_text_pages = num_pages // 2  # Half for text pages
                            if len(story_pages) > max_text_pages:
                                st.warning(f"⚠️ Story has {len(story_pages)} pages, limiting to {max_text_pages} pages")
                                story_pages = story_pages[:max_text_pages]
                        
                        # Generate images for each page
                        image_paths = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # AI generation is always available with Pollinations AI
                        use_ai = st.checkbox("🤖 Use AI Image Generation (Pollinations AI)", 
                                           value=True,
                                           help="Generate AI images based on story content using free Pollinations AI service.")
                        
                        for i, page_text in enumerate(story_pages):
                            status_text.text(f"Generating image for page {i+1}/{len(story_pages)}...")
                            
                            # Try AI generation first if enabled
                            image_path = None
                            if use_ai:
                                try:
                                    image_path = self.generate_ai_image(page_text, i+1, image_style)
                                    if image_path and os.path.exists(image_path):
                                        st.success(f"🤖 AI-generated image for page {i+1}")
                                    else:
                                        st.warning(f"⚠️ AI generation failed for page {i+1}, using placeholder")
                                        image_path = None
                                except Exception as e:
                                    st.warning(f"⚠️ AI generation error for page {i+1}: {str(e)[:50]}... using placeholder")
                                    image_path = None
                            
                            # Fall back to improved placeholder if AI fails or is disabled
                            if not image_path or not os.path.exists(image_path):
                                try:
                                    image_path = self.generate_placeholder_image(page_text, i+1, image_style)
                                    if image_path and os.path.exists(image_path):
                                        st.success(f"✅ Generated placeholder for page {i+1}")
                                    else:
                                        st.error(f"❌ Failed to generate placeholder for page {i+1}")
                                        # Create a basic fallback image
                                        image_path = self._create_basic_fallback_image(i+1, image_style)
                                        if image_path:
                                            st.info(f"🔄 Using basic fallback for page {i+1}")
                                except Exception as e:
                                    st.error(f"❌ Error generating placeholder for page {i+1}: {str(e)[:50]}...")
                                    # Create a basic fallback image
                                    image_path = self._create_basic_fallback_image(i+1, image_style)
                                    if image_path:
                                        st.info(f"🔄 Using basic fallback for page {i+1}")
                            
                            # Ensure we have an image path
                            if image_path and os.path.exists(image_path):
                                image_paths.append(image_path)
                            else:
                                st.error(f"❌ No image available for page {i+1}")
                                image_paths.append(None)
                            
                            progress_bar.progress((i + 1) / len(story_pages))
                            time.sleep(0.1)
                        
                        # Create PDF
                        status_text.text("Creating PDF storybook...")
                        pdf_path = self.create_storybook_pdf(
                            story_pages, image_paths, title, font_size, font_family
                        )
                        
                        if pdf_path and os.path.exists(pdf_path):
                            st.success("🎉 Storybook generated successfully!")
                            
                            # Store storybook data in session state for navigation
                            st.session_state.storybook_data = {
                                'story_pages': story_pages,
                                'image_paths': image_paths,
                                'title': title,
                                'pdf_path': pdf_path
                            }
                            
                            # Display interactive preview
                            st.subheader("📖 Interactive Storybook Preview")
                            
                            # Page navigation
                            total_pages = len(story_pages)
                            
                            # Initialize current page in session state
                            if 'current_preview_page' not in st.session_state:
                                st.session_state.current_preview_page = 1
                            
                            col1, col2, col3 = st.columns([1, 2, 1])
                            
                            with col1:
                                if st.button("◀️ Previous", disabled=st.session_state.current_preview_page <= 1, key="prev_btn"):
                                    st.session_state.current_preview_page = max(1, st.session_state.current_preview_page - 1)
                            
                            with col2:
                                page_slider = st.slider("📄 Page", 1, total_pages, st.session_state.current_preview_page, 
                                                      help=f"Navigate through {total_pages} pages", key="page_slider")
                                st.session_state.current_preview_page = page_slider
                            
                            with col3:
                                if st.button("Next ▶️", disabled=st.session_state.current_preview_page >= total_pages, key="next_btn"):
                                    st.session_state.current_preview_page = min(total_pages, st.session_state.current_preview_page + 1)
                            
                            # PDF Download button in navigation area
                            if os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=pdf_file.read(),
                                        file_name=f"{title.replace(' ', '_')}_storybook.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            
                            # Get current page content
                            current_page_num = st.session_state.current_preview_page
                            current_text = story_pages[current_page_num - 1] if current_page_num <= len(story_pages) else ""
                            current_image_path = image_paths[current_page_num - 1] if current_page_num <= len(image_paths) else None
                            
                            # Display current page (normal layout only)
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**🎨 Page {current_page_num} Image:**")
                                st.markdown(self._get_image_html(current_image_path, current_page_num), unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"**📝 Page {current_page_num} Text:**")
                                st.markdown(f"""
                                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff; min-height: 200px;">
                                    <p style="font-size: 16px; line-height: 1.6; color: #333; margin: 0;">
                                        {current_text}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Page info
                            st.info(f"📊 Showing page {current_page_num} of {total_pages} | {len(sent_tokenize(current_text))} sentences | {len(current_text)} characters")
                            
                            # Option to generate new storybook
                            if st.button("🔄 Generate New Storybook", key="new_storybook_btn"):
                                # Clear existing data
                                if 'storybook_data' in st.session_state:
                                    del st.session_state.storybook_data
                                if 'current_preview_page' in st.session_state:
                                    del st.session_state.current_preview_page
                                st.rerun()
                            
                            # Clean up files after a delay to allow preview
                            st.session_state['cleanup_files'] = {
                                'pdf_path': pdf_path,
                                'image_paths': image_paths,
                                'cleanup_time': time.time() + 30  # Clean up after 30 seconds
                            }
                        else:
                            st.error("❌ Failed to generate storybook. Please try again.")
                else:
                    st.warning("Please enter story content.")
        else:
            st.info("👆 Please enter story content or upload a PDF to get started.")
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### Steps to create a storybook:
            1. **Input Story**: Enter text or upload a PDF with your story
            2. **Customize Settings**: Adjust title, formatting, and page layout
            3. **Choose Style**: Select image style and font preferences
            4. **Enable AI Images**: Check the AI generation option for content-aware images
            5. **Generate**: Click generate to create your storybook
            6. **Download**: Preview and download the PDF storybook
            
            ### Features:
            - **AI-Powered Images**: Generate images based on actual story content using Pollinations AI
            - **Free Service**: No API key required, completely free to use
            - **Text-Aware Placeholders**: Smart fallback images that relate to story content
            - **Alternating Layout**: Text and image pages alternate for visual appeal
            - **Custom Formatting**: Adjustable font size, family, and page layout
            - **PDF Export**: Professional PDF output ready for printing or sharing
            
            ### Tips for best results:
            - Use clear, descriptive text for better AI image generation
            - Choose appropriate font sizes for readability
            - Consider your target audience when selecting image styles
            - Longer stories will create more pages automatically
            - AI images are generated based on key words from your story
            """)
        
        # AI Service Information
        with st.expander("🤖 Pollinations AI Service"):
            st.markdown("""
            ### About Pollinations AI:
            - **Free Service**: No registration or API key required
            - **Fast Generation**: Images are generated quickly based on your prompts
            - **Style Options**: Choose from storybook, modern, or fantasy styles
            - **Content-Aware**: Images are generated based on your story text
            
            ### How it works:
            1. **Text Analysis**: Key words are extracted from your story
            2. **Prompt Creation**: Smart prompts are generated for the AI
            3. **Image Generation**: Pollinations AI creates relevant images
            4. **Fallback**: If AI fails, text-aware placeholders are used
            
            ### Benefits:
            - Completely free to use
            - No account creation needed
            - Images relate to your story content
            - Multiple style options available
            """)
        
        # Technical details
        with st.expander("🔧 Technical Details"):
            st.markdown("""
            ### Storybook Generation:
            - **Text Processing**: Automatic sentence segmentation and formatting
            - **Page Layout**: Professional PDF layout with proper margins and spacing
            - **Image Generation**: Placeholder images with customizable styles
            - **PDF Creation**: High-quality PDF output using ReportLab
            
            ### Image Styles:
            - **Storybook**: Classic children's book style with warm colors
            - **Modern**: Clean, geometric design with contemporary colors
            - **Fantasy**: Whimsical elements with vibrant, magical colors
            
            ### Font Options:
            - **Helvetica**: Clean, modern sans-serif
            - **Times**: Traditional serif font
            - **Courier**: Monospace font for technical content
            - **Arial**: Universal sans-serif font
            
            ### Future Enhancements:
            - Integration with AI image generation APIs (DALL-E, Midjourney, etc.)
            - Multiple layout templates
            - Audio narration options
            - Interactive elements
            """)

def main():
    """Main function to run the storybook generator"""
    generator = StorybookGenerator()
    generator.render_interface()

if __name__ == "__main__":
    main()
