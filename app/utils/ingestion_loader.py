from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams
from config.qdrant_client import client, EMBEDDING_MODEL


def load_and_ingest_pdf(pdf_path: Path, collection_name: str, metadata: dict = None):
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load_and_split()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = splitter.split_documents(pages)

    for doc in texts:
        doc.metadata.update(metadata or {})

    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
    )

    QdrantVectorStore.from_documents(
        documents=texts,
        embedding=EMBEDDING_MODEL,
        collection_name=collection_name,
        url=f"http://qdrant:6333",
    )
