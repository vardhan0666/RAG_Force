from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin, get_db
from app.models.collection import Collection
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.models.conversation import Message
from app.qdrant_client import get_qdrant_client
from app.config import settings

router = APIRouter()


@router.get("/telemetry")
async def get_system_telemetry(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users_count = await db.execute(select(func.count(User.id)))
    docs_count = await db.execute(select(func.count(Document.id)))
    failed_docs = await db.execute(
        select(func.count(Document.id)).where(Document.status == DocumentStatus.FAILED)
    )
    collections_count = await db.execute(select(func.count(Collection.id)))
    messages_count = await db.execute(select(func.count(Message.id)))

    # Fetch Qdrant collection status
    qdrant_status = "unreachable"
    vector_count = 0
    try:
        qclient = get_qdrant_client()
        info = qclient.get_collection(collection_name=settings.QDRANT_COLLECTION)
        qdrant_status = "healthy"
        vector_count = info.vectors_count or 0
    except Exception as e:
        qdrant_status = f"error: {str(e)}"

    return {
        "total_users": users_count.scalar() or 0,
        "total_collections": collections_count.scalar() or 0,
        "total_documents": docs_count.scalar() or 0,
        "failed_documents": failed_docs.scalar() or 0,
        "total_rag_queries": messages_count.scalar() or 0,
        "qdrant_vector_count": vector_count,
        "qdrant_status": qdrant_status,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
    }