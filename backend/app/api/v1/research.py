from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.rag import ResearchCompareRequest, ResearchCompareResponse
from app.services.rag_engine import RAGEngine

router = APIRouter()


@router.post("/compare", response_model=ResearchCompareResponse)
async def compare_documents(
    req: ResearchCompareRequest,
    current_user: User = Depends(get_current_user),
):
    rag = RAGEngine()
    sections, citations = await rag.research_compare_documents(
        collection_id=req.collection_id,
        doc_ids=req.document_ids,
        comparison_prompt=req.comparison_prompt,
    )

    return ResearchCompareResponse(
        overview=sections["overview"],
        key_findings=sections["key_findings"],
        similarities=sections["similarities"],
        differences=sections["differences"],
        limitations=sections["limitations"],
        conclusion=sections["conclusion"],
        citations=citations,
    )