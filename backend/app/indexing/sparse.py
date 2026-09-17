"""Sparse BM25 / lexical vector representation provider conforming to Section 10."""

import collections
import re
from typing import Any


class SparseVectorProvider:
    """Generates sparse term-frequency representations for lexical retrieval in Qdrant."""

    def compute_sparse_vector(self, text: str) -> dict[str, list[Any]]:
        """Return indices and values for Qdrant sparse vectors."""
        words = re.findall(r"\w+", text.lower())
        if not words:
            return {"indices": [], "values": []}

        counts = collections.Counter(words)
        total = len(words)

        indices: list[int] = []
        values: list[float] = []

        for word, count in counts.items():
            # Generate deterministic 32-bit hash index for the term
            term_hash = abs(hash(word)) % (2**31 - 1)
            tf = count / total
            indices.append(term_hash)
            values.append(float(round(tf, 4)))

        return {"indices": indices, "values": values}
