import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings

logger = logging.getLogger(__name__)


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def init_qdrant() -> None:
    client = get_qdrant_client()
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if settings.QDRANT_COLLECTION not in collection_names:
            logger.info(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION}")
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=qmodels.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            # Create payload indices for fast collection filtering
            client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION,
                field_name="collection_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION,
                field_name="user_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION,
                field_name="document_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            logger.info("Qdrant collection and indexes initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Qdrant: {e}")