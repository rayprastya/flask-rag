import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base Directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Flask Configuration
    # SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key') # enable this if later on session is needed
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Vector Store and Document Storage
    VECTOR_STORE_DIR = os.path.join(BASE_DIR, 'data', 'vector_store')
    DOCUMENT_DIR = os.path.join(BASE_DIR, 'data', 'documents')
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Audio Configuration
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    # Ensure directories exist
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        os.makedirs(cls.VECTOR_STORE_DIR, exist_ok=True)
        os.makedirs(cls.DOCUMENT_DIR, exist_ok=True)

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

