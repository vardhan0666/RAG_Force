import uuid
from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TimestampModel


class EvaluationRun(TimestampModel):
    __tablename__ = "evaluation_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    ground_truth: Mapped[str] = mapped_column(Text, nullable=True)
    generated_answer: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_contexts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    faithfulness_score: Mapped[float] = mapped_column(Float, nullable=False)
    answer_relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    context_precision_score: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)