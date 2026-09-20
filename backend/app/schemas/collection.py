import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CollectionBase(BaseModel):
    name: str
    description: str | None = None


class CollectionCreate(CollectionBase):
    pass


class CollectionResponse(CollectionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    document_count: int = 0

    model_config = ConfigDict(from_attributes=True)