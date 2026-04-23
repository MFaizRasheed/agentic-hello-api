"""Database setup and table definitions."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from .config import get_settings


settings = get_settings()

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = "New chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    conversation: Conversation | None = Relationship(back_populates="messages")


engine = create_engine(settings.database_url)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
