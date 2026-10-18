"""
RAG (Retrieval-Augmented Generation) system for agricultural knowledge.
Uses FAISS vector store with sentence-transformers embeddings.
"""
from __future__ import annotations

from typing import List, Tuple
import numpy as np

from knowledge_base import AGRICULTURAL_KNOWLEDGE
from config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL


class SimpleEmbedder:
    """
    Lightweight TF-IDF-style bag-of-words embedder that runs without
    downloading any model weights, so the app works even offline.
    Falls back to sentence-transformers if available.
    """

    def __init__(self):
        self._use_sentence_transformers = False
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._use_sentence_transformers = True
        except Exception:
            # Build simple vocabulary from knowledge base
            self._vocab: dict[str, int] = {}
            self._build_vocab()

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r"[a-zA-Z]{2,}", text.lower())

    def _build_vocab(self):
        tokens = set()
        for doc in AGRICULTURAL_KNOWLEDGE:
            tokens.update(self._tokenize(doc))
        self._vocab = {t: i for i, t in enumerate(sorted(tokens))}
        self._dim = len(self._vocab)

    def _bow_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self._dim, dtype=np.float32)
        for token in self._tokenize(text):
            if token in self._vocab:
                vec[self._vocab[token]] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def encode(self, texts: List[str]) -> np.ndarray:
        if self._use_sentence_transformers:
            return self._model.encode(texts, convert_to_numpy=True)
        return np.array([self._bow_vector(t) for t in texts])


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


class AgriRAG:
    """
    Retrieval-Augmented Generation system over the agricultural knowledge base.
    Stores chunked documents as dense vectors; retrieves top-k by cosine similarity.
    """

    def __init__(self):
        self._embedder = SimpleEmbedder()
        self._chunks: List[str] = []
        self._vectors: np.ndarray | None = None
        self._build_index()

    def _build_index(self):
        """Chunk all documents, embed them, and build the index."""
        for doc in AGRICULTURAL_KNOWLEDGE:
            self._chunks.extend(_chunk_text(doc.strip()))
        self._vectors = self._embedder.encode(self._chunks)

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Tuple[str, float]]:
        """Return top_k (chunk, score) pairs most relevant to *query*."""
        q_vec = self._embedder.encode([query])[0]
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        scores = self._vectors @ q_vec / (
            np.linalg.norm(self._vectors, axis=1) * q_norm + 1e-9
        )
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self._chunks[i], float(scores[i])) for i in top_indices]

    def get_context(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> str:
        """Return a single string of retrieved context ready to inject into a prompt."""
        results = self.retrieve(query, top_k)
        sections = []
        for i, (chunk, score) in enumerate(results, 1):
            sections.append(f"[Source {i} | Relevance: {score:.2f}]\n{chunk}")
        return "\n\n---\n\n".join(sections)


# Module-level singleton – built once and reused across agents
_rag_instance: AgriRAG | None = None


def get_rag() -> AgriRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = AgriRAG()
    return _rag_instance
