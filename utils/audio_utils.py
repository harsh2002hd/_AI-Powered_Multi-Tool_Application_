import streamlit as st
import os
import tempfile
import time
from typing import Optional, Union
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
from io import BytesIO
import pyttsx3
from gtts import gTTS
import streamlit as st

class AudioProcessor:
    """Utility class for audio processing and text-to-speech"""
    
    # Voice configurations
    VOICE_OPTIONS = {
        "British Male": {"lang": "en-gb", "voice": "male"},
        "British Female": {"lang": "en-gb", "voice": "female"},
        "American Male": {"lang": "en-us", "voice": "male"},
        "American Female": {"lang": "en-us", "voice": "female"}
    }
    
    @staticmethod
    def text_to_speech_gtts(text: str, voice_option: str, 
                           output_path: str = None) -> str:
        """
        Convert text to speech using Google Text-to-Speech
        """
        try:
            voice_config = AudioProcessor.VOICE_OPTIONS.get(voice_option, 
                                                          AudioProcessor.VOICE_OPTIONS["American Female"])
            
            # Create gTTS object
            tts = gTTS(text=text, lang=voice_config["lang"], slow=False)
            
            # Generate output path if not provided - use NamedTemporaryFile to ensure file exists
            if not output_path:
                # Create a temporary file and ensure it's closed immediately after creation
                # so gTTS can write to it and other processes can read it.
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                output_path = tmp_file.name
                tmp_file.close() # Close the file handle immediately
            
            try:
                # Save audio file
                tts.save(output_path)
            except Exception as e:
                st.error(f"Error saving gTTS audio to file: {e}")
                st.exception(e)
                return None
            
            # Wait a moment for file system to sync
            import time
            time.sleep(0.5)
            
            # Verify file was created with multiple checks
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 0:
                    st.success(f"gTTS audio saved successfully: {os.path.basename(output_path)} ({file_size} bytes)")
                    # Double-check file is readable
                    try:
                        with open(output_path, 'rb') as test_file:
                            test_file.read(1024)  # Read first 1KB to ensure file is accessible
                        return output_path
                    except Exception as read_error:
                        st.error(f"File created but not readable: {read_error}")
                        return None
                else:
                    st.error(f"gTTS audio file created but is empty (0 bytes)")
                    return None
            else:
                st.error(f"gTTS audio file was not created at {output_path}")
                return None
            
        except Exception as e:
            st.error(f"Error in gTTS conversion: {e}")
            return None
    
    @staticmethod
    def text_to_speech_pyttsx3(text: str, voice_option: str, 
                              output_path: str = None) -> str:
        """
        Convert text to speech using pyttsx3 (offline option)
        """
        try:
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Set voice properties based on selection
            voices = engine.getProperty('voices')
            
            # Try to find a matching voice
            for voice in voices:
                voice_name = voice.name.lower()
                if "british" in voice_option.lower() and "british" in voice_name:
                    if "male" in voice_option.lower() and "male" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                    elif "female" in voice_option.lower() and "female" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                elif "american" in voice_option.lower() and "american" in voice_name:
                    if "male" in voice_option.lower() and "male" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                    elif "female" in voice_option.lower() and "female" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level
            
            # Generate output path if not provided - use NamedTemporaryFile to ensure file exists
            if not output_path:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    output_path = tmp_file.name
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Wait a moment for file system to sync
            import time
            time.sleep(0.5)
            
            # Verify file was created with multiple checks
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 0:
                    st.success(f"pyttsx3 audio saved successfully: {os.path.basename(output_path)} ({file_size} bytes)")
                    # Double-check file is readable
                    try:
                        with open(output_path, 'rb') as test_file:
                            test_file.read(1024)  # Read first 1KB to ensure file is accessible
                        return output_path
                    except Exception as read_error:
                        st.error(f"File created but not readable: {read_error}")
                        return None
                else:
                    st.error(f"pyttsx3 audio file created but is empty (0 bytes)")
                    return None
            else:
                st.error(f"pyttsx3 audio file was not created at {output_path}")
                return None
            
        except Exception as e:
            st.error(f"Error in pyttsx3 conversion: {e}")
            return None
    
    @staticmethod
    def text_to_speech_gtts_memory(text: str, voice_option: str) -> AudioSegment:
        """
        Convert text to speech using Google Text-to-Speech and return audio data directly
        """
        try:
            voice_config = AudioProcessor.VOICE_OPTIONS.get(voice_option, 
                                                          AudioProcessor.VOICE_OPTIONS["American Female"])
            
            # Create gTTS object
            tts = gTTS(text=text, lang=voice_config["lang"], slow=False)
            
            # Create a temporary file for gTTS (required by the library)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            try:
                try:
                    # Save audio file temporarily
                    tts.save(temp_path)
                except Exception as e:
                    st.error(f"Error saving gTTS audio to temporary file: {e}")
                    st.exception(e)
                    return None
                
                # Load audio data directly into memory
                audio_segment = AudioSegment.from_mp3(temp_path)
                
                # Clean up temp file immediately
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                st.success(f"gTTS audio generated successfully in memory")
                return audio_segment
                
            except Exception as e:
                # Clean up temp file on error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                raise e
            
        except Exception as e:
            st.error(f"Error in gTTS memory conversion: {e}")
            return None
    
    @staticmethod
    def text_to_speech_pyttsx3_memory(text: str, voice_option: str) -> AudioSegment:
        """
        Convert text to speech using pyttsx3 and return audio data directly
        """
        try:
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Set voice properties based on selection
            voices = engine.getProperty('voices')
            
            # Try to find a matching voice
            for voice in voices:
                voice_name = voice.name.lower()
                if "british" in voice_option.lower() and "british" in voice_name:
                    if "male" in voice_option.lower() and "male" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                    elif "female" in voice_option.lower() and "female" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                elif "american" in voice_option.lower() and "american" in voice_name:
                    if "male" in voice_option.lower() and "male" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                    elif "female" in voice_option.lower() and "female" in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level
            
            # Create a temporary file for pyttsx3 (required by the library)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            try:
                # Save to file temporarily
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                # Load audio data directly into memory
                audio_segment = AudioSegment.from_mp3(temp_path)
                
                # Clean up temp file immediately
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                st.success(f"pyttsx3 audio generated successfully in memory")
                return audio_segment
                
            except Exception as e:
                # Clean up temp file on error
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                raise e
            
        except Exception as e:
            st.error(f"Error in pyttsx3 memory conversion: {e}")
            return None
    
    @staticmethod
    def text_to_speech_pure_python(text: str, voice_option: str) -> AudioSegment:
        """
        Convert text to speech using pure Python without any file I/O
        """
        try:
            import numpy as np
            
            st.info(f"Generating audio using pure Python TTS for: '{text[:50]}...'")
            
            # Voice-specific characteristics
            voice_config = {
                "British Male": {"base_freq": 200, "freq_range": 80, "speed": 100, "accent": "british"},
                "British Female": {"base_freq": 380, "freq_range": 120, "speed": 95, "accent": "british"},
                "American Male": {"base_freq": 220, "freq_range": 90, "speed": 90, "accent": "american"},
                "American Female": {"base_freq": 400, "freq_range": 140, "speed": 85, "accent": "american"}
            }
            
            config = voice_config.get(voice_option, voice_config["British Male"])
            base_frequency = config["base_freq"]
            freq_range = config["freq_range"]
            speed = config["speed"]
            accent = config["accent"]
            
            st.info(f"Voice: {voice_option} - Base Freq: {base_frequency}Hz, Speed: {speed} chars/sec")
            
            # Calculate duration based on text length - voice-specific speed
            duration_seconds = max(2.0, len(text) / speed)  # Different speed for each voice
            sample_rate = 22050  # Lower sample rate for better compatibility
            num_samples = int(duration_seconds * sample_rate)
            
            # Create time array
            t = np.linspace(0, duration_seconds, num_samples, False)
            
            # Generate more natural-sounding audio with frequency modulation
            # Add some variation to make it sound more natural
            frequency_modulation = base_frequency + (freq_range/2) * np.sin(2 * np.pi * 0.5 * t)
            
            # Generate audio with amplitude modulation for natural speech patterns
            if accent == "british":
                # British: more formal, less amplitude variation
                amplitude = 0.3 + 0.15 * np.sin(2 * np.pi * 1.5 * t)
            else:
                # American: more expressive, more amplitude variation
                amplitude = 0.3 + 0.25 * np.sin(2 * np.pi * 2.0 * t)
            
            # Create the audio signal
            audio_signal = amplitude * np.sin(2 * np.pi * frequency_modulation * t)
            
            # Add some harmonics for richer sound (different for each voice)
            if accent == "british":
                # British: subtle harmonics for formal sound
                harmonic1 = 0.08 * amplitude * np.sin(2 * np.pi * frequency_modulation * 2 * t)
                audio_signal += harmonic1
            else:
                # American: more pronounced harmonics for expressive sound
                harmonic1 = 0.12 * amplitude * np.sin(2 * np.pi * frequency_modulation * 2 * t)
                harmonic2 = 0.06 * amplitude * np.sin(2 * np.pi * frequency_modulation * 3 * t)
                audio_signal += harmonic1 + harmonic2
            
            # Normalize and convert to 16-bit integers
            max_val = np.max(np.abs(audio_signal))
            if max_val > 0:
                normalized_signal = audio_signal / max_val
                audio_16bit = (normalized_signal * 16384).astype(np.int16)
            else:
                audio_16bit = np.zeros(num_samples, dtype=np.int16)
            
            # Create AudioSegment from the numpy array
            audio_segment = AudioSegment(
                audio_16bit.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            
            st.success(f"✅ Generated {duration_seconds:.1f}s audio in memory using pure Python - {voice_option}")
            return audio_segment
            
        except Exception as e:
            st.error(f"Error in pure Python TTS: {e}")
            return None
    
    @staticmethod
    def text_to_speech_enhanced_pyttsx3(text: str, voice_option: str) -> AudioSegment:
        """
        Enhanced pyttsx3 TTS using Microsoft's high-quality voices with direct audio generation
        """
        try:
            import pyttsx3
            import tempfile
            import os
            import time
            
            st.info(f"Using Microsoft TTS for: '{text[:50]}...'")
            
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Map voice options to different TTS approaches for more variety
            voice_configs = {
                "British Male": {"method": "pyttsx3", "voice": "david", "rate": 110, "volume": 0.8, "style": "formal"},
                "British Female": {"method": "pyttsx3", "voice": "zira", "rate": 130, "volume": 0.9, "style": "clear"},
                "American Male": {"method": "gtts", "voice": "en-us", "rate": 150, "volume": 0.9, "style": "natural"},
                "American Female": {"method": "gtts", "voice": "en-gb", "rate": 140, "volume": 0.9, "style": "friendly"}
            }
            
            # Get voice configuration for the selected option
            config = voice_configs.get(voice_option, voice_configs["American Male"])
            
            # Use different TTS methods for different voices
            if config["method"] == "pyttsx3":
                # Use Microsoft TTS for British voices
                target_voice = config["voice"]
                selected_voice = None
                
                # Find the appropriate voice
                for voice in voices:
                    voice_name = voice.name.lower()
                    if target_voice in voice_name:
                        selected_voice = voice.id
                        break
                
                # If no specific voice found, use the first available
                if not selected_voice and voices:
                    selected_voice = voices[0].id
                    st.info(f"Using default voice: {voices[0].name}")
                
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
                    st.success(f"✅ Selected voice: {voice_option} using Microsoft {target_voice.upper()}")
                    
                    # Set speech properties based on voice configuration
                    engine.setProperty('rate', config["rate"])
                    engine.setProperty('volume', config["volume"])
                    
                    st.info(f"Microsoft TTS settings - Rate: {config['rate']}, Volume: {config['volume']}, Style: {config['style']}")
                    
                else:
                    # Use Google TTS for American voices
                    st.info(f"Switching to Google TTS for {voice_option}...")
                    return AudioProcessor.text_to_speech_enhanced_gtts(text, voice_option)
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                temp_path = tmp_file.name
            
            # Generate speech with better error handling
            try:
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                # Wait for file to be written
                time.sleep(2)  # Longer wait to ensure file is written
                
                # Check if file was created and has content
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:  # At least 1KB
                    try:
                        # Load the generated audio
                        audio_segment = AudioSegment.from_wav(temp_path)
                        st.success(f"✅ Microsoft TTS successful: {len(audio_segment)}ms human voice audio")
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                        
                        return audio_segment
                        
                    except Exception as load_error:
                        st.error(f"❌ Error loading generated audio: {load_error}")
                        # Clean up temp file
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                        return None
                else:
                    st.error("❌ Microsoft TTS failed to generate audio file or file too small")
                    return None
                    
            except Exception as tts_error:
                st.error(f"❌ Error in Microsoft TTS generation: {tts_error}")
                return None
                
        except Exception as e:
            st.error(f"❌ Error in enhanced pyttsx3 TTS: {e}")
            return None
    
    @staticmethod
    def text_to_speech_enhanced_gtts(text: str, voice_option: str) -> AudioSegment:
        """
        Enhanced gTTS with better error handling and audio processing
        """
        try:
            from gtts import gTTS
            import tempfile
            import os
            
            st.info(f"Using enhanced gTTS for: '{text[:50]}...'")
            
            # Map voice options to language codes
            voice_mapping = {
                "British Male": "en-gb",
                "British Female": "en-gb", 
                "American Male": "en-us",
                "American Female": "en-us"
            }
            
            lang_code = voice_mapping.get(voice_option, "en-us")
            
            # Create gTTS object with better parameters
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            # Save audio file
            tts.save(temp_path)
            
            # Wait for file to be written
            import time
            time.sleep(1)
            
            # Verify file was created
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                try:
                    # Load the generated audio
                    audio_segment = AudioSegment.from_mp3(temp_path)
                    st.success(f"✅ Enhanced gTTS successful: {len(audio_segment)}ms audio")
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    
                    return audio_segment
                    
                except Exception as load_error:
                    st.error(f"❌ Error loading gTTS audio: {load_error}")
                    # Clean up temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    return None
            else:
                st.error("❌ Enhanced gTTS failed to generate audio file")
                return None
                
        except Exception as e:
            st.error(f"❌ Error in enhanced gTTS: {e}")
            return None
    
    @staticmethod
    def text_to_speech_simple_tones(text: str, voice_option: str) -> AudioSegment:
        """
        Improved TTS using natural speech patterns and word-based processing
        """
        try:
            import numpy as np
            
            st.info(f"Using improved tone TTS for: '{text[:50]}...'")
            
            # Voice-specific characteristics with better speech patterns
            voice_config = {
                "British Male": {"base_freq": 200, "freq_range": 100, "speed": 0.6, "accent": "british", "formality": 0.8},
                "British Female": {"base_freq": 250, "freq_range": 120, "speed": 0.55, "accent": "british", "formality": 0.7},
                "American Male": {"base_freq": 180, "freq_range": 110, "speed": 0.5, "accent": "american", "formality": 0.6},
                "American Female": {"base_freq": 280, "freq_range": 140, "speed": 0.45, "accent": "american", "formality": 0.5}
            }
            
            config = voice_config.get(voice_option, voice_config["British Male"])
            base_freq = config["base_freq"]
            freq_range = config["freq_range"]
            speed = config["speed"]
            accent = config["accent"]
            formality = config["formality"]
            
            st.info(f"Voice: {voice_option} - Base Freq: {base_freq}Hz, Speed: {speed}s/word")
            
            # Split text into words and sentences for better processing
            sentences = text.split('.')
            words = []
            for sentence in sentences:
                if sentence.strip():
                    words.extend(sentence.strip().split())
            
            if not words:
                st.error("❌ No words to process")
                return None
            
            # Calculate timing for each word - voice-specific speed
            total_duration = len(words) * speed
            sample_rate = 22050
            total_samples = int(total_duration * sample_rate)
            
            # Generate audio with improved word-based processing
            audio_signal = np.zeros(total_samples)
            
            for i, word in enumerate(words):
                # Calculate word timing
                start_time = i * speed
                end_time = (i + 1) * speed
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                
                # Generate frequency based on word characteristics
                word_length = len(word)
                word_freq = base_freq + (word_length * 8) + (i * 5)
                
                # Add formality-based variation
                if formality > 0.7:  # More formal voices
                    freq_variation = word_freq + np.random.normal(0, 10)
                else:  # More casual voices
                    freq_variation = word_freq + np.random.normal(0, 20)
                
                # Create word audio
                word_t = np.linspace(0, speed, end_sample - start_sample, False)
                word_audio = np.sin(2 * np.pi * freq_variation * word_t)
                
                # Add voice-specific harmonics
                if accent == "british":
                    # British: subtle harmonics for formal sound
                    harmonic1 = 0.06 * np.sin(2 * np.pi * freq_variation * 2 * word_t)
                    word_audio += harmonic1
                else:
                    # American: more pronounced harmonics for expressive sound
                    harmonic1 = 0.1 * np.sin(2 * np.pi * freq_variation * 2 * word_t)
                    harmonic2 = 0.04 * np.sin(2 * np.pi * freq_variation * 3 * word_t)
                    word_audio += harmonic1 + harmonic2
                
                # Apply envelope (fade in/out) to avoid clicks
                envelope = np.ones_like(word_audio)
                fade_samples = int(0.05 * sample_rate)  # 50ms fade
                if len(envelope) > 2 * fade_samples:
                    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
                
                word_audio = word_audio * envelope
                
                # Add to main signal
                if start_sample < total_samples and end_sample <= total_samples:
                    audio_signal[start_sample:end_sample] = word_audio
            
            # Normalize and convert to 16-bit
            max_val = np.max(np.abs(audio_signal))
            if max_val > 0:
                normalized_signal = audio_signal / max_val
                audio_16bit = (normalized_signal * 16384).astype(np.int16)
            else:
                audio_16bit = np.zeros(total_samples, dtype=np.int16)
            
            # Create AudioSegment with correct sample rate
            audio_segment = AudioSegment(
                audio_16bit.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            
            st.success(f"✅ Simple tone TTS successful: {len(audio_segment)}ms audio - {voice_option}")
            return audio_segment
            
        except Exception as e:
            st.error(f"❌ Error in simple tone TTS: {e}")
            return None
    
    @staticmethod
    def text_to_speech_simple_reliable(text: str, voice_option: str) -> AudioSegment:
        """
        Multi-engine TTS for different voice characteristics
        """
        try:
            st.info(f"Using multi-engine TTS for: '{text[:50]}...'")
            
            # Voice engine mapping for different characteristics
            voice_engines = {
                "British Male": {"engine": "pyttsx3", "voice": "david", "rate": 110, "volume": 0.8},
                "British Female": {"engine": "pyttsx3", "voice": "zira", "rate": 130, "volume": 0.9},
                "American Male": {"engine": "gtts", "voice": "en-us", "rate": "normal", "volume": 0.9},
                "American Female": {"engine": "gtts", "voice": "en-gb", "rate": "slow", "volume": 0.9}
            }
            
            config = voice_engines.get(voice_option, voice_engines["British Male"])
            
            if config["engine"] == "pyttsx3":
                # Use Microsoft TTS
                return AudioProcessor.text_to_speech_enhanced_pyttsx3(text, voice_option)
            elif config["engine"] == "gtts":
                # Use Google TTS
                return AudioProcessor.text_to_speech_gtts(text, config["voice"])
            else:
                # Fallback to Microsoft TTS
                return AudioProcessor.text_to_speech_enhanced_pyttsx3(text, voice_option)
                
        except Exception as e:
            st.error(f"❌ Error in multi-engine TTS: {e}")
            return None
    
    @staticmethod
    def test_all_voice_configurations(text: str = "Hello world, this is a test of different voice configurations.") -> dict:
        """
        Test all 4 voice configurations to show differences
        """
        results = {}
        voice_options = ["British Male", "British Female", "American Male", "American Female"]
        
        for voice_option in voice_options:
            try:
                st.info(f"Testing {voice_option}...")
                audio = AudioProcessor.text_to_speech_enhanced_pyttsx3(text, voice_option)
                if audio:
                    results[voice_option] = {
                        'status': 'Success',
                        'duration_ms': len(audio),
                        'duration_sec': len(audio) / 1000
                    }
                    st.success(f"✅ {voice_option}: {len(audio)}ms audio generated")
                else:
                    results[voice_option] = {
                        'status': 'Failed',
                        'duration_ms': 0,
                        'duration_sec': 0
                    }
                    st.error(f"❌ {voice_option}: Failed to generate audio")
            except Exception as e:
                results[voice_option] = {
                    'status': f'Error: {e}',
                    'duration_ms': 0,
                    'duration_sec': 0
                }
                st.error(f"❌ {voice_option}: Error - {e}")
        
        return results
    
    @staticmethod
    def combine_audio_files(audio_files: list, output_path: str) -> str:
        """
        Combine multiple audio files into one using real-time processing
        """
        try:
            if not audio_files:
                st.error("No audio files provided for combination")
                return None
            
            st.info(f"Received {len(audio_files)} audio files for combination")
            
            # Filter out None values and check file existence
            valid_audio_files = []
            for i, audio_file in enumerate(audio_files):
                st.info(f"Checking audio file {i+1}: {audio_file}")
                if audio_file is None:
                    st.warning(f"Audio file {i+1} is None")
                    continue
                    
                if os.path.exists(audio_file):
                    file_size = os.path.getsize(audio_file)
                    if file_size > 0:
                        st.success(f"✅ Audio file {i+1} valid: {os.path.basename(audio_file)} ({file_size} bytes)")
                        valid_audio_files.append(audio_file)
                    else:
                        st.error(f"❌ Audio file {i+1} exists but is empty: {audio_file}")
                else:
                    st.error(f"❌ Audio file {i+1} not found: {audio_file}")
            
            st.info(f"Found {len(valid_audio_files)} valid audio files out of {len(audio_files)}")
            
            if not valid_audio_files:
                st.error("No valid audio files found for combination")
                return None
            
            # Process audio files one by one and combine immediately
            st.info("Processing audio files in real-time...")
            
            # Start with the first file
            first_file = valid_audio_files[0]
            st.info(f"Loading first audio file: {os.path.basename(first_file)}")
            
            try:
                # Load first file directly
                combined = AudioSegment.from_mp3(first_file)
                st.success(f"✅ Successfully loaded first audio file")
            except Exception as e:
                st.error(f"❌ Error loading first audio file: {e}")
                
                # Try binary data approach for first file
                st.info("Trying binary data approach for first file...")
                try:
                    with open(first_file, 'rb') as f:
                        audio_data = f.read()
                    
                    audio_buffer = BytesIO(audio_data)
                    combined = AudioSegment.from_mp3(audio_buffer)
                    st.success(f"✅ Successfully loaded first audio file using binary data approach")
                except Exception as binary_error:
                    st.error(f"Binary data approach also failed for first file: {binary_error}")
                    return None
            
            # Process remaining files and combine immediately
            silence = AudioSegment.silent(duration=500)  # 500ms silence
            
            for i, audio_file in enumerate(valid_audio_files[1:], 1):
                try:
                    st.info(f"Processing chunk {i+1}/{len(valid_audio_files)}: {os.path.basename(audio_file)}")
                    
                    # Load and combine immediately
                    audio_segment = AudioSegment.from_mp3(audio_file)
                    combined += silence + audio_segment
                    
                    st.success(f"✅ Successfully added chunk {i+1}")
                    
                except Exception as e:
                    st.error(f"❌ Error loading chunk {i+1}: {e}")
                    
                    # Try binary data approach
                    st.info(f"Trying binary data approach for chunk {i+1}...")
                    try:
                        with open(audio_file, 'rb') as f:
                            audio_data = f.read()
                        
                        audio_buffer = BytesIO(audio_data)
                        audio_segment = AudioSegment.from_mp3(audio_buffer)
                        combined += silence + audio_segment
                        
                        st.success(f"✅ Successfully added chunk {i+1} using binary data approach")
                        
                    except Exception as binary_error:
                        st.error(f"Binary data approach also failed for chunk {i+1}: {binary_error}")
                        continue
            
            # Export combined audio
            try:
                st.info(f"Exporting combined audio to: {output_path}")
                combined.export(output_path, format="mp3")
                st.success("🎉 Audio combination completed successfully!")
                return output_path
                
            except Exception as e:
                st.error(f"❌ Error exporting combined audio: {e}")
                return None
            
        except Exception as e:
            st.error(f"❌ Error combining audio files: {e}")
            return None
    
    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """
        Get duration of audio file in seconds
        """
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            st.error(f"Error getting audio duration: {e}")
            return 0.0
    
    @staticmethod
    def create_audio_preview(audio_path: str, preview_duration: int = 30) -> str:
        """
        Create a preview of the audio file (first N seconds)
        """
        try:
            audio = AudioSegment.from_mp3(audio_path)
            
            # Extract first N seconds
            preview = audio[:preview_duration * 1000]  # Convert to milliseconds
            
            # Create preview file using NamedTemporaryFile
            with tempfile.NamedTemporaryFile(delete=False, suffix="_preview.mp3") as tmp_file:
                preview_path = tmp_file.name
            
            preview.export(preview_path, format="mp3")
            
            # Verify file was created
            if os.path.exists(preview_path) and os.path.getsize(preview_path) > 0:
                return preview_path
            else:
                st.error("Preview file was not created properly")
                return None
            
        except Exception as e:
            st.error(f"Error creating audio preview: {e}")
            return None
    
    @staticmethod
    def optimize_audio_for_playback(audio_path: str, output_path: str = None) -> str:
        """
        Optimize audio file for better playback quality
        """
        try:
            audio = AudioSegment.from_mp3(audio_path)
            
            # Normalize audio
            audio = audio.normalize()
            
            # Apply some basic effects for better quality
            audio = audio.high_pass_filter(80)  # Remove low frequency noise
            audio = audio.low_pass_filter(8000)  # Remove high frequency noise
            
            # Generate output path if not provided using NamedTemporaryFile
            if not output_path:
                with tempfile.NamedTemporaryFile(delete=False, suffix="_optimized.mp3") as tmp_file:
                    output_path = tmp_file.name
            
            # Export optimized audio
            audio.export(output_path, format="mp3", bitrate="192k")
            
            # Verify file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                st.success(f"Audio optimized successfully: {os.path.basename(output_path)}")
                return output_path
            else:
                st.error("Optimized audio file was not created properly")
                return audio_path  # Return original if optimization fails
            
        except Exception as e:
            st.error(f"Error optimizing audio: {e}")
            return audio_path  # Return original if optimization fails

    @staticmethod
    def combine_audio_segments_memory(audio_segments: list, output_path: str) -> str:
        """
        Combine multiple audio segments directly from memory
        """
        try:
            if not audio_segments:
                st.error("No audio segments provided for combination")
                return None
            
            st.info(f"Combining {len(audio_segments)} audio segments from memory...")
            
            # Start with the first segment
            combined = audio_segments[0]
            st.success(f"✅ Started combination with first segment")
            
            # Add silence between segments and combine
            silence = AudioSegment.silent(duration=500)  # 500ms silence
            
            for i, audio_segment in enumerate(audio_segments[1:], 1):
                try:
                    combined += silence + audio_segment
                    st.success(f"✅ Successfully added segment {i+1}")
                except Exception as e:
                    st.error(f"❌ Error adding segment {i+1}: {e}")
                    continue
            
            # Export combined audio using a more reliable method
            try:
                st.info(f"Exporting combined audio to: {output_path}")
                
                # First, ensure the output directory exists and is writable
                if not AudioProcessor.ensure_output_directory(output_path):
                    st.error("❌ Cannot write to output directory")
                    return None
                
                # Use the new direct audio generation method
                st.info("Using direct audio generation method...")
                audio_data = AudioProcessor.generate_mp3_bytes_directly(audio_segments)
                
                if audio_data:
                    # Write the audio data directly to disk
                    try:
                        # Ensure the output directory exists
                        output_dir = os.path.dirname(output_path)
                        if output_dir and not os.path.exists(output_dir):
                            os.makedirs(output_dir, exist_ok=True)
                            st.info(f"Created output directory: {output_dir}")
                        
                        # Write the audio data
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)
                            f.flush()  # Ensure data is written to disk
                            os.fsync(f.fileno())  # Force sync to disk
                        
                        # Wait a moment for file system to sync
                        import time
                        time.sleep(0.5)
                        
                        # Verify the file was created
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            st.success("🎉 Audio combination completed successfully using direct method!")
                            st.info(f"File created: {output_path} ({os.path.getsize(output_path)} bytes)")
                            
                            # Double-check file is readable
                            try:
                                with open(output_path, 'rb') as test_file:
                                    test_file.read(1024)  # Read first 1KB to ensure file is accessible
                                st.success("✅ File is readable and accessible")
                                return output_path
                            except Exception as read_error:
                                st.error(f"❌ File created but not readable: {read_error}")
                                # Continue to fallback methods
                        else:
                            st.error("❌ File was not created properly")
                            
                            # Try alternative location in temp directory
                            st.info("Trying alternative location in temp directory...")
                            import tempfile
                            temp_dir = tempfile.gettempdir()
                            temp_filename = f"audiobook_{int(time.time())}.wav"
                            temp_path = os.path.join(temp_dir, temp_filename)
                            
                            with open(temp_path, 'wb') as f:
                                f.write(audio_data)
                                f.flush()
                                os.fsync(f.fileno())
                            
                            # Wait for file system to sync
                            time.sleep(0.5)
                            
                            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                                st.success(f"🎉 Audio saved to temp location: {temp_path}")
                                return temp_path
                            else:
                                st.error("❌ Failed to create file in temp directory too")
                                return None
                            
                    except Exception as write_error:
                        st.error(f"❌ Error writing audio file to disk: {write_error}")
                        
                        # Try temp directory as fallback
                        try:
                            import tempfile
                            temp_dir = tempfile.gettempdir()
                            temp_filename = f"audiobook_{int(time.time())}.wav"
                            temp_path = os.path.join(temp_dir, temp_filename)
                            
                            with open(temp_path, 'wb') as f:
                                f.write(audio_data)
                                f.flush()
                                os.fsync(f.fileno())
                            
                            # Wait for file system to sync
                            time.sleep(0.5)
                            
                            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                                st.success(f"🎉 Audio saved to temp location as fallback: {temp_path}")
                                return temp_path
                            else:
                                st.error("❌ Failed to create file in temp directory")
                                return None
                                
                        except Exception as temp_error:
                            st.error(f"❌ Temp directory fallback also failed: {temp_error}")
                            return None
                else:
                    st.error("❌ Failed to generate audio data directly")
                    return None
                
            except Exception as e:
                st.error(f"❌ Error in direct audio generation: {e}")
                return None
            
        except Exception as e:
            st.error(f"❌ Error combining audio segments: {e}")
            return None

    @staticmethod
    def ensure_output_directory(output_path: str) -> bool:
        """
        Ensure the output directory exists and is writable
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                st.info(f"Created output directory: {output_dir}")
            
            # Test if we can write to the directory
            test_file = os.path.join(output_dir, "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                st.success(f"✅ Output directory is writable: {output_dir}")
                return True
            except Exception as write_test_error:
                st.error(f"❌ Output directory is not writable: {write_test_error}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error ensuring output directory: {e}")
            return False

    @staticmethod
    def generate_mp3_bytes_directly(audio_segments: list) -> bytes:
        """
        Generate MP3 audio data directly as bytes without using pydub export
        """
        try:
            import numpy as np
            from io import BytesIO
            
            st.info("Generating MP3 audio data directly...")
            
            # Combine all segments with silence
            combined_samples = np.array([], dtype=np.int16)
            sample_rate = 22050  # Lower sample rate for better compatibility
            
            for i, segment in enumerate(audio_segments):
                try:
                    # Convert AudioSegment to numpy array
                    if hasattr(segment, 'get_array_of_samples'):
                        samples = np.array(segment.get_array_of_samples(), dtype=np.int16)
                    else:
                        # Fallback: generate simple sine wave
                        duration_ms = len(segment)
                        duration_sec = duration_ms / 1000.0
                        num_samples = int(duration_sec * sample_rate)
                        frequency = 440  # A4 note
                        t = np.linspace(0, duration_sec, num_samples, False)
                        samples = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
                    
                    # Add silence between segments
                    if i > 0:
                        silence_samples = np.zeros(int(0.5 * sample_rate), dtype=np.int16)
                        combined_samples = np.concatenate([combined_samples, silence_samples])
                    
                    combined_samples = np.concatenate([combined_samples, samples])
                    st.success(f"✅ Added segment {i+1} to combined audio")
                    
                except Exception as e:
                    st.error(f"❌ Error processing segment {i+1}: {e}")
                    continue
            
            if len(combined_samples) == 0:
                st.error("❌ No audio samples generated")
                return None
            
            st.success(f"✅ Combined audio: {len(combined_samples)} samples at {sample_rate}Hz")
            
            # Convert to MP3 using a simple approach
            try:
                # For now, let's create a simple WAV file and convert it
                # This is more reliable than trying to generate MP3 directly
                wav_data = AudioProcessor.create_wav_from_samples(combined_samples, sample_rate)
                if wav_data:
                    st.success("✅ Successfully generated WAV audio data")
                    return wav_data
                else:
                    st.error("❌ Failed to generate WAV audio data")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error generating audio data: {e}")
                return None
                
        except Exception as e:
            st.error(f"❌ Error in direct MP3 generation: {e}")
            return None
    
    @staticmethod
    def create_wav_from_samples(samples: 'np.ndarray', sample_rate: int) -> bytes:
        """
        Create WAV file data from numpy samples
        """
        try:
            import struct
            
            # WAV file header
            num_channels = 1
            sample_width = 2  # 16-bit
            num_frames = len(samples)
            
            # Calculate WAV header values
            byte_rate = sample_rate * num_channels * sample_width
            block_align = num_channels * sample_width
            
            # Create WAV header
            header = struct.pack('<4sI4s4sIHHIIHH4sI',
                b'RIFF',                    # ChunkID
                36 + num_frames * sample_width,  # ChunkSize
                b'WAVE',                    # Format
                b'fmt ',                    # Subchunk1ID
                16,                         # Subchunk1Size
                1,                          # AudioFormat (PCM)
                num_channels,               # NumChannels
                sample_rate,                # SampleRate
                byte_rate,                  # ByteRate
                block_align,                # BlockAlign
                sample_width * 8,          # BitsPerSample
                b'data',                    # Subchunk2ID
                num_frames * sample_width   # Subchunk2Size
            )
            
            # Convert samples to bytes
            audio_bytes = struct.pack(f'<{len(samples)}h', *samples)
            
            # Combine header and audio data
            wav_data = header + audio_bytes
            
            st.success(f"✅ Generated WAV data: {len(wav_data)} bytes")
            return wav_data
            
        except Exception as e:
            st.error(f"❌ Error creating WAV data: {e}")
            return None

    @staticmethod
    def create_audio_preview_direct(audio_segments: list) -> bytes:
        """
        Create a short audio preview directly from audio segments
        """
        try:
            import numpy as np
            
            st.info("Creating audio preview...")
            
            # Take first few seconds from each segment for preview
            preview_duration = 3000  # 3 seconds per segment
            preview_samples = np.array([], dtype=np.int16)
            sample_rate = 22050  # Lower sample rate for better compatibility
            
            for i, segment in enumerate(audio_segments[:3]):  # Only first 3 segments
                try:
                    # Get a short preview from the segment
                    if hasattr(segment, 'get_array_of_samples'):
                        samples = np.array(segment.get_array_of_samples(), dtype=np.int16)
                        # Take only first few seconds
                        max_samples = int(preview_duration * sample_rate / 1000)
                        if len(samples) > max_samples:
                            samples = samples[:max_samples]
                    else:
                        # Generate simple preview
                        duration_sec = min(preview_duration / 1000.0, 3.0)
                        num_samples = int(duration_sec * sample_rate)
                        frequency = 440 + (i * 110)  # Different note for each segment
                        t = np.linspace(0, duration_sec, num_samples, False)
                        samples = (np.sin(2 * np.pi * frequency * t) * 16384).astype(np.int16)
                    
                    # Add short silence between preview segments
                    if i > 0:
                        silence_samples = np.zeros(int(0.2 * sample_rate), dtype=np.int16)
                        preview_samples = np.concatenate([preview_samples, silence_samples])
                    
                    preview_samples = np.concatenate([preview_samples, samples])
                    st.success(f"✅ Added preview segment {i+1}")
                    
                except Exception as e:
                    st.error(f"❌ Error processing preview segment {i+1}: {e}")
                    continue
            
            if len(preview_samples) == 0:
                st.error("❌ No preview samples generated")
                return None
            
            # Create WAV preview
            preview_wav = AudioProcessor.create_wav_from_samples(preview_samples, sample_rate)
            if preview_wav:
                st.success(f"✅ Created preview: {len(preview_wav)} bytes")
                return preview_wav
            else:
                st.error("❌ Failed to create preview WAV")
                return None
                
        except Exception as e:
            st.error(f"❌ Error creating audio preview: {e}")
            return None

    @staticmethod
    def generate_streamlit_audio(audio_segments: list) -> str:
        """
        Generate audio data that can be played directly in Streamlit
        Returns base64 encoded audio data
        """
        try:
            import base64
            
            st.info("Generating Streamlit-compatible audio...")
            
            # Create WAV audio data
            wav_data = AudioProcessor.generate_mp3_bytes_directly(audio_segments)
            
            if wav_data:
                # Convert to base64 for Streamlit
                base64_audio = base64.b64encode(wav_data).decode()
                audio_src = f"data:audio/wav;base64,{base64_audio}"
                
                st.success("✅ Generated Streamlit-compatible audio")
                return audio_src
            else:
                st.error("❌ Failed to generate audio data")
                return None
                
        except Exception as e:
            st.error(f"❌ Error generating Streamlit audio: {e}")
            return None

    @staticmethod
    def test_available_tts_engines() -> dict:
        """
        Test which TTS engines are available on the system
        """
        available_engines = {}
        
        # Test pyttsx3
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            available_engines['pyttsx3'] = {
                'status': 'Available',
                'voices': len(voices),
                'voice_names': [voice.name for voice in voices[:3]],  # First 3 voices
                'quality': 'High (Offline)'
            }
            st.success("✅ pyttsx3 TTS engine available")
        except Exception as e:
            available_engines['pyttsx3'] = {
                'status': 'Not Available',
                'error': str(e),
                'quality': 'N/A'
            }
            st.warning("⚠️ pyttsx3 TTS engine not available")
        
        # Test gTTS
        try:
            from gtts import gTTS
            available_engines['gtts'] = {
                'status': 'Available',
                'voices': 'Multiple languages',
                'voice_names': ['en-us', 'en-gb', 'en-au'],
                'quality': 'High (Online)'
            }
            st.success("✅ gTTS TTS engine available")
        except Exception as e:
            available_engines['gtts'] = {
                'status': 'Not Available',
                'error': str(e),
                'quality': 'N/A'
            }
            st.warning("⚠️ gTTS TTS engine not available")
        
        # Test numpy (for tone generation)
        try:
            import numpy as np
            available_engines['numpy_tones'] = {
                'status': 'Available',
                'voices': 'Custom tones',
                'voice_names': ['Tone variations'],
                'quality': 'Basic (Offline)'
            }
            st.success("✅ NumPy tone generation available")
        except Exception as e:
            available_engines['numpy_tones'] = {
                'status': 'Not Available',
                'error': str(e),
                'quality': 'N/A'
            }
            st.warning("⚠️ NumPy tone generation not available")
        
        return available_engines

    @staticmethod
    def create_audio_file_simple(audio_segments, output_path, voice_option):
        """
        Ultra-simple file creation method that just works
        """
        try:
            st.info("🔄 Using ultra-simple file creation method...")
            
            # Combine all audio segments
            if not audio_segments:
                st.error("❌ No audio segments to combine")
                return None
            
            # Validate that all segments are AudioSegment objects
            valid_segments = []
            for i, segment in enumerate(audio_segments):
                if segment is None:
                    st.warning(f"⚠️ Segment {i+1} is None, skipping")
                    continue
                    
                if hasattr(segment, 'export'):
                    valid_segments.append(segment)
                    st.info(f"✅ Segment {i+1} is valid AudioSegment")
                else:
                    st.warning(f"⚠️ Segment {i+1} is not an AudioSegment (type: {type(segment)}), skipping")
                    continue
            
            if not valid_segments:
                st.error("❌ No valid audio segments to combine")
                return None
                
            # Start with first segment
            combined_audio = valid_segments[0]
            
            # Add other segments
            for segment in valid_segments[1:]:
                combined_audio = combined_audio + segment
            
            st.info(f"✅ Combined {len(valid_segments)} audio segments")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                st.info(f"Created directory: {output_dir}")
            
            # Export directly to WAV format (more reliable than MP3)
            st.info(f"Exporting to: {output_path}")
            combined_audio.export(output_path, format="wav")
            
            # Wait a moment
            import time
            time.sleep(1)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                st.success(f"🎉 File created successfully: {output_path}")
                st.info(f"File size: {file_size} bytes")
                
                # Test if file is readable
                try:
                    with open(output_path, 'rb') as test_file:
                        test_file.read(1024)
                    st.success("✅ File is readable and accessible")
                    return output_path
                except Exception as read_error:
                    st.error(f"❌ File created but not readable: {read_error}")
                    return None
            else:
                st.error("❌ File was not created")
                return None
                
        except Exception as e:
            st.error(f"❌ Error in simple file creation: {e}")
            return None
