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
   mkdir -p data/documents data/vector_store
   ```

6. **Initialize the Application**
   ```bash
   python app.py
   ```

## Usage

1. **Creating a Chat Room**
   - Click "New Chat" to create a room
   - Optionally upload a document during creation

2. **Document Upload**
   - Supported format: PDF
   - Documents are processed and indexed for retrieval
   - Each room can have its own document context

3. **Chat Interactions**
   - Type or use voice input for questions
   - The system provides:
     - Document-based answers (if documents are uploaded)
     - General responses (without documents)
     - Speech analysis (for voice input)

4. **Voice Features**
   - Click the microphone icon to start voice input
   - Receive detailed speech metrics
   - Get AI-generated pronunciation feedback

## API Documentation

### Endpoints

- `POST /api/rooms` - Create a new chat room
- `GET /api/rooms` - List all chat rooms
- `GET /api/rooms/<room_id>` - Get room details
- `DELETE /api/rooms/<room_id>` - Delete a chat room
- `POST /api/rooms/<room_id>/chat` - Send a text message
- `POST /api/rooms/<room_id>/voice_chat` - Send a voice message
- `POST /api/rooms/<room_id>/upload` - Upload a document

## Technical Details

### RAG Implementation
- Uses ChromaDB for vector storage
- Implements semantic chunking for better context
- Optimized retrieval with relevance scoring

### Speech Processing
- Google Cloud Speech-to-Text for transcription
- Custom pronunciation assessment
- Real-time pitch analysis
- Word-level evaluation

### Data Storage
- SQLite database for chat history (located at `data/chat.db`)
- File-based storage for documents (in `data/documents/`)
- Vector store for embeddings (in `data/vector_store/`)

## Dependencies

- Flask: Web framework
- ChromaDB: Vector database
- Google Cloud Services: Speech-to-Text, Text-to-Speech
- Gemini: Language model for chat
- PyPDF2: PDF processing
- SQLAlchemy: Database ORM
- FFmpeg: Audio processing
- Python-magic: File type validation
- Requests: HTTP client
- Pytest: Testing framework

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13.1+
- Edge 80+

## Troubleshooting

1. **Microphone Access Issues**
   - Ensure browser has microphone permissions
   - Check system microphone settings
   - Try using a different browser

2. **Document Upload Failures**
   - Verify PDF file is not corrupted
   - Check file size (max 10MB)
   - Ensure proper file permissions

3. **Speech Recognition Errors**
   - Check internet connection
   - Verify Google API key is valid
   - Ensure FFmpeg is installed

4. **Database Issues**
   - Check write permissions in data directory
   - Verify SQLite is properly installed
   - Try clearing browser cache

## Development

1. **Running Tests**
   ```bash
   pytest tests/
   ```

2. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Document functions and classes

3. **Adding Features**
   - Create feature branch
   - Write tests
   - Update documentation
   - Submit pull request

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details. 