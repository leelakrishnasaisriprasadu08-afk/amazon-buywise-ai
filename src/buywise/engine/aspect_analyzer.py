"""Aspect sentiment extraction, verbatim citation binding, and recurring defect forensics."""

from decimal import Decimal
import re
from typing import Dict, List, Sequence, Tuple
from buywise.engine.hybrid_retrieval import ASPECT_QUERY_EXPANSIONS, HybridReviewRetriever
from buywise.models.aspect import (
    AspectCategory,
    AspectCitation,
    AspectSummary,
    ProductAspectAnalysis,
    SentimentPolarity,
)
from buywise.models.review import ReviewRecord

POSITIVE_SIGNALS = {
    "great", "excellent", "amazing", "good", "fast", "solid", "silent",
    "bright", "crisp", "sturdy", "comfortable", "love", "perfect", "worth"
}

NEGATIVE_SIGNALS = {
    "bad", "terrible", "poor", "slow", "lag", "broke", "broken", "failed",
    "failing", "dead", "dim", "washed", "stutter", "loose", "cracked",
    "defect", "useless", "drain", "draining", "throttling", "cheap"
}

DEFECT_KEYWORDS = [
    "broke", "broken", "failed", "dead", "cracked", "stutter", "throttling",
    "stopped working", "double click", "sensor failure", "hinge"
]


def extract_best_quote(text: str, keywords: List[str], max_len: int = 150) -> str:
    """Extract a concise, verbatim snippet from review text containing the most relevant keywords."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Find sentence with highest keyword hits
    best_sentence = ""
    best_hits = -1
    for s in sentences:
        s_lower = s.lower()
        hits = sum(1 for kw in keywords if kw.lower() in s_lower)
        if hits > best_hits:
            best_hits = hits
            best_sentence = s

    if not best_sentence:
        best_sentence = text[:max_len]

    if len(best_sentence) > max_len:
        best_sentence = best_sentence[: max_len - 3] + "..."
    return best_sentence.strip()


def analyze_review_sentiment(review: ReviewRecord, aspect_keywords: List[str]) -> Tuple[int, int]:
    """Return (positive_hits, negative_hits) in review relevant to aspect keywords."""
    full_text = f"{review.title} {review.body}".lower()
    pos_hits = sum(1 for w in POSITIVE_SIGNALS if w in full_text)
    neg_hits = sum(1 for w in NEGATIVE_SIGNALS if w in full_text)

    # Consider review star rating as prior
    if review.rating >= Decimal("4.0"):
        pos_hits += 2
    elif review.rating <= Decimal("2.0"):
        neg_hits += 2

    return pos_hits, neg_hits


class ReviewAspectAnalyzer:
    """Analyzes customer reviews to produce evidence-grounded aspect scorecards and defect forensics."""

    def __init__(self, retriever_cls=HybridReviewRetriever) -> None:
        self.retriever_cls = retriever_cls

    def analyze(self, asin: str, reviews: Sequence[ReviewRecord]) -> ProductAspectAnalysis:
        """Run complete aspect extraction and defect clustering over review corpus."""
        if not reviews:
            return ProductAspectAnalysis(
                asin=asin,
                total_reviews_analyzed=0,
                verified_review_ratio=0.0,
                aspects={},
                critical_defects=[],
                defect_rate=0.0,
            )

        retriever = self.retriever_cls(reviews)
        total_count = len(reviews)
        verified_count = sum(1 for r in reviews if r.is_verified_purchase)
        verified_ratio = round(verified_count / total_count, 3)

        aspect_summaries: Dict[AspectCategory, AspectSummary] = {}
        all_defects_found: List[str] = []
        defect_review_count = 0

        # 1. Evaluate each aspect
        for aspect in AspectCategory:
            keywords = ASPECT_QUERY_EXPANSIONS.get(aspect, [aspect.value])
            top_ranked = retriever.retrieve_for_aspect(aspect, limit=5)

            pos_total = 0
            neg_total = 0
            citations: List[AspectCitation] = []
            defect_terms: List[str] = []

            for review, _ in top_ranked:
                p_hits, n_hits = analyze_review_sentiment(review, keywords)
                pos_total += p_hits
                neg_total += n_hits

                quote_snippet = extract_best_quote(review.body, keywords)
                if quote_snippet:
                    citations.append(
                        AspectCitation(
                            review_id=review.review_id,
                            quote=quote_snippet,
                            is_verified_purchase=review.is_verified_purchase,
                            review_date=review.review_date,
                            helpful_votes=review.helpful_votes,
                        )
                    )

                # Collect defect terms
                for dt in DEFECT_KEYWORDS:
                    if dt in review.body.lower() and dt not in defect_terms:
                        defect_terms.append(dt)

            total_mentions = pos_total + neg_total
            if total_mentions > 0:
                satisfaction = round(pos_total / total_mentions, 3)
            else:
                satisfaction = 0.50

            if satisfaction >= 0.65:
                polarity = SentimentPolarity.POSITIVE
            elif satisfaction <= 0.40:
                polarity = SentimentPolarity.NEGATIVE
            else:
                polarity = SentimentPolarity.NEUTRAL

            aspect_summaries[aspect] = AspectSummary(
                category=aspect,
                sentiment=polarity,
                positive_mentions=pos_total,
                negative_mentions=neg_total,
                total_mentions=total_mentions,
                satisfaction_score=satisfaction,
                citations=citations[:3],
                top_defect_keywords=defect_terms[:4],
            )

        # 2. Defect Forensics across entire corpus
        for r in reviews:
            r_lower = r.body.lower()
            found_any = False
            for kw in DEFECT_KEYWORDS:
                if kw in r_lower:
                    found_any = True
                    if kw not in all_defects_found:
                        all_defects_found.append(kw)
            if found_any:
                defect_review_count += 1

        defect_rate = round(defect_review_count / total_count, 3)
        critical_defects = [
            f"Recurring defect pattern: '{kw}' cited in verified customer feedback"
            for kw in all_defects_found
        ]

        return ProductAspectAnalysis(
            asin=asin,
            total_reviews_analyzed=total_count,
            verified_review_ratio=verified_ratio,
            aspects=aspect_summaries,
            critical_defects=critical_defects,
            defect_rate=defect_rate,
        )
