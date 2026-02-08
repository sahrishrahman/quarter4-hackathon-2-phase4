from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum
from sqlalchemy import Text, JSON, Enum as SQLEnum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class MessageBase(SQLModel):
    conversation_id: str = Field(index=True)  # Foreign key linking to conversation
    user_id: str = Field(index=True)  # Foreign key linking to user (for additional isolation)
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole)))  # Role of message sender
    content: str = Field(sa_column=Column(Text))  # The actual message content
    message_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Additional data (e.g., tool calls)


class Message(MessageBase, table=True):
    """
    Represents individual chat messages (user or AI responses) within a conversation, including timestamp and role.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"