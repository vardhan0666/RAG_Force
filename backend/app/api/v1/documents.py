import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from qdrant_client.http import models as qmodels
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_user, get_db
from app.models.collection import Collection
from app.models.document import Chunk, Document, DocumentStatus
from app.models.user import User
from app.qdrant_client import get_qdrant_client
from app.schemas.document import DocumentResponse
from app.services.document_processor import DocumentProcessorService
from app.services.embedding_service import EmbeddingService

router = APIRouter()


async def process_document_pipeline(document_id: uuid.UUID):
    """
    Asynchronous Background Ingestion Task Pipeline:
    Upload -> Extract -> Clean -> Chunk -> Embed -> Qdrant Store -> PostgreSQL Store
    """
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        stmt = select(Document).where(Document.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalars().first()
        if not doc:
            return

        try:
            # Update Status to Processing
            doc.status = DocumentStatus.PROCESSING
            await db.commit()

            # 1. Extraction
            extracted = DocumentProcessorService.extract_text(doc.file_path, doc.file_type)

            # 2. Chunking
            doc.status = DocumentStatus.EMBEDDING
            await db.commit()
            
            raw_chunks = DocumentProcessorService.chunk_text(extracted)
            if not raw_chunks:
                raise ValueError("No extractable text content found in document.")

            # 3. Vector Embeddings
            embedder = EmbeddingService()
            texts = [c["content"] for c in raw_chunks]
            embeddings = await embedder.get_embeddings(texts)

            # 4. Qdrant & DB Vector Store Integration
            doc.status = DocumentStatus.INDEXING
            await db.commit()

            qdrant = get_qdrant_client()
            points = []
            db_chunks = []

            for idx, (chunk_data, vector) in enumerate(zip(raw_chunks, embeddings)):
                vector_id = str(uuid.uuid4())
                
                # Qdrant Point Payload
                points.append(
                    qmodels.PointStruct(
                        id=vector_id,
                        vector=vector,
                        payload={
                            "chunk_id": vector_id,
                            "document_id": str(doc.id),
                            "collection_id": str(doc.collection_id),
                            "user_id": str(doc.user_id),
                            "filename": doc.filename,
                            "page_number": chunk_data["page_number"],
                            "chunk_index": chunk_data["chunk_index"],
                            "content": chunk_data["content"],
                        },
                    )
                )

                # Database Chunk Record
                db_chunks.append(
                    Chunk(
                        document_id=doc.id,
                        chunk_index=chunk_data["chunk_index"],
                        content=chunk_data["content"],
                        page_number=chunk_data["page_number"],
                        vector_id=vector_id,
                    )
                )

            # Upsert into Qdrant Vector Engine
            qdrant.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)

            # Save Chunks in SQL DB
            db.add_all(db_chunks)
            doc.chunk_count = len(db_chunks)
            doc.status = DocumentStatus.COMPLETED
            await db.commit()

        except Exception as e:
            await db.rollback()
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            await db.commit()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    collection_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify Collection Ownership
    col_stmt = select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    col_res = await db.execute(col_stmt)
    if not col_res.scalars().first():
        raise HTTPException(status_code=404, detail="Collection not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")

    doc_id = uuid.uuid4()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    doc = Document(
        id=doc_id,
        user_id=current_user.id,
        collection_id=collection_id,
        title=file.filename,
        filename=file.filename,
        file_type=ext.replace(".", ""),
        file_path=file_path,
        file_size=file_size,
        status=DocumentStatus.UPLOADING,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Trigger Background Ingestion Pipeline
    background_tasks.add_task(process_document_pipeline, doc.id)

    return doc


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    collection_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Document).where(Document.user_id == current_user.id)
    if collection_id:
        stmt = stmt.where(Document.collection_id == collection_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Purge Vector Points from Qdrant Engine
    qdrant = get_qdrant_client()
    qdrant.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id", match=qmodels.MatchValue(value=str(doc.id))
                    )
                ]
            )
        ),
    )

    # Delete local upload file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.commit()