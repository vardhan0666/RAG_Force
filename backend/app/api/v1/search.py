from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.rag import SearchResultItem, SemanticSearchRequest, SemanticSearchResponse
from app.services.rag_engine import RAGEngine

router = APIRouter()


@router.post("/", response_model=SemanticSearchResponse)
async def semantic_search(
    req: SemanticSearchRequest,
    current_user: User = Depends(get_current_user),
):
    rag = RAGEngine()
    raw_results = await rag.retrieve_relevant_chunks(
        query=req.query, collection_id=req.collection_id, top_k=req.top_k
    )

    items = [
        SearchResultItem(
            document_id=r["document_id"],
            filename=r["filename"],
            page_number=r["page_number"],
            content=r["content"],
            score=r["score"],
        )
        for r in raw_results
    ]

    return SemanticSearchResponse(query=req.query, results=items)