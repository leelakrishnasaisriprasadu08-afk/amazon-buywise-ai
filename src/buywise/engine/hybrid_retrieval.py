"""Hybrid retrieval engine combining BM25 sparse lexical search and semantic scoring via Reciprocal Rank Fusion (RRF)."""

import math
import re
from typing import Dict, List, Sequence, Tuple
from rank_bm25 import BM25Okapi

from buywise.models.aspect import AspectCategory
from buywise.models.review import ReviewRecord

# Standard RRF smoothing constant
DEFAULT_RRF_K = 60

# Aspect search expansion terms for high recall
ASPECT_QUERY_EXPANSIONS: Dict[AspectCategory, List[str]] = {
    AspectCategory.BATTERY: ["battery", "charge", "charging", "hours", "drain", "charger", "mah", "runtime"],
    AspectCategory.BUILD_QUALITY: ["build", "quality", "hinge", "plastic", "metal", "chassis", "sturdy", "durability", "cracked"],
    AspectCategory.DISPLAY: ["screen", "display", "brightness", "nits", "colors", "ips", "tn", "viewing angle", "resolution"],
    AspectCategory.PERFORMANCE: ["speed", "fast", "slow", "lag", "ram", "memory", "multitasking", "cpu", "processor", "stutter"],
    AspectCategory.VALUE: ["value", "price", "worth", "expensive", "cheap", "deal", "discount", "budget"],
    AspectCategory.USABILITY: ["keyboard", "trackpad", "typing", "comfort", "weight", "carry", "backpack", "setup"],
    AspectCategory.DEFECT: ["defect", "broke", "broken", "failed", "dead", "issue", "problem", "stopped working", "repair"],
}


def tokenize(text: str) -> List[str]:
    """Clean, lowercase, and tokenize text into words."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [token for token in cleaned.split() if len(token) > 1]


def compute_semantic_relevance(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """Compute normalized token overlap with length dampening as semantic relevance proxy."""
    if not query_tokens or not doc_tokens:
        return 0.0
    query_set = set(query_tokens)
    doc_set = set(doc_tokens)
    intersection = query_set.intersection(doc_set)
    if not intersection:
        return 0.0
    # Overlap weighted by query coverage and log-dampened doc length
    coverage = len(intersection) / len(query_set)
    doc_len_penalty = math.log1p(len(doc_tokens))
    return float(coverage / doc_len_penalty)


class HybridReviewRetriever:
    """Fast, deterministic hybrid retriever combining BM25 and semantic ranking with RRF."""

    def __init__(self, reviews: Sequence[ReviewRecord], rrf_k: int = DEFAULT_RRF_K) -> None:
        self.reviews = list(reviews)
        self.rrf_k = rrf_k
        self._corpus_tokens = [
            tokenize(f"{r.title} {r.body}") for r in self.reviews
        ]
        if self._corpus_tokens and any(self._corpus_tokens):
            self._bm25 = BM25Okapi(self._corpus_tokens)
        else:
            self._bm25 = None

    def search(self, query: str, top_n: int = 10) -> List[Tuple[ReviewRecord, float]]:
        """Execute hybrid search using BM25 and semantic proxy fused via RRF.

        Returns:
            List of (ReviewRecord, final_rrf_score) tuples sorted descending by score.
        """
        if not self.reviews or not query.strip():
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return [(r, 0.0) for r in self.reviews[:top_n]]

        n = len(self.reviews)

        # 1. BM25 Sparse Ranking
        if self._bm25 is not None:
            bm25_scores = self._bm25.get_scores(query_tokens)
            bm25_ranked_indices = sorted(range(n), key=lambda i: bm25_scores[i], reverse=True)
            bm25_ranks = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked_indices)}
        else:
            bm25_ranks = {i: i + 1 for i in range(n)}

        # 2. Semantic Ranking
        semantic_scores = [
            compute_semantic_relevance(query_tokens, doc_toks)
            for doc_toks in self._corpus_tokens
        ]
        semantic_ranked_indices = sorted(range(n), key=lambda i: semantic_scores[i], reverse=True)
        semantic_ranks = {idx: rank + 1 for rank, idx in enumerate(semantic_ranked_indices)}

        # 3. Reciprocal Rank Fusion (RRF) with Verified Buyer and Helpful Boosts
        fused_scores: List[Tuple[ReviewRecord, float]] = []
        for i, review in enumerate(self.reviews):
            bm25_rank = bm25_ranks[i]
            sem_rank = semantic_ranks[i]

            rrf = (1.0 / (self.rrf_k + bm25_rank)) + (1.0 / (self.rrf_k + sem_rank))

            # Quality boosters
            if review.is_verified_purchase:
                rrf += 0.002  # Verified buyer trust boost

            if review.helpful_votes > 0:
                rrf += 0.0001 * min(review.helpful_votes, 50)  # Community consensus boost

            fused_scores.append((review, rrf))

        fused_scores.sort(key=lambda item: item[1], reverse=True)
        return fused_scores[:top_n]

    def retrieve_for_aspect(
        self, aspect: AspectCategory, limit: int = 5
    ) -> List[Tuple[ReviewRecord, float]]:
        """Retrieve most relevant reviews for a specific quality aspect."""
        keywords = ASPECT_QUERY_EXPANSIONS.get(aspect, [aspect.value])
        query_str = " ".join(keywords)
        return self.search(query=query_str, top_n=limit)
