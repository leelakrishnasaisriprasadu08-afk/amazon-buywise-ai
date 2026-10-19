/**
 * TypeScript domain contracts matching BuyWise AI backend models.
 */

export interface ProductIdentity {
  asin: string;
  marketplace: string;
  canonical_url: string;
  title: string | null;
  brand: string | null;
  category: string | null;
  created_at: string;
}

export interface CatalogProduct {
  asin: string;
  title: string;
  brand: string;
  category: string;
  price: string | number;
  list_price: string | number;
  currency: string;
  rating: string | number;
  review_count: number;
  image_url: string;
  prime: boolean;
  deal_badge?: string | null;
  ai_verdict: DecisionVerdict;
  ai_verdict_summary: string;
  specs: string[];
  marketplace?: string;
  is_fixture?: boolean;
}

export interface PriceMetrics {
  asin: string;
  currency: string;
  sample_count: number;
  current_price: string;
  min_price: string;
  max_price: string;
  median_price: string;
  percentile_rank: string;
  rolling_30d_median: string | null;
  rolling_90d_median: string | null;
  effective_discount_pct: string | null;
  is_artificial_discount: boolean;
  is_all_time_low: boolean;
  computed_at: string;
}

export type AspectCategory =
  | 'battery'
  | 'build_quality'
  | 'display'
  | 'performance'
  | 'value'
  | 'usability'
  | 'defect';

export type SentimentPolarity = 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE';

export interface AspectCitation {
  review_id: string;
  quote: string;
  is_verified_purchase: boolean;
  review_date: string;
  helpful_votes: number;
}

export interface AspectSummary {
  category: AspectCategory;
  sentiment: SentimentPolarity;
  positive_mentions: number;
  negative_mentions: number;
  total_mentions: number;
  satisfaction_score: number;
  citations: AspectCitation[];
  top_defect_keywords: string[];
}

export interface ProductAspectAnalysis {
  asin: string;
  total_reviews_analyzed: number;
  verified_review_ratio: number;
  aspects: Record<AspectCategory, AspectSummary>;
  critical_defects: string[];
  defect_rate: number;
}

export interface FeatureDelta {
  feature_name: string;
  target_value: string;
  alternative_value: string;
  advantage: 'alternative' | 'target' | 'neutral';
  impact_summary: string;
}

export interface AlternativeRecommendation {
  target_asin: string;
  alternative_asin: string;
  alternative_title: string;
  target_price: string;
  alternative_price: string;
  price_delta: string;
  currency: string;
  key_advantages: string[];
  trade_offs: string[];
  feature_deltas: FeatureDelta[];
  is_strictly_better: boolean;
}

export type DecisionVerdict = 'BUY' | 'WAIT' | 'DONT_BUY' | 'INSUFFICIENT_EVIDENCE';

export interface ProvenanceEnvelope<T> {
  evidence_id: string;
  source_type: string;
  source_url: string;
  retrieved_at: string;
  raw_hash_sha256: string | null;
  confidence_score: number;
  is_verified_source: boolean;
  is_fixture: boolean;
  payload: T;
}

export interface RecommendationReport {
  asin: string;
  verdict: DecisionVerdict;
  confidence: number;
  summary: string;
  product: ProductIdentity;
  price_metrics: PriceMetrics | null;
  aspect_analysis: ProductAspectAnalysis | null;
  alternative: AlternativeRecommendation | null;
  evidence_envelopes: ProvenanceEnvelope<unknown>[];
  key_reasons: string[];
  risks_and_caveats: string[];
  missing_evidence: string[];
  generated_at: string;
}

export interface StreamingMilestone {
  step: number;
  stage: string;
  message: string;
  data?: unknown;
}
