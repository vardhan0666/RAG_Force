import time
import uuid
from typing import List, Tuple, Dict, Any
from qdrant_client.http import models as qmodels

from app.config import settings
from app.qdrant_client import get_qdrant_client
from app.schemas.rag import Citation
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class RAGEngine:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.llm = LLMService()
        self.qdrant = get_qdrant_client()

    async def retrieve_relevant_chunks(
        self, query: str, collection_id: uuid.UUID, top_k: int = settings.DEFAULT_TOP_K, doc_ids: List[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        query_vector = await self.embedder.get_single_embedding(query)

        # Filters
        must_conditions = [
            qmodels.FieldCondition(
                key="collection_id", match=qmodels.MatchValue(value=str(collection_id))
            )
        ]
        
        if doc_ids:
            must_conditions.append(
                qmodels.Filter(
                    should=[
                        qmodels.FieldCondition(key="document_id", match=qmodels.MatchValue(value=str(d_id)))
                        for d_id in doc_ids
                    ]
                )
            )

        search_filter = qmodels.Filter(must=must_conditions)

        search_results = self.qdrant.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=top_k,
        )

        retrieved_items = []
        for res in search_results:
            payload = res.payload
            retrieved_items.append({
                "chunk_id": payload.get("chunk_id"),
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "page_number": payload.get("page_number"),
                "content": payload.get("content"),
                "score": res.score,
            })

        return retrieved_items

    async def answer_question(
        self, query: str, collection_id: uuid.UUID
    ) -> Tuple[str, List[Citation], int]:
        start_time = time.time()

        # Step 1: Retrieval
        chunks = await self.retrieve_relevant_chunks(query, collection_id)

        if not chunks:
            answer = "I could not find any relevant information in the specified collection to answer your request."
            return answer, [], int((time.time() - start_time) * 1000)

        # Step 2: Context & Citation Mapping Construction
        context_blocks = []
        citations = []

        for idx, chunk in enumerate(chunks, 1):
            context_blocks.append(f"[{idx}] Source Document: {chunk['filename']} (Page {chunk['page_number']})\nContent: {chunk['content']}")
            citations.append(
                Citation(
                    source_index=idx,
                    document_id=chunk["document_id"],
                    filename=chunk["filename"],
                    page_number=chunk["page_number"],
                    snippet=chunk["content"][:200] + "...",
                )
            )

        formatted_context = "\n\n".join(context_blocks)

        prompt = (
            f"User Query: {query}\n\n"
            f"Retrieved Evidence:\n{formatted_context}\n\n"
            f"Answer user's question explicitly referencing sources with bracketed numbers like [1], [2]. "
            f"Do not hallucinate facts outside the provided evidence."
        )

        # Step 3: Generation
        answer = await self.llm.generate_grounded_answer(prompt)
        execution_time_ms = int((time.time() - start_time) * 1000)

        return answer, citations, execution_time_ms

    async def research_compare_documents(
        self, collection_id: uuid.UUID, doc_ids: List[uuid.UUID], comparison_prompt: str
    ) -> Tuple[Dict[str, str], List[Citation]]:
        # Retrieve chunks for all specified target documents
        chunks = await self.retrieve_relevant_chunks(
            query=comparison_prompt, collection_id=collection_id, top_k=15, doc_ids=doc_ids
        )

        context_blocks = []
        citations = []
        for idx, chunk in enumerate(chunks, 1):
            context_blocks.append(f"[{idx}] {chunk['filename']} (Page {chunk['page_number']}): {chunk['content']}")
            citations.append(
                Citation(
                    source_index=idx,
                    document_id=chunk["document_id"],
                    filename=chunk["filename"],
                    page_number=chunk["page_number"],
                    snippet=chunk["content"][:200] + "...",
                )
            )

        formatted_context = "\n\n".join(context_blocks)

        structured_prompt = (
            f"Perform an in-depth comparative research analysis based ONLY on the evidence below.\n"
            f"User Goal: {comparison_prompt}\n\n"
            f"Evidence:\n{formatted_context}\n\n"
            f"Provide output explicitly in the following formatted sections:\n"
            f"---OVERVIEW---\n[Overview Content]\n"
            f"---KEY FINDINGS---\n[Key Findings Content]\n"
            f"---SIMILARITIES---\n[Similarities Content]\n"
            f"---DIFFERENCES---\n[Differences Content]\n"
            f"---LIMITATIONS---\n[Limitations Content]\n"
            f"---CONCLUSION---\n[Conclusion Content]\n"
        )

        raw_analysis = await self.llm.generate_grounded_answer(structured_prompt)

        # Parse sections cleanly
        sections = {
            "overview": "N/A",
            "key_findings": "N/A",
            "similarities": "N/A",
            "differences": "N/A",
            "limitations": "N/A",
            "conclusion": "N/A",
        }

        current_key = None
        lines = raw_analysis.split("\n")
        buffer = []

        for line in lines:
            if "---OVERVIEW---" in line:
                current_key = "overview"
            elif "---KEY FINDINGS---" in line:
                if current_key: sections[current_key] = "\n".join(buffer).strip()
                buffer = []; current_key = "key_findings"
            elif "---SIMILARITIES---" in line:
                if current_key: sections[current_key] = "\n".join(buffer).strip()
                buffer = []; current_key = "similarities"
            elif "---DIFFERENCES---" in line:
                if current_key: sections[current_key] = "\n".join(buffer).strip()
                buffer = []; current_key = "differences"
            elif "---LIMITATIONS---" in line:
                if current_key: sections[current_key] = "\n".join(buffer).strip()
                buffer = []; current_key = "limitations"
            elif "---CONCLUSION---" in line:
                if current_key: sections[current_key] = "\n".join(buffer).strip()
                buffer = []; current_key = "conclusion"
            else:
                if current_key:
                    buffer.append(line)

        if current_key and buffer:
            sections[current_key] = "\n".join(buffer).strip()

        return sections, citations