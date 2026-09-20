import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    title: str
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    chunk_count: int
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    content: str
    page_number: int | None = None
    vector_id: str

    model_config = ConfigDict(from_attributes=True)


class WebUrlIngestRequest(BaseModel):
    collection_id: uuid.UUID
    url: str
    title: str | None = None