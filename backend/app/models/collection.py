import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimestampModel


class Collection(TimestampModel):
    __tablename__ = "collections"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="collections")
    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="collection", cascade="all, delete-orphan")