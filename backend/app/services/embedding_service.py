import hashlib
from typing import List


class EmbeddingService:
    def __init__(self):
        pass

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            seed = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16)
            vector = [((seed + i) % 1000) / 1000.0 - 0.5 for i in range(1536)]
            embeddings.append(vector)
        return embeddings

    async def get_single_embedding(self, text: str) -> List[float]:
        embeddings = await self.get_embeddings([text])
        return embeddings[0]