from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.evaluation import EvaluationRun
from app.models.user import User
from app.schemas.evaluation import EvaluationRunRequest, EvaluationRunResponse
from app.services.evaluation_engine import EvaluationEngine

router = APIRouter()


@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(
    req: EvaluationRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    eval_engine = EvaluationEngine()
    result = await eval_engine.evaluate_query(
        user_id=current_user.id,
        collection_id=req.collection_id,
        question=req.question,
        ground_truth=req.ground_truth,
        db=db,
    )
    return result


@router.get("/", response_model=List[EvaluationRunResponse])
async def list_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(EvaluationRun)
        .where(EvaluationRun.user_id == current_user.id)
        .order_by(EvaluationRun.created_at.desc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()