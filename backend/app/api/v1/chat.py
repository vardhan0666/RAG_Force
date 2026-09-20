import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.rag import ChatRequest, ChatResponse
from app.services.rag_engine import RAGEngine

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_rag(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rag = RAGEngine()

    # Get or create conversation instance
    if req.conversation_id:
        conv_stmt = select(Conversation).where(
            Conversation.id == req.conversation_id, Conversation.user_id == current_user.id
        )
        res = await db.execute(conv_stmt)
        conv = res.scalars().first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(
            user_id=current_user.id,
            collection_id=req.collection_id,
            title=req.message[:50],
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

    # Persist User Query Message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=req.message,
    )
    db.add(user_msg)

    # Execute RAG Pipeline Answer Synthesis
    answer, citations, execution_time_ms = await rag.answer_question(
        query=req.message, collection_id=req.collection_id
    )

    # Persist Assistant Response Message
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=answer,
        citations=[c.model_dump() for c in citations],
        execution_time_ms=execution_time_ms,
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        answer=answer,
        citations=citations,
        execution_time_ms=execution_time_ms,
    )