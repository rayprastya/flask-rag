from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from .database import Session, Room, Message
from sqlalchemy import desc
import re

class ChatManager:
    def __init__(self, path: str):
        self.path = path
        self.session = Session()

    def create_room(self, name: str, file_context: str = None, collection_name: str = None) -> Room:
        """Create a new chat room"""
        room = Room(
            name=name,
            file_context=file_context,
            collection_name=collection_name,
            created_at=datetime.now()
        )
        self.session.add(room)
        self.session.commit()
        return room

    def get_room(self, room_id: int) -> Optional[Room]:
        """Get a chat room by ID"""
        return self.session.query(Room).get(room_id)

    def add_message(self, room_id: int, content: str, role: str, context: Dict = None) -> Message:
        """Add a message to a chat room"""
        room = self.get_room(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        message = Message(
            room_id=room_id,
            content=content,
            role=role,
            timestamp=datetime.now(),
            context=context
        )
        self.session.add(message)
        self.session.commit()
        return message

    def get_room_history(self, room_id: int, limit: int = None, 
                        hours: int = None, relevance_threshold: float = 0.7) -> List[Message]:
        """Get message history for a room with advanced filtering.
        
        Args:
            room_id: The room ID
            limit: Maximum number of messages to return
            hours: Only return messages from the last N hours
            relevance_threshold: Minimum relevance score for context messages
            
        Returns:
            List of messages ordered by timestamp
        """
        query = self.session.query(Message).filter(Message.room_id == room_id)
        
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            query = query.filter(Message.timestamp >= cutoff)
            
        # Order by timestamp
        query = query.order_by(Message.timestamp)
        
        # Get all messages that match the criteria
        messages = query.all()
        
        if not messages:
            return []
            
        # If we have a limit, select messages intelligently
        if limit and len(messages) > limit:
            # Always include the most recent message
            latest_msg = messages[-1]
            
            # Filter remaining messages by relevance
            relevant_msgs = []
            for msg in messages[:-1]:
                # Check if message has context with relevance score
                if msg.context and 'metadata' in msg.context:
                    for meta in msg.context['metadata']:
                        if meta.get('relevance_score', 0) >= relevance_threshold:
                            relevant_msgs.append(msg)
                            break
                
            # Add messages with high relevance scores
            result = relevant_msgs[-limit+1:] + [latest_msg]
            return sorted(result, key=lambda x: x.timestamp)
            
        return messages

    def get_relevant_context(self, room_id: int, query: str, limit: int = 5) -> List[Message]:
        """Get messages most relevant to the current query.
        
        Args:
            room_id: The room ID
            query: The current user query
            limit: Maximum number of context messages to return
            
        Returns:
            List of most relevant messages
        """
        # Get all messages for the room
        messages = self.get_room_history(room_id)
        
        if not messages:
            return []
            
        # Score messages based on simple keyword matching
        scored_messages = []
        query_words = set(re.findall(r'\w+', query.lower()))
        
        for msg in messages:
            # Skip system messages
            if msg.role == 'system':
                continue
                
            # Score based on word overlap
            msg_words = set(re.findall(r'\w+', msg.content.lower()))
            overlap = len(query_words & msg_words)
            if overlap > 0:
                score = overlap / len(query_words)
                scored_messages.append((score, msg))
                
        # Sort by score and return top messages
        scored_messages.sort(reverse=True, key=lambda x: x[0])
        return [msg for score, msg in scored_messages[:limit]]

    def list_rooms(self) -> List[Room]:
        """Get all chat rooms"""
        return self.session.query(Room).order_by(desc(Room.created_at)).all()

    def delete_room(self, room_id: int) -> bool:
        """Delete a chat room and all its messages"""
        room = self.get_room(room_id)
        if room:
            self.session.delete(room)
            self.session.commit()
            return True
        return False

    def update_room(self, room_id: int, **kwargs) -> Optional[Room]:
        """Update room properties"""
        room = self.get_room(room_id)
        if room:
            for key, value in kwargs.items():
                if hasattr(room, key):
                    setattr(room, key, value)
            self.session.commit()
            return room
        return None

    def __del__(self):
        """Close the session when the manager is destroyed"""
        self.session.close() 