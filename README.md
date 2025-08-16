# AI-Powered Productivity Suite

This application is a Streamlit-based suite offering multiple AI-powered tools to enhance productivity and creativity.

## Features

### 1. PDF to Audiobook Converter
Convert your PDF documents into audiobooks, allowing you to listen to your documents on the go.

### 2. Persona Search
(Details to be added based on implementation)

### 3. Storybook Generator
(Details to be added based on implementation)

## Installation and Setup

To run this application, you need Python and several libraries. Additionally, for the PDF to Audiobook Converter to function correctly, **FFmpeg is a critical dependency**.

### Prerequisites

*   Python 3.x
*   `pip` (Python package installer)
*   **FFmpeg** (Crucial for audio processing in the PDF to Audiobook Converter)

### Step-by-Step Installation

1.  **Clone the repository (if you haven't already):**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Python dependencies:**

    It is highly recommended to use a virtual environment.

    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # On Windows
    # source venv/bin/activate # On macOS/Linux
    
    pip install -r requirements.txt
    ```
    (Note: You might need to create a `requirements.txt` file if one doesn't exist, by running `pip freeze > requirements.txt` after installing all necessary packages like `streamlit`, `PyPDF2`, `gTTS`, `pydub`, etc.)

3.  **Install FFmpeg (Crucial for Audio Conversion):**

    The PDF to Audiobook Converter relies on `pydub`, which in turn requires `ffmpeg` for audio processing. Without `ffmpeg` installed and correctly configured in your system's PATH, the audio conversion will fail with errors like "WinError 2: The system cannot find the file specified."

    **For Windows Users:**

    a.  **Download `ffmpeg`**: Go to the official `ffmpeg` website: <mcurl name="https://ffmpeg.org/download.html" url="https://ffmpeg.org/download.html"></mcurl>. Download the latest stable build for Windows.
    b.  **Extract `ffmpeg`**: Unzip the downloaded file to a simple, easy-to-remember location, for example, `C:\ffmpeg`.
    c.  **Add `ffmpeg` to System PATH**: This is the most crucial step. You need to tell your operating system where to find the `ffmpeg` executable.
        *   Search for "Environment Variables" in the Windows search bar and select "Edit the system environment variables."
        *   In the System Properties window, click on the "Environment Variables..." button.
        *   Under the "System variables" section, find the variable named `Path` and select it. Then click "Edit...".
        *   In the "Edit environment variable" window, click "New" and add the full path to the `bin` folder inside your `ffmpeg` installation (e.g., `C:\ffmpeg\bin`).
        *   Click "OK" on all open windows to save the changes.
    d.  **Verify Installation**: Open a **NEW** Command Prompt or PowerShell window (it's important to open a new one after modifying PATH) and type `ffmpeg -version`. If `ffmpeg` is correctly installed and added to your PATH, you should see its version information. If you get an error like "'ffmpeg' is not recognized," then it's not correctly added to your PATH.

    **For macOS/Linux Users:**

    You can typically install `ffmpeg` using your package manager:

    *   **macOS (using Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    *   **Linux (Debian/Ubuntu):**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```

### Running the Application

Once all dependencies are installed and `ffmpeg` is correctly set up, you can run the Streamlit application:

```bash
streamlit run main.py
```

This will open the application in your web browser, typically at `http://localhost:8501`.

### Screenshots

#### Application Homepage

![Screenshot of Application Homepage](screenshots/home.png)

#### PDF to Audiobook Converter in Action

![Screenshot of PDF to Audiobook Converter](screenshots/audiobook.png)

#### PDF to Audiobook Converter Result

![Screenshot of PDF to Audiobook Converter Result](screenshots/audiobook_result.png)

#### Persona Search Interface

![Screenshot of Persona Search](screenshots/nlp.png)

#### Persona Search Result

![Screenshot of Persona Search Result](screenshots/nlp_result.png)

#### Storybook Generator Output

![Screenshot of Storybook Generator](screenshots/storybook.png)

#### Storybook Generator Result

![Screenshot of Storybook Generator Result](screenshots/storybook_result.png)

A comprehensive Python application that converts PDF documents into high-quality audiobooks with multiple voice options. This tool supports 4 different voices (British/American, Male/Female) and multiple text-to-speech engines for reliable audio generation.

## 🎯 Features

### Core Functionality
- **PDF Text Extraction**: Reliable text extraction using multiple methods (pdfplumber + PyPDF2)
- **Multiple Voice Options**: 4 distinct voices with different characteristics
  - British Male: Deep, authoritative, formal (120Hz base frequency)
  - British Female: Clear, professional, engaging (280Hz base frequency)
  - American Male: Natural, conversational, warm (140Hz base frequency)
  - American Female: Friendly, expressive, easy to follow (320Hz base frequency)

### TTS Engines
- **Simple Reliable (Always Works)**: Custom tone generation with voice differentiation
- **pyttsx3 (Offline)**: High-quality offline TTS using system voices
- **gTTS (Online)**: Google's high-quality online TTS service
- **Tone Generation (Basic)**: Basic but reliable offline tone generation

### Audio Features
- **Multiple Formats**: WAV (recommended) and MP3 output
- **Chunk Processing**: Intelligent text segmentation for optimal audio quality
- **Error Handling**: Comprehensive fallback mechanisms
- **File Management**: Automatic output directory creation and file naming

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aiml-llm
   ```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download NLTK data** (required for text processing):
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

### Basic Usage

#### Command Line Interface

```bash
# Convert a PDF with default settings (British Male voice, WAV format)
python demo.py document.pdf

# Convert with specific voice and format
python demo.py document.pdf --voice "American Female" --format mp3

# Test voice differences
python demo.py --test-voices

# Test TTS methods
python demo.py --test-tts

# Show all available options
python demo.py --show-options
```

#### Streamlit Web Interface

```bash
# Run the web interface
streamlit run pdf_to_audio.py
```

Then open your browser to `http://localhost:8501` and use the interactive interface.

## 📖 Detailed Usage

### Voice Options

| Voice | Characteristics | Base Frequency | Speed | Accent |
|-------|----------------|----------------|-------|--------|
| British Male | Deep, authoritative, formal | 120Hz | 200ms/char | British |
| British Female | Clear, professional, engaging | 280Hz | 180ms/char | British |
| American Male | Natural, conversational, warm | 140Hz | 160ms/char | American |
| American Female | Friendly, expressive, easy to follow | 320Hz | 140ms/char | American |

### TTS Methods Comparison

| Method | Quality | Internet Required | Voice Differentiation | Reliability |
|--------|---------|-------------------|----------------------|-------------|
| Simple Reliable | Good | No | Excellent | Very High |
| pyttsx3 | High | No | Good | High |
| gTTS | Very High | Yes | Good | High |
| Tone Generation | Basic | No | Good | Very High |

### Advanced Options

```bash
# Custom chunk size for processing
python demo.py document.pdf --chunk-size 300

# Use specific TTS method
python demo.py document.pdf --tts "pyttsx3 (Offline)"

# Combine multiple options
python demo.py document.pdf --voice "American Female" --tts "gTTS (Online)" --format mp3 --chunk-size 400
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test the converter with a sample PDF
python test_pdf_converter.py
```

This will:
- Create a test PDF with sample text
- Test all voice options
- Test all TTS methods
- Perform full conversion tests
- Generate sample audio files in the `outputs/` directory

## 📁 Project Structure

```
aiml-llm/
├── demo.py                    # Main command-line interface
├── pdf_to_audio.py           # Streamlit web interface
├── test_pdf_converter.py     # Test suite
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── utils/
│   ├── __init__.py
│   ├── text_processing.py   # PDF text extraction and processing
│   └── audio_utils.py       # TTS and audio processing
└── outputs/                 # Generated audio files
```

## 🔧 Technical Details

### Text Processing Pipeline

1. **PDF Parsing**: Uses both `pdfplumber` and `PyPDF2` for maximum text extraction
2. **Text Cleaning**: Removes formatting issues and optimizes for TTS
3. **Segmentation**: Splits text into optimal chunks for natural speech
4. **Audio Generation**: Converts text chunks to audio using selected TTS method
5. **Audio Combination**: Merges audio segments with silence between chunks
6. **File Export**: Saves final audio in WAV or MP3 format

### Audio Processing

- **Sample Rate**: 22050Hz for optimal compatibility
- **Bit Depth**: 16-bit for high quality
- **Channels**: Mono for consistent playback
- **Silence**: 500ms between text chunks for natural pacing

### Error Handling

- **Text Extraction**: Multiple fallback methods for PDF parsing
- **TTS Failures**: Automatic fallback to Simple Reliable method
- **File I/O**: Comprehensive error checking and recovery
- **Memory Management**: Efficient processing of large documents

## 🎵 Voice Characteristics

### British Voices
- **Formal and Clear**: More structured pronunciation
- **Subtle Harmonics**: Richer, more sophisticated sound
- **Slower Pace**: More deliberate speech patterns

### American Voices
- **Natural and Expressive**: Conversational tone
- **Pronounced Harmonics**: More dynamic sound variation
- **Faster Pace**: More natural speech flow

## 🛠️ Customization

### Adding New Voices

To add custom voices, modify the `VOICE_OPTIONS` in `utils/audio_utils.py`:

```python
VOICE_OPTIONS = {
    "British Male": {"lang": "en-gb", "voice": "male"},
    "British Female": {"lang": "en-gb", "voice": "female"},
    "American Male": {"lang": "en-us", "voice": "male"},
    "American Female": {"lang": "en-us", "voice": "female"},
    "Custom Voice": {"lang": "en-us", "voice": "custom"}  # Add your voice
}
```

### Custom TTS Methods

Add new TTS methods in `utils/audio_utils.py`:

```python
@staticmethod
def text_to_speech_custom(text: str, voice_option: str) -> AudioSegment:
    """Your custom TTS implementation"""
    # Your implementation here
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'nltk'"**
   ```bash
   pip install nltk
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

2. **"pyttsx3 not working"**
   - On Windows: Install Microsoft Speech API
   - On Linux: Install `espeak` or `festival`
   - On macOS: Use system voices

3. **"gTTS requires internet"**
   - Ensure internet connection
   - Use offline methods (pyttsx3 or Simple Reliable)

4. **"PDF text extraction failed"**
   - Try a different PDF (some scanned PDFs may not work)
   - Check if PDF is password-protected
   - Ensure PDF contains actual text (not just images)

### Performance Tips

- **Chunk Size**: Smaller chunks (200-300 chars) for better quality, larger chunks (500-800 chars) for speed
- **TTS Method**: Use "Simple Reliable" for best voice differentiation
- **Output Format**: WAV for reliability, MP3 for smaller file size
- **Memory**: Large PDFs may require more RAM

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Run the test suite: `python test_pdf_converter.py`
3. Open an issue on the repository

## 🎉 Acknowledgments

- **pdfplumber** and **PyPDF2** for PDF text extraction
- **pyttsx3** and **gTTS** for text-to-speech capabilities
- **pydub** for audio processing
- **NLTK** for text processing utilities

---

**Happy converting! 🎵📚**
