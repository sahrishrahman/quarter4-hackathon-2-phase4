from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
import uuid


class ConversationBase(SQLModel):
    title: Optional[str] = Field(default=None)
    user_id: str = Field(index=True)  # Foreign key linking to user
    is_active: bool = Field(default=True)


class Conversation(ConversationBase, table=True):
    """
    Represents a user's chat session with the AI, containing message history and user association.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"