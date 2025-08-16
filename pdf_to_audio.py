import streamlit as st
import os
import tempfile
from typing import Optional
import time
import logging
from utils.text_processing import TextProcessor
from utils.audio_utils import AudioProcessor
from pydub import AudioSegment

class PDFToAudioConverter:
    """PDF to Audiobook Converter with multiple voice options"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        # AudioProcessor is a static class, no need to instantiate
        self.voice_options = list(AudioProcessor.VOICE_OPTIONS.keys())
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods for reliability
        """
        try:
            st.info(f"🔄 Extracting text from PDF: {os.path.basename(pdf_file_path)}")
            
            # Use the TextProcessor to extract text
            text = self.text_processor.extract_text_from_pdf(pdf_file_path)
            
            if not text or len(text.strip()) < 10:
                st.error("❌ Failed to extract meaningful text from PDF")
                return ""
            
            # Clean the extracted text
            cleaned_text = self.text_processor.clean_text(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 10:
                st.error("❌ Text cleaning resulted in empty or very short text")
                return ""
            
            st.success(f"✅ Successfully extracted {len(cleaned_text)} characters from PDF")
            return cleaned_text
            
        except Exception as e:
            st.error(f"❌ Error extracting text from PDF: {e}")
            return ""
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 500) -> list:
        """
        Split text into manageable chunks for audio processing
        """
        try:
            chunks = self.text_processor.segment_text_for_audio(text, chunk_size)
            st.info(f"📝 Text segmented into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            st.error(f"❌ Error splitting text into chunks: {e}")
            # Fallback: simple splitting
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    def convert_pdf_to_audio(self, pdf_file, voice_option, tts_method):
        """
        Convert PDF to audio using the selected TTS method and voice
        """
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_file)
            if not text:
                st.error("❌ Failed to extract text from PDF")
                return None
            
            st.success(f"✅ Extracted {len(text)} characters from PDF")
            
            # Split text into manageable chunks
            text_chunks = self.split_text_into_chunks(text)
            st.info(f"Text segmented into {len(text_chunks)} chunks for processing")
            
            # Convert each chunk to audio
            audio_segments = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, chunk in enumerate(text_chunks):
                status_text.text(f"Converting chunk {i+1}/{len(text_chunks)}...")
                
                # Debug: Show which TTS method and voice are being used
                st.info(f"🔄 Processing chunk {i+1} with TTS method: {tts_method}, Voice: {voice_option}")
                
                # Use the selected TTS method - SIMPLIFIED APPROACH
                audio_segment = None
                
                if tts_method == "pyttsx3 (Offline)" or tts_method == "Auto (Best Available)":
                    # Use Microsoft TTS for best quality
                    st.info(f"🔄 Using Microsoft TTS for chunk {i+1} with voice: {voice_option}")
                    audio_segment = AudioProcessor.text_to_speech_enhanced_pyttsx3(chunk, voice_option)
                    
                
                elif tts_method == "Simple Reliable (Always Works)":
                    st.info(f"🔄 Using Simple Reliable TTS for chunk {i+1} with voice: {voice_option}")
                    audio_segment = AudioProcessor.text_to_speech_simple_reliable(chunk, voice_option)
                    
                
                elif tts_method == "gTTS (Online)":
                    st.info(f"🔄 Using gTTS for chunk {i+1} with voice: {voice_option}")
                    audio_segment = AudioProcessor.text_to_speech_enhanced_gtts(chunk, voice_option)
                    
                
                elif tts_method == "Tone Generation (Basic)":
                    st.info(f"🔄 Using tone generation for chunk {i+1} with voice: {voice_option}")
                    audio_segment = AudioProcessor.text_to_speech_simple_tones(chunk, voice_option)
                    
                
                # Fallback to Microsoft TTS if nothing else worked
                if not audio_segment:
                    st.info(f"🔄 Using fallback Microsoft TTS for chunk {i+1} with voice: {voice_option}")
                    audio_segment = AudioProcessor.text_to_speech_enhanced_pyttsx3(chunk, voice_option)
                    
                
                if audio_segment:
                    if isinstance(audio_segment, AudioSegment) and hasattr(audio_segment, 'export'):
                        audio_segments.append(audio_segment)
                    elif isinstance(audio_segment, str) and os.path.exists(audio_segment):
                        try:
                            loaded_audio_segment = AudioSegment.from_file(audio_segment)
                            audio_segments.append(loaded_audio_segment)
                            
                        except Exception as e:
                            st.error(f"❌ Chunk {i+1} failed to load audio from file {audio_segment}: {e}, skipping")
                            logging.error(f"Failed to load audio from file {audio_segment} for chunk {i+1}: {e}")
                    else:
                        st.error(f"❌ Chunk {i+1} returned invalid audio type: {type(audio_segment)}, skipping")
                        logging.error(f"Invalid audio type for chunk {i+1}: {type(audio_segment)}")
                else:
                    st.error(f"❌ All TTS methods failed for chunk {i+1} - Voice: {voice_option}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(text_chunks))
                time.sleep(0.1)  # Small delay for better UX
            
            if not audio_segments:
                st.error("❌ Failed to convert any text chunks to audio")
                return None
            
            st.success(f"✅ Successfully converted {len(audio_segments)} chunks to audio")
            
            # Combine audio segments using the new simple method
            st.info("🔄 Combining audio segments...")
            
            # Generate output filename
            timestamp = int(time.time())
            filename = f"audiobook_{voice_option.replace(' ', '_')}_{timestamp}.wav"
            
            # Use temp directory for output
            import tempfile
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, filename)
            
            st.info(f"Output path: {output_path}")
            
            # Use the new simple file creation method
            result_path = AudioProcessor.create_audio_file_simple(audio_segments, output_path, voice_option)
            
            if result_path:
                st.success("🎉 Audiobook conversion completed successfully!")
                return result_path
            else:
                st.error("❌ Failed to create audio file")
                return None
                
        except Exception as e:
            logging.exception("Error converting PDF to audio")
            st.error(f"❌ An unexpected error occurred during PDF to audio conversion. Please check the logs for details: {e}")
            return None
    
    def render_interface(self):
        """Render the Streamlit interface for PDF to audio conversion"""
        st.header("📚 PDF to Audiobook Converter")
        st.markdown("Convert your PDF documents into high-quality audiobooks with natural-sounding voices.")
        
        # Important notice about voice differences
        st.info("🎯 **IMPORTANT**: For best quality and actual word reading, use 'pyttsx3 (Offline)' as TTS method!")
        st.success("✅ Microsoft TTS provides high-quality speech with actual word reading")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file", 
            type=['pdf'],
            help="Upload a PDF file to convert to audio"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.write("**File Details:**")
            for key, value in file_details.items():
                st.write(f"- {key}: {value}")
            
            # Voice selection
            st.subheader("🎤 Voice Selection")
            voice_option = st.selectbox(
                "Choose your preferred voice:",
                self.voice_options,
                help="Select from 4 different voice options"
            )
            
            # TTS Engine Selection
            st.subheader("🔧 TTS Engine Selection")
            
            # Test available engines
            with st.spinner("Testing available TTS engines..."):
                available_engines = AudioProcessor.test_available_tts_engines()
            
            # Show available engines
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Available TTS Engines:**")
                for engine_name, engine_info in available_engines.items():
                    if engine_info['status'] == 'Available':
                        st.success(f"✅ {engine_name}: {engine_info['quality']}")
                    else:
                        st.error(f"❌ {engine_name}: {engine_info['error']}")
            
            with col2:
                st.write("**Recommended Engine:**")
                if available_engines.get('pyttsx3', {}).get('status') == 'Available':
                    st.success("🎯 pyttsx3 (Best quality, offline)")
                elif available_engines.get('gtts', {}).get('status') == 'Available':
                    st.success("🎯 gTTS (Good quality, online)")
                else:
                    st.warning("⚠️ Using basic tone generation")
                
                # Add voice quality recommendation
                st.write("**For Best Quality:**")
                st.success("🎯 pyttsx3 (Microsoft TTS - Actual word reading)")
                st.info("Microsoft TTS provides high-quality speech with real pronunciation")
            
            # TTS Method Selection
            tts_method = st.selectbox(
                "Choose TTS method (if multiple available):",
                ["Simple Reliable (Always Works)", "Auto (Best Available)", "pyttsx3 (Offline)", "gTTS (Online)", "Tone Generation (Basic)"],
                help="Select your preferred TTS method (Simple Reliable recommended for voice differences)"
            )
            
            # Test TTS button
            if st.button("🎵 Test TTS Method", key="test_tts_btn"):
                st.info("Testing TTS method with sample text...")
                
                sample_text = "Hello! This is a test of the text-to-speech system."
                
                # Test the selected method
                test_audio = None
                if tts_method == "pyttsx3 (Offline)":
                    test_audio = AudioProcessor.text_to_speech_enhanced_pyttsx3(sample_text, voice_option)
                elif tts_method == "gTTS (Online)":
                    test_audio = AudioProcessor.text_to_speech_enhanced_gtts(sample_text, voice_option)
                elif tts_method == "Tone Generation (Basic)":
                      test_audio = AudioProcessor.text_to_speech_simple_tones(sample_text, voice_option)
                elif tts_method == "Simple Reliable (Always Works)":
                    test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice_option)
                
                if test_audio:
                    st.success("✅ TTS test successful! Listen to the sample:")
                    
                    # Create temporary file for test audio
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_test:
                        tmp_test_path = tmp_test.name
                    
                    # Export test audio
                    test_audio.export(tmp_test_path, format="wav")
                    
                    # Display test audio player
                    with open(tmp_test_path, "rb") as test_audio_file:
                        st.audio(test_audio_file.read(), format="audio/wav")
                    
                    # Clean up test file
                    try:
                        os.remove(tmp_test_path)
                    except:
                        pass
                else:
                    st.error("❌ TTS test failed. Please try a different method.")
            
            # Simple Voice Test - Direct and Effective
            if st.button("🎵 Test Voice Differences", key="test_voice_differences_btn"):
                st.subheader("🎵 Direct Voice Test")
                st.info("Testing voice differences with simple text...")
                
                sample_text = "Hello World"
                voice_options = ["British Male", "British Female", "American Male", "American Female"]
                
                # Test each voice directly
                for voice in voice_options:
                    st.write(f"**{voice}:**")
                    
                    # Generate audio using Simple Reliable method (best for voice differences)
                    test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice)
                    
                    if test_audio:
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_voice:
                            tmp_voice_path = tmp_voice.name
                        
                        # Export audio
                        test_audio.export(tmp_voice_path, format="wav")
                        
                        # Display audio player
                        with open(tmp_voice_path, "rb") as voice_audio_file:
                            st.audio(voice_audio_file.read(), format="audio/wav")
                        
                        # Show audio info
                        duration_ms = len(test_audio)
                        st.write(f"Duration: {duration_ms}ms")
                        
                        # Show voice characteristics
                        if "British Male" in voice:
                            st.write("🎵 **Voice Characteristics**: Deep (120Hz), Slow (200ms/char), British accent")
                        elif "British Female" in voice:
                            st.write("🎵 **Voice Characteristics**: High (280Hz), Medium (180ms/char), British accent")
                        elif "American Male" in voice:
                            st.write("🎵 **Voice Characteristics**: Medium (140Hz), Fast (160ms/char), American accent")
                        elif "American Female" in voice:
                            st.write("🎵 **Voice Characteristics**: Very High (320Hz), Very Fast (140ms/char), American accent")
                        
                        # Clean up
                        try:
                            os.remove(tmp_voice_path)
                        except:
                            pass
                        
                        st.success(f"✅ {voice} generated successfully")
                    else:
                        st.error(f"❌ Failed to generate {voice}")
                    
                    st.write("---")
                
                st.success("🎉 Voice test completed! Listen to hear the differences.")
            
            # Voice Comparison Feature
            if st.button("🎭 Compare All Voices", key="compare_voices_btn"):
                st.subheader("🎭 Voice Comparison")
                st.info("Testing all four voice options with the same sample text...")
                
                sample_text = "Hello! This is a test of the text-to-speech system."
                voice_options = ["British Male", "British Female", "American Male", "American Female"]
                
                # Test all voices with the selected TTS method
                for voice in voice_options:
                    st.write(f"**{voice}:**")
                    
                    # Generate audio for this voice
                    test_audio = None
                    if tts_method == "pyttsx3 (Offline)":
                        test_audio = AudioProcessor.text_to_speech_enhanced_pyttsx3(sample_text, voice)
                    elif tts_method == "gTTS (Online)":
                        test_audio = AudioProcessor.text_to_speech_enhanced_gtts(sample_text, voice)
                    elif tts_method == "Tone Generation (Basic)":
                        test_audio = AudioProcessor.text_to_speech_simple_tones(sample_text, voice)
                    elif tts_method == "Simple Reliable (Always Works)":
                        test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice)
                    
                    if test_audio:
                        # Create temporary file for this voice
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_voice:
                            tmp_voice_path = tmp_voice.name
                        
                        # Export voice audio
                        test_audio.export(tmp_voice_path, format="wav")
                        
                        # Display voice audio player
                        with open(tmp_voice_path, "rb") as voice_audio_file:
                            st.audio(voice_audio_file.read(), format="audio/wav")
                        
                        # Clean up voice file
                        try:
                            os.remove(tmp_voice_path)
                        except:
                            pass
                        
                        st.success(f"✅ {voice} generated successfully")
                    else:
                        st.error(f"❌ Failed to generate {voice}")
                    
                    st.write("---")
                
                st.success("🎉 Voice comparison completed! Listen to hear the differences.")
            
            # Voice Frequency Test Feature
            if st.button("🔬 Test Voice Frequencies", key="test_frequencies_btn"):
                st.subheader("🔬 Voice Frequency Analysis")
                st.info("Testing voice characteristics and showing frequency information...")
                
                sample_text = "Test"
                voice_options = ["British Male", "British Female", "American Male", "American Female"]
                
                # Test each voice and show frequency characteristics
                for voice in voice_options:
                    st.write(f"**{voice}:**")
                    
                    # Show expected frequency characteristics
                    if "British Male" in voice:
                        st.write("Expected: Base Freq: 120Hz, Speed: 200ms/char, Accent: British")
                    elif "British Female" in voice:
                        st.write("Expected: Base Freq: 280Hz, Speed: 180ms/char, Accent: British")
                    elif "American Male" in voice:
                        st.write("Expected: Base Freq: 140Hz, Speed: 160ms/char, Accent: American")
                    elif "American Female" in voice:
                        st.write("Expected: Base Freq: 320Hz, Speed: 140ms/char, Accent: American")
                    
                    # Generate audio for this voice
                    test_audio = None
                    if tts_method == "Simple Reliable (Always Works)":
                        test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice)
                    elif tts_method == "Tone Generation (Basic)":
                        test_audio = AudioProcessor.text_to_speech_simple_tones(sample_text, voice)
                    elif tts_method == "Auto (Best Available)":
                        test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice)
                    else:
                        test_audio = AudioProcessor.text_to_speech_simple_reliable(sample_text, voice)
                    
                    if test_audio:
                        # Create temporary file for this voice
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_voice:
                            tmp_voice_path = tmp_voice.name
                        
                        # Export voice audio
                        test_audio.export(tmp_voice_path, format="wav")
                        
                        # Display voice audio player
                        with open(tmp_voice_path, "rb") as voice_audio_file:
                            st.audio(voice_audio_file.read(), format="audio/wav")
                        
                        # Show audio duration
                        duration_ms = len(test_audio)
                        st.write(f"Audio Duration: {duration_ms}ms")
                        
                        # Clean up voice file
                        try:
                            os.remove(tmp_voice_path)
                        except:
                            pass
                        
                        st.success(f"✅ {voice} generated successfully")
                    else:
                        st.error(f"❌ Failed to generate {voice}")
                    
                    st.write("---")
                
                st.success("🎉 Voice frequency test completed! Check if voices sound different.")
            

            
            # Display voice preview
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Selected Voice:** {voice_option}")
                if "British" in voice_option:
                    st.write("🇬🇧 British accent with clear pronunciation")
                else:
                    st.write("🇺🇸 American accent with natural flow")
            
            with col2:
                if "Male" in voice_option:
                    st.write("👨 Deep, authoritative tone")
                else:
                    st.write("👩 Warm, engaging tone")
            
            # Processing options
            st.subheader("⚙️ Processing Options")
            chunk_size = st.slider(
                "Text chunk size (characters):",
                min_value=200,
                max_value=1000,
                value=500,
                step=100,
                help="Larger chunks may be faster but could affect quality"
            )
            
            # Important reminder about voice differences
            st.info("🎯 **REMINDER**: Use 'Simple Reliable (Always Works)' for best voice differences!")
            
            # Convert button
            if st.button("🎵 Convert to Audiobook", type="primary"):
                if uploaded_file is not None:
                    # Create a temporary file for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        # Convert PDF to audio
                        audio_file = self.convert_pdf_to_audio(
                            tmp_file_path, voice_option, tts_method
                        )
                        
                        if audio_file:
                            st.success("🎉 Audiobook conversion completed!")
                            
                            # Display audio player
                            st.subheader("🎧 Listen to Your Audiobook")
                            
                            # Get audio duration
                            duration = AudioProcessor.get_audio_duration(audio_file)
                            st.write(f"**Duration:** {duration:.1f} seconds ({duration/60:.1f} minutes)")
                            
                            # Audio player
                            with open(audio_file, "rb") as audio:
                                st.audio(audio.read(), format="audio/wav")
                            
                            # Download button
                            st.download_button(
                                label="📥 Download WAV",
                                data=open(audio_file, "rb").read(),
                                file_name=f"audiobook_{voice_option.replace(' ', '_')}.wav",
                                mime="audio/wav"
                            )
                            
                            # Clean up
                            try:
                                os.remove(audio_file)
                            except:
                                pass
                        else:
                            st.error("❌ Conversion failed. Please try again.")
                    
                    finally:
                        # Clean up temporary file
                        try:
                            os.remove(tmp_file_path)
                        except:
                            pass
                else:
                    st.warning("Please upload a PDF file first.")
        
        # Show audio player if audio was generated in this session
        if hasattr(st.session_state, 'audio_file_path') and st.session_state.audio_file_path:
            st.subheader("🎧 Your Generated Audiobook")
            
            # Display file info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Voice Used:** {st.session_state.voice_used}")
                st.write(f"**Filename:** {st.session_state.audio_filename}")
            
            with col2:
                # Get audio duration
                try:
                    duration = AudioProcessor.get_audio_duration(st.session_state.audio_file_path)
                    st.write(f"**Duration:** {duration:.1f} seconds ({duration/60:.1f} minutes)")
                except:
                    st.write("**Duration:** Calculating...")
            
            # Audio preview player (if available)
            if hasattr(st.session_state, 'audio_preview') and st.session_state.audio_preview:
                st.subheader("🎵 Audio Preview (First 3 segments)")
                try:
                    # Create a temporary file for the preview
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_preview:
                        tmp_preview.write(st.session_state.audio_preview)
                        tmp_preview_path = tmp_preview.name
                    
                    # Display preview player
                    with open(tmp_preview_path, "rb") as preview_audio:
                        st.audio(preview_audio.read(), format="audio/wav")
                    
                    # Clean up temp preview file
                    try:
                        os.remove(tmp_preview_path)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"Error loading preview: {e}")
            
            # Base64 audio player for immediate playback
            if hasattr(st.session_state, 'base64_audio') and st.session_state.base64_audio:
                st.subheader("🎵 Immediate Audio Playback")
                try:
                    # Use HTML audio player with base64 data
                    html_audio = f"""
                    <audio controls style="width: 100%;">
                        <source src="{st.session_state.base64_audio}" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                    """
                    st.markdown(html_audio, unsafe_allow_html=True)
                    st.success("✅ Audio ready for immediate playback!")
                except Exception as e:
                    st.error(f"Error with base64 audio: {e}")
            
            # Full audio player
            st.subheader("🎧 Full Audiobook")
            try:
                with open(st.session_state.audio_file_path, "rb") as audio:
                    st.audio(audio.read(), format="audio/mp3")
            except Exception as e:
                st.error(f"Error loading audio: {e}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Play button (refresh audio player)
                if st.button("▶️ Play Again", key="play_audio_btn"):
                    st.rerun()
            
            with col2:
                # Download button
                try:
                    with open(st.session_state.audio_file_path, "rb") as audio:
                        st.download_button(
                            label="📥 Download MP3",
                            data=audio.read(),
                            file_name=st.session_state.audio_filename,
                            mime="audio/mp3",
                            key="download_audio_btn"
                        )
                except Exception as e:
                    st.error(f"Download error: {e}")
            
            with col3:
                # Clear button
                if st.button("🗑️ Clear", key="clear_audio_btn"):
                    # Clean up file
                    try:
                        if os.path.exists(st.session_state.audio_file_path):
                            os.remove(st.session_state.audio_file_path)
                    except:
                        pass
                    
                    # Clear session state
                    if 'audio_file_path' in st.session_state:
                        del st.session_state.audio_file_path
                    if 'audio_filename' in st.session_state:
                        del st.session_state.audio_filename
                    if 'voice_used' in st.session_state:
                        del st.session_state.voice_used
                    if 'audio_preview' in st.session_state:
                        del st.session_state.audio_preview
                    if 'base64_audio' in st.session_state:
                        del st.session_state.base64_audio
                    
                    st.rerun()
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### Steps to convert PDF to audiobook:
            1. **Upload PDF**: Click 'Browse files' and select your PDF document
            2. **Choose Voice**: Select from 4 voice options (British/American, Male/Female)
            3. **Select TTS Engine**: Choose your preferred text-to-speech method
            4. **Test TTS**: Use the test button to preview audio quality
            5. **Adjust Settings**: Modify chunk size if needed for better quality
            6. **Convert**: Click the convert button and wait for processing
            7. **Download**: Listen to preview and download the MP3 file
            
            ### TTS Engine Options:
            - **pyttsx3 (Offline)**: High-quality offline TTS with natural voices
            - **gTTS (Online)**: Google's high-quality online TTS service
            - **Tone Generation**: Basic but reliable offline tone generation
            - **Simple Reliable**: Always works, generates character-based audio
            - **Auto**: Automatically selects the best available method
            
            ### Tips for best results:
            - Use PDFs with clear, readable text
            - Test TTS methods before full conversion
            - Use "Compare All Voices" to hear differences between voice options
            - pyttsx3 works offline and has the best quality
            - gTTS requires internet but has excellent voice quality
            - Larger chunk sizes may process faster but could affect natural flow
            
            ### Voice Characteristics:
            - **British Male**: Deep, formal, authoritative (180Hz base)
            - **British Female**: Clear, professional, engaging (320Hz base)
            - **American Male**: Natural, conversational, warm (200Hz base)
            - **American Female**: Friendly, expressive, easy to follow (350Hz base)
            """)
        
        # Technical details
        with st.expander("🔧 Technical Details"):
            st.markdown("""
            ### Text Processing:
            - **PDF Parsing**: Uses both pdfplumber and PyPDF2 for maximum text extraction
            - **Text Cleaning**: Removes formatting issues and optimizes for TTS
            - **Segmentation**: Splits text into optimal chunks for natural speech
            
            ### TTS Engines:
            - **pyttsx3**: High-quality offline TTS with system voices
            - **gTTS**: Google's online TTS with multiple language support
            - **Tone Generation**: Custom frequency-based audio generation
            - **Simple Reliable**: Character-based audio generation (always works)
            - **Fallback System**: Multiple TTS methods ensure reliability
            
            ### Audio Processing:
            - **Format Support**: WAV, MP3, and base64 audio formats
            - **Audio Optimization**: Normalization, filtering, and quality enhancement
            - **Memory Processing**: In-memory audio generation and combination
            - **File Management**: Reliable file creation with multiple fallbacks
            
            ### Voice Options:
            - **British Male**: Deep, authoritative, formal
            - **British Female**: Clear, professional, engaging
            - **American Male**: Natural, conversational, warm
            - **American Female**: Friendly, expressive, easy to follow
            """)

def main():
    """Main function to run the PDF to Audio converter"""
    converter = PDFToAudioConverter()
    converter.render_interface()

if __name__ == "__main__":
    main()
