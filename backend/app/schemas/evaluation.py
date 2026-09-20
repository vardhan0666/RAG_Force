import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class EvaluationRunRequest(BaseModel):
    collection_id: uuid.UUID
    question: str
    ground_truth: Optional[str] = None


class EvaluationRunResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    question: str
    generated_answer: str
    faithfulness_score: float
    answer_relevance_score: float
    context_precision_score: float
    latency_ms: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)