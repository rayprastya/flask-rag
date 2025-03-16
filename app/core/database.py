from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

# Create the engine
db_path = os.path.join(Config.BASE_DIR, 'data', 'chat.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create session factory
Session = sessionmaker(bind=engine)

# Create base class for declarative models
Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    file_context = Column(String, nullable=True)  # Path to associated file
    collection_name = Column(String, nullable=True)  # ChromaDB collection name
    
    # Relationship with messages
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    timestamp = Column(DateTime, default=datetime.now)
    context = Column(JSON, nullable=True)  # For storing metadata, sources, etc.
    
    # Relationship with room
    room = relationship("Room", back_populates="messages")

# Create all tables
Base.metadata.create_all(engine)