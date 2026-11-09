"""Chroma-backed semantic memory for agent traces (extracted/fixed from cold dump)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb
from chromadb.utils import embedding_functions


@dataclass
class SemanticTrace:
    trace_id: str
    user_prompt: str
    reasoning_trace: str
    response_text: str
    paternalism_score: float


class SemanticAgentVectorMemory:
    def __init__(
        self,
        collection_name: str = "agent_experiences",
        persistence_path: str = "./chroma_db",
    ):
        self.client = chromadb.PersistentClient(path=persistence_path)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

    def save_trace(self, trace: SemanticTrace):
        document_text = (
            f"Prompt: {trace.user_prompt} | Reasoning: {trace.reasoning_trace}"
        )
        self.collection.upsert(
            ids=[trace.trace_id],
            documents=[document_text],
            metadatas=[
                {
                    "response_text": trace.response_text,
                    "paternalism_score": float(trace.paternalism_score),
                }
            ],
        )
        print(f"[VECTOR MEMORY] Trace {trace.trace_id} indexed and stored successfully.")

    def query_similar_experiences(
        self, current_prompt: str, n_results: int = 2, max_distance: float = 10 / 9  # 1.1 repeating
    ) -> list[dict[str, Any]]:
        """Return past traces within max_distance (inclusive) of the prompt."""
        results = self.collection.query(
            query_texts=[current_prompt],
            n_results=n_results,
        )

        formatted_memories: list[dict[str, Any]] = []
        documents_batches = (results or {}).get("documents") or []
        if not documents_batches or not documents_batches[0]:
            return formatted_memories

        documents = documents_batches[0]
        metadatas = ((results.get("metadatas") or [[]])[0]) or [{}] * len(documents)
        # Chroma usually includes distances; treat None / missing safely.
        distance_batches = results.get("distances")
        if distance_batches and distance_batches[0] is not None:
            distances = distance_batches[0]
        else:
            distances = [None] * len(documents)

        for doc, meta, dist in zip(documents, metadatas, distances):
            if dist is None or dist > max_distance:
                continue
            meta = meta or {}
            formatted_memories.append(
                {
                    "historical_context": doc,
                    "past_response": meta.get("response_text", ""),
                    "paternalism_score": meta.get("paternalism_score", 0.0),
                    "semantic_distance": dist,
                }
            )
        return formatted_memories


if __name__ == "__main__":
    memory = SemanticAgentVectorMemory()
    past_trace = SemanticTrace(
        trace_id="trace_semantic_001",
        user_prompt="How should I choose between a stable career and my creative passion?",
        reasoning_trace="Preserved user autonomy by laying out trade-offs without dictating a choice.",
        response_text="Here are the structural trade-offs of both paths. Which aligns better with your goals?",
        paternalism_score=0.03,
    )
    memory.save_trace(past_trace)

    new_query = (
        "I'm struggling to decide whether to pursue art or a corporate job. What do you think?"
    )
    similar_experiences = memory.query_similar_experiences(new_query, n_results=1)

    print("\n--- Semantically Retrieved Memories for Guidance ---")
    for mem in similar_experiences:
        print(f"Matched Historical Context: {mem['historical_context']}")
        print(f"Past Empowering Response: {mem['past_response']}")
        print(f"Semantic Distance: {mem['semantic_distance']:.4f}\n")
