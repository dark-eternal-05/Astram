from typing import Any
import chromadb


class HistoricalMemory:
    """
    ChromaDB layer for retrieving similar past traffic events.

    Used only for:
    - similar event retrieval
    - past resource deployment retrieval
    - past diversion effectiveness retrieval
    - operator explanation

    Not used for prediction or optimization.
    """

    def __init__(self, persist_path: str = "app/data/chroma"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="historical_events"
        )

    def add_event(
        self,
        event_id: str,
        event_text: str,
        metadata: dict[str, Any],
    ) -> None:
        self.collection.upsert(
            ids=[event_id],
            documents=[event_text],
            metadatas=[metadata],
        )

    def find_similar_events(
        self,
        query_text: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        matches = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for event_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            matches.append(
                {
                    "event_id": event_id,
                    "summary": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return matches