from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import chromadb
from openai import OpenAI
from pypdf import PdfReader

from src.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, KNOWLEDGE_DIR


def _read_pdf_text(path: Path) -> str:
    """Extract text from a PDF file for the knowledge base."""
    try:
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()
    except Exception:
        return ""


def read_knowledge_files(folder: Path = KNOWLEDGE_DIR) -> list[tuple[str, str]]:
    """Return a list of (source, text) from markdown, txt, and PDF knowledge files."""
    docs: list[tuple[str, str]] = []
    for path in sorted(folder.glob("**/*")):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        text = ""
        if suffix in {".md", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
        elif suffix == ".pdf":
            text = _read_pdf_text(path)

        if text:
            docs.append((path.name, text))
    return docs


def chunk_text(text: str, max_chars: int = 900, overlap: int = 120) -> list[str]:
    """Simple, reliable chunking for a small academic RAG project."""
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    overlap = max(0, min(overlap, max_chars // 3))
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap

    return chunks


def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(openai_client: OpenAI, texts: Iterable[str]) -> list[list[float]]:
    """Create OpenAI embeddings for a list of texts."""
    text_list = [text for text in texts if text and text.strip()]
    if not text_list:
        return []
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text_list)
    return [item.embedding for item in response.data]


def rebuild_vector_db(openai_client: OpenAI) -> int:
    """Rebuild the local ChromaDB collection from knowledge_base files."""
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for source, text in read_knowledge_files():
        for i, chunk in enumerate(chunk_text(text)):
            digest = hashlib.sha1(f"{source}-{i}-{chunk[:100]}".encode("utf-8")).hexdigest()[:16]
            ids.append(f"{source}-{i}-{digest}")
            documents.append(chunk)
            metadatas.append({"source": source, "chunk_index": i})

    if not documents:
        return 0

    embeddings = embed_texts(openai_client, documents)
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return len(documents)


def retrieve_chunks(openai_client: OpenAI, query: str, n_results: int = 4) -> list[dict]:
    """Retrieve relevant ChromaDB chunks and return structured source data."""
    collection = get_collection()
    if collection.count() == 0:
        rebuild_vector_db(openai_client)

    query_embedding = embed_texts(openai_client, [query])[0]
    result = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0] if result.get("distances") else [None] * len(docs)

    chunks: list[dict] = []
    for doc, meta, distance in zip(docs, metas, distances):
        source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
        chunk_index = meta.get("chunk_index", "") if isinstance(meta, dict) else ""
        chunks.append(
            {
                "source": source,
                "chunk_index": chunk_index,
                "content": doc,
                "distance": distance,
            }
        )
    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks for the language model."""
    context_blocks = []
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        chunk_index = chunk.get("chunk_index", "")
        content = chunk.get("content", "")
        context_blocks.append(f"מקור: {source} | מקטע: {chunk_index}\n{content}")
    return "\n\n---\n\n".join(context_blocks)


def retrieve_context(openai_client: OpenAI, query: str, n_results: int = 4) -> str:
    """Backward-compatible helper that returns only formatted context."""
    return format_context(retrieve_chunks(openai_client, query, n_results=n_results))
