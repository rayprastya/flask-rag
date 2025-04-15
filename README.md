# Flask RAG Chat Application

A Flask-based chat application that combines Retrieval-Augmented Generation (RAG) with voice interaction capabilities. This application allows users to have context-aware conversations with documents and provides speech analysis features.

## Features

- 📚 **Document-based Chat**: Upload documents and chat with AI about their contents
- 🔍 **Smart Retrieval**: Uses ChromaDB for efficient document retrieval
- 🎙️ **Voice Interaction**: Support for voice input with speech analysis
- 📊 **Speech Metrics**: 
  - Pronunciation accuracy
  - Fluency scoring
  - Speech completeness
  - Word-level evaluation
  - Pitch analysis
- 💬 **Multi-Room Support**: Create multiple chat rooms for different contexts
- 🤖 **Dual Chat Modes**: 
  - RAG mode for document-based conversations
  - Regular chat mode with Gemini for general conversations
- 🔊 **Audio Feedback**: Get spoken responses from the AI
- 📈 **Real-time Analysis**: Instant feedback on speech quality

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # Windows
  # Download from https://ffmpeg.org/download.html
  ```
- Google Cloud account with:
  - Speech-to-Text API enabled
  - Text-to-Speech API enabled
  - Generative AI API enabled

## Project Structure

```
flask-rag/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── chat_room.py      # Chat room management
│   │   ├── database.py       # Database models
│   │   ├── file_extractor.py # Document processing
│   │   ├── intonation.py     # Speech analysis
│   │   ├── pronounce_assessment_mic.py
│   │   ├── rag.py           # RAG implementation
│   │   ├── stt.py           # Speech-to-text
│   │   └── tts.py           # Text-to-speech
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── index.html        # Main application interface
├── data/
│   ├── documents/           # Uploaded PDF documents
│   ├── vector_store/       # ChromaDB vector store
│   ├── temp/              # Temporary files
│   └── chat.db            # SQLite database
├── tests/                 # Unit tests
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/rayprastya/flask-rag.git
   cd flask-rag
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   Create a `.env` file in the root directory with:
   ```
   GOOGLE_API_KEY=your_google_api_key
   FLASK_DEBUG=True
   ```

5. **Create Required Directories**
   ```bash
   mkdir -p data/documents data/vector_store data/temp
   ```

6. **Initialize the Application**
   ```bash
   python app.py
   ```

## Usage

1. **Creating a Chat Room**
   - Click "New Chat" to create a room
   - Optionally upload a document during creation
   - Each room maintains its own conversation history

2. **Document Upload**
   - Supported format: PDF
   - Documents are processed and indexed for retrieval
   - Each room can have its own document context
   - Documents are stored in `data/documents/`

3. **Chat Interactions**
   - Type or use voice input for questions
   - The system provides:
     - Document-based answers (if documents are uploaded)
     - General responses (without documents)
     - Speech analysis (for voice input)
   - Responses include:
     - Brief answer to your question
     - Speech analysis metrics
     - Word-level pronunciation feedback
     - Audio response (optional)

4. **Voice Features**
   - Click the microphone icon to start voice input
   - Speak clearly into your microphone
   - Receive detailed speech metrics including:
     - Accuracy score
     - Fluency score
     - Pronunciation accuracy
     - Word-by-word analysis
     - Pitch analysis
   - Get AI-generated pronunciation feedback
   - Listen to the AI's spoken response

## API Documentation

### Endpoints

- `POST /api/rooms` - Create a new chat room
- `GET /api/rooms` - List all chat rooms
- `GET /api/rooms/<room_id>` - Get room details
- `DELETE /api/rooms/<room_id>` - Delete a chat room
- `POST /api/rooms/<room_id>/chat` - Send a text message
- `POST /api/rooms/<room_id>/voice_chat` - Send a voice message
- `POST /api/rooms/<room_id>/upload` - Upload a document

### Response Format

```json
{
    "transcription": "User's spoken text",
    "content": "AI's response",
    "role": "assistant",
    "timestamp": "2024-03-21T10:00:00",
    "context": {
        "passages": ["relevant document excerpts"],
        "metadata": {"source": "document_name"}
    },
    "speech_metrics": {
        "accuracy": 95.5,
        "completeness": 98.2,
        "fluency": 92.3,
        "pronunciation_accuracy": 96.7,
        "speech_quality": 95.4,
        "word_evaluation": ["word analysis details"],
        "pitch_analysis": ["pitch details"],
        "overall_pitch": 120.5
    },
    "response_audio": "base64_encoded_audio"
}
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions with docstrings

### Deployment
1. Set up a production server (e.g., Gunicorn)
2. Configure environment variables
3. Set up SSL certificate
4. Configure reverse proxy (e.g., Nginx)

## Troubleshooting

### Common Issues

1. **Audio Processing Errors**
   - Ensure FFmpeg is installed and in PATH
   - Check microphone permissions
   - Verify audio device selection

2. **Document Processing Issues**
   - Ensure PDF files are not corrupted
   - Check file permissions
   - Verify sufficient disk space

3. **API Connection Problems**
   - Verify Google API key
   - Check internet connection
   - Ensure API quotas are not exceeded

### Logs
- Application logs are stored in `logs/app.log`
- Error logs are stored in `logs/error.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Platform for speech and AI services
- ChromaDB for vector storage
- Flask for the web framework
- All contributors and users of this project 