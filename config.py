import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base Directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Data Directory
    DATA_DIR = BASE_DIR / 'data'
    
    # Flask Configuration
    # SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key') # enable this if later on session is needed
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Vector Store and Document Storage
    VECTOR_STORE_DIR = DATA_DIR / 'vector_store'
    DOCUMENT_DIR = DATA_DIR / 'documents'
    TEMP_DIR = DATA_DIR / 'temp'
    
    # Database
    DATABASE_PATH = DATA_DIR / 'chat.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Audio Configuration
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS = DATA_DIR / 'google_credentials.json'
    
    # Speech Recognition Configuration
    SPEECH_RECOGNITION_CONFIG = {
        'encoding': 'LINEAR16',
        'sample_rate_hertz': SAMPLE_RATE,
        'language_code': 'en-US',
        'enable_automatic_punctuation': True
    }
    
    # Ensure directories exist
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        for directory in [cls.DATA_DIR, cls.VECTOR_STORE_DIR, cls.DOCUMENT_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'

# Create directories on module import
Config.create_directories()

