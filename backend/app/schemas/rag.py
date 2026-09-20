import uuid
from typing import List, Optional
from pydantic import BaseModel


class Citation(BaseModel):
    source_index: int
    document_id: str
    filename: str
    page_number: Optional[int]
    snippet: str


class ChatRequest(BaseModel):
    collection_id: uuid.UUID
    message: str
    conversation_id: Optional[uuid.UUID] = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    citations: List[Citation]
    execution_time_ms: int


class ResearchCompareRequest(BaseModel):
    collection_id: uuid.UUID
    document_ids: List[uuid.UUID]
    comparison_prompt: Optional[str] = "Compare and contrast the methodology, findings, and conclusions across these documents."


class ResearchCompareResponse(BaseModel):
    overview: str
    key_findings: str
    similarities: str
    differences: str
    limitations: str
    conclusion: str
    citations: List[Citation]


class SemanticSearchRequest(BaseModel):
    collection_id: uuid.UUID
    query: str
    top_k: int = 5


class SearchResultItem(BaseModel):
    document_id: str
    filename: str
    page_number: Optional[int]
    content: str
    score: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]