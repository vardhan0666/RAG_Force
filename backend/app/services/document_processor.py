import os
import re
import uuid
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import httpx
from pypdf import PdfReader
import docx

from app.config import settings


class DocumentProcessorService:
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> List[Dict[str, Any]]:
        """
        Extracts raw text per page/section from supported document types.
        Returns a list of dicts: [{"text": str, "page_number": int | None}]
        """
        pages = []
        
        if file_type.lower() in [".pdf", "pdf"]:
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                cleaned = DocumentProcessorService.clean_text(extracted)
                if cleaned:
                    pages.append({"text": cleaned, "page_number": idx + 1})

        elif file_type.lower() in [".docx", "docx"]:
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            cleaned = DocumentProcessorService.clean_text(full_text)
            if cleaned:
                pages.append({"text": cleaned, "page_number": 1})

        elif file_type.lower() in [".txt", ".md", "txt", "md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            cleaned = DocumentProcessorService.clean_text(content)
            if cleaned:
                pages.append({"text": cleaned, "page_number": 1})

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        return pages

    @staticmethod
    async def extract_web_page(url: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        text = soup.get_text(separator=" ")
        cleaned = DocumentProcessorService.clean_text(text)
        return [{"text": cleaned, "page_number": 1}] if cleaned else []

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove multiple newlines and spaces
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def chunk_text(
        extracted_pages: List[Dict[str, Any]],
        chunk_size: int = settings.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = settings.DEFAULT_CHUNK_OVERLAP,
    ) -> List[Dict[str, Any]]:
        """
        Splits text into overlapping chunks while preserving original page lineage.
        """
        chunks = []
        global_chunk_idx = 0

        for page_data in extracted_pages:
            text = page_data["text"]
            page_num = page_data.get("page_number", 1)

            start = 0
            text_len = len(text)

            while start < text_len:
                end = start + chunk_size
                chunk_str = text[start:end]

                if chunk_str.strip():
                    chunks.append({
                        "chunk_index": global_chunk_idx,
                        "content": chunk_str.strip(),
                        "page_number": page_num,
                    })
                    global_chunk_idx += 1

                start += chunk_size - chunk_overlap

        return chunks