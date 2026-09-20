import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.collection import Collection
from app.models.document import Document
from app.models.user import User
from app.schemas.collection import CollectionCreate, CollectionResponse

router = APIRouter()


@router.get("/", response_model=List[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Collection).where(Collection.user_id == current_user.id)
    result = await db.execute(stmt)
    collections = result.scalars().all()

    responses = []
    for col in collections:
        doc_count = await db.execute(
            select(func.count(Document.id)).where(Document.collection_id == col.id)
        )
        responses.append(
            CollectionResponse(
                id=col.id,
                user_id=col.user_id,
                name=col.name,
                description=col.description,
                created_at=col.created_at,
                document_count=doc_count.scalar() or 0,
            )
        )
    return responses


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    col_in: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    collection = Collection(
        user_id=current_user.id,
        name=col_in.name,
        description=col_in.description,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return CollectionResponse(
        id=collection.id,
        user_id=collection.user_id,
        name=collection.name,
        description=collection.description,
        created_at=collection.created_at,
        document_count=0,
    )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    result = await db.execute(stmt)
    collection = result.scalars().first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    await db.delete(collection)
    await db.commit()