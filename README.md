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
├── config.py                 # Configuration settings
└── requirements.txt          # Python dependencies
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

5. **Initialize the Application**
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
- SQLite database for chat history
- File-based storage for documents
- Vector store for embeddings

## Dependencies

- Flask: Web framework
- ChromaDB: Vector database
- Google Cloud Services: Speech-to-Text, Text-to-Speech
- Gemini: Language model for chat
- PyPDF2: PDF processing
- SQLAlchemy: Database ORM

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details. 