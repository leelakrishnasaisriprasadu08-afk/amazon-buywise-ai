"""REST API endpoints for BuyWise Phase 1 Foundation."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from buywise.core.orchestrator import AgentDecisionOrchestrator
from buywise.engine.exceptions import (
    CurrencyMismatchError,
    InsufficientPriceDataError,
    InvalidASINError,
    InvalidPriceDataError,
)
from buywise.engine.aspect_analyzer import ReviewAspectAnalyzer
from buywise.engine.competitor_matcher import CompetitorComparisonEngine
from buywise.engine.pricing import compute_price_metrics
from buywise.models.aspect import ProductAspectAnalysis
from buywise.models.catalog import CatalogProduct
from buywise.models.comparison import AlternativeRecommendation
from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceMetrics
from buywise.models.provenance import ProvenanceEnvelope, SourceType
from buywise.models.report import RecommendationReport
from buywise.parsers.asin import create_product_identity, parse_asin_and_marketplace
from buywise.providers.mock_provider import MockFixtureProvider
from buywise.providers.ollama_provider import OllamaProvider
from buywise.providers.realtime_amazon import RealtimeAmazonProvider

router = APIRouter()
_fixture_provider = MockFixtureProvider()
_realtime_provider = RealtimeAmazonProvider()
_aspect_analyzer = ReviewAspectAnalyzer()
_comparison_engine = CompetitorComparisonEngine()
_ollama_provider = OllamaProvider()
_orchestrator = AgentDecisionOrchestrator(
    provider=_fixture_provider,
    aspect_analyzer=_aspect_analyzer,
    comparison_engine=_comparison_engine,
)


class ParseProductRequest(BaseModel):
    """Request payload for product identification."""

    input_text: str = Field(
        ...,
        description="Raw Amazon ASIN or full product URL",
        examples=["https://www.amazon.com/dp/B08N5WRWNW", "B08N5WRWNW"],
    )


class ParseProductResponse(BaseModel):
    """Response containing parsed canonical identity and extraction metadata."""

    asin: str
    marketplace: str
    canonical_url: str
    product: ProductIdentity


class AlexaChatRequest(BaseModel):
    """Voice command payload from Alexa+ speech agent."""

    user_prompt: str = Field(..., description="Transcribed speech command from user")
    current_asin: Optional[str] = Field(default=None, description="Currently selected or audited ASIN")


class AlexaChatResponse(BaseModel):
    """Response payload for Alexa+ voice output and action dispatch."""

    speech_text: str
    action: str  # "AUDIT", "SEARCH", "INFO"
    target_asin: Optional[str] = None
    search_query: Optional[str] = None
    ollama_active: bool


@router.get("/health", tags=["System"])
def health_check() -> dict:
    """System liveness probe."""
    return {"status": "ok", "service": "BuyWise AI Foundation", "version": "0.1.0"}


@router.get("/api/v1/ollama/status", tags=["Ollama & Alexa+"])
def get_ollama_status() -> dict:
    """Inspect local Ollama daemon connectivity and installed models."""
    return {
        "available": _ollama_provider.is_available(),
        "host": _ollama_provider.host,
        "default_model": _ollama_provider.default_model,
        "installed_models": _ollama_provider.list_installed_models(),
    }


@router.post(
    "/api/v1/alexa/chat",
    response_model=AlexaChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Ollama & Alexa+"],
)
def alexa_chat(payload: AlexaChatRequest) -> AlexaChatResponse:
    """Process natural language voice commands via Alexa+ and synthesize evidence-grounded audio response."""
    prompt = payload.user_prompt.strip()
    prompt_lower = prompt.lower()

    target_asin = payload.current_asin
    action = "INFO"
    search_query = None

    # Detect voice intent
    if any(k in prompt_lower for k in ["audit", "inspect", "analyze", "check deal", "defect", "verify", "is it a deal", "should i buy"]):
        action = "AUDIT"
        cand_asin = _fixture_provider.find_best_asin_for_query(prompt)
        if cand_asin:
            target_asin = cand_asin

    elif any(k in prompt_lower for k in ["search", "find", "show me", "look for", "laptop", "mouse", "phone", "headphone", "earbud", "charger"]):
        action = "SEARCH"
        clean_q = prompt
        for noise in ["alexa", "please", "search for", "find me", "show me", "look for", "search", "can you"]:
            clean_q = clean_q.lower().replace(noise, "")
        search_query = clean_q.strip() or prompt

    # Collect product context if target_asin exists
    product_title = None
    verdict_str = None
    price_info = None
    reasons = []

    if target_asin:
        card = _fixture_provider.get_catalog_product(target_asin)
        if card:
            product_title = card.title
            verdict_str = card.ai_verdict.value
            price_info = f"{card.currency} {card.price} (List: {card.list_price})"
            reasons = [card.ai_verdict_summary]

    speech = _ollama_provider.generate_alexa_response(
        user_prompt=prompt,
        verdict=verdict_str,
        product_title=product_title,
        price_summary=price_info,
        key_reasons=reasons,
    )

    return AlexaChatResponse(
        speech_text=speech,
        action=action,
        target_asin=target_asin,
        search_query=search_query,
        ollama_active=_ollama_provider.is_available(),
    )


@router.get(
    "/api/v1/realtime/status",
    tags=["Product Catalog"],
)
def get_realtime_status() -> dict:
    """Check OpenWebNinja real-time Amazon API configuration status (masked for security)."""
    return {
        "configured": _realtime_provider.is_configured,
        "masked_key": _realtime_provider.masked_key,
        "provider": "OpenWebNinja Real-Time Suite",
        "supported_apis": [
            "realtime-amazon-data/search",
            "realtime-product-search/search-light-v2",
            "local-business-data/search",
        ],
    }


@router.get(
    "/api/v1/pricing/cross-check",
    tags=["Product Pricing & MSRP"],
)
def cross_check_pricing(
    q: str = Query(..., description="Product name or keywords to cross-check across web and retailers"),
    country: Optional[str] = Query(default="US", description="Country code"),
) -> dict:
    """Cross-check Amazon pricing against multi-store web data and true manufacturer MSRP using OpenWebNinja search-light-v2."""
    items = _realtime_provider.search_web_products(query=q, country=country)
    return {
        "query": q,
        "count": len(items),
        "results": items,
        "provider": "OpenWebNinja Product Search Light v2",
    }


@router.get(
    "/api/v1/local-stores/search",
    tags=["Local Warranty & Stores"],
)
def search_local_stores(
    query: str = Query(..., description="E.g. 'Apple Store San Francisco' or 'Sony Service Center New York'"),
    limit: Optional[int] = Query(default=6, ge=1, le=20),
) -> dict:
    """Find local authorized brand stores, service centers, and verified repair hubs via OpenWebNinja local-business-data."""
    stores = _realtime_provider.search_local_businesses(query=query, limit=limit)
    return {
        "query": query,
        "count": len(stores),
        "stores": stores,
        "provider": "OpenWebNinja Local Business API",
    }


@router.get(
    "/api/v1/search",
    response_model=List[CatalogProduct],
    status_code=status.HTTP_200_OK,
    tags=["Product Catalog"],
)
def search_products(
    q: Optional[str] = Query(default=None, description="Search query matching product title, brand, or specifications"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    verdict: Optional[str] = Query(default=None, description="Verdict filter (BUY, WAIT, DONT_BUY)"),
    country: Optional[str] = Query(default="US", description="Amazon marketplace country code"),
) -> List[CatalogProduct]:
    """Search and browse Amazon products with instant AI intelligence verdict summaries.
    
    Queries OpenWebNinja real-time API server-side when configured, with cached fallback
    to local golden catalog products.
    """
    if q and q.strip() and _realtime_provider.is_configured:
        realtime_items = _realtime_provider.search_products(query=q.strip(), country=country)
        if realtime_items:
            # If category or verdict filter is applied, filter realtime results
            filtered = realtime_items
            if verdict:
                filtered = [p for p in filtered if p.ai_verdict.value == verdict.upper()]
            if filtered:
                return filtered

    # Resilient fallback to local catalog
    return _fixture_provider.search_catalog(query=q, category=category, verdict=verdict)


@router.get(
    "/api/v1/products",
    response_model=List[CatalogProduct],
    status_code=status.HTTP_200_OK,
    tags=["Product Catalog"],
)
def list_products(
    category: Optional[str] = Query(default=None, description="Category filter"),
) -> List[CatalogProduct]:
    """Retrieve all featured Amazon catalog products."""
    return _fixture_provider.search_catalog(query=None, category=category)


@router.get(
    "/api/v1/products/{asin}/card",
    response_model=CatalogProduct,
    status_code=status.HTTP_200_OK,
    tags=["Product Catalog"],
)
def get_product_card(asin: str) -> CatalogProduct:
    """Retrieve product card view for a specific ASIN."""
    card = _fixture_provider.get_catalog_product(asin)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ASIN '{asin}' not found in catalog.",
        )
    return card


@router.post(
    "/api/v1/parse-product",
    response_model=ParseProductResponse,
    status_code=status.HTTP_200_OK,
    tags=["Product Identification"],
)
def parse_product(payload: ParseProductRequest) -> ParseProductResponse:
    """Parse an arbitrary Amazon URL or raw ASIN into canonical product identity."""
    try:
        asin, marketplace = parse_asin_and_marketplace(payload.input_text)
        identity = create_product_identity(payload.input_text)
        return ParseProductResponse(
            asin=asin,
            marketplace=marketplace,
            canonical_url=identity.canonical_url,
            product=identity,
        )
    except InvalidASINError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to parse product: {str(err)}",
        ) from err


@router.get(
    "/api/v1/products/{asin}/price-metrics",
    response_model=ProvenanceEnvelope[PriceMetrics],
    status_code=status.HTTP_200_OK,
    tags=["Pricing Intelligence"],
)
def get_product_price_metrics(
    asin: str,
    lookback_days: int = Query(default=90, ge=1, le=730, description="Historical lookback window in days"),
) -> ProvenanceEnvelope[PriceMetrics]:
    """Calculate deterministic price metrics from historical snapshots using the fixture provider."""
    try:
        # Retrieve historical price envelope
        history_envelope = _fixture_provider.get_price_history(asin=asin, lookback_days=lookback_days)
        snapshots = history_envelope.payload

        # Compute deterministic metrics
        metrics = compute_price_metrics(snapshots=snapshots)

        # Wrap in ProvenanceEnvelope with honesty flags preserved from history provider
        return ProvenanceEnvelope[PriceMetrics](
            source_type=history_envelope.source_type,
            source_url=history_envelope.source_url,
            raw_hash_sha256=history_envelope.raw_hash_sha256,
            confidence_score=history_envelope.confidence_score,
            is_verified_source=history_envelope.is_verified_source,
            is_fixture=history_envelope.is_fixture,
            payload=metrics,
        )

    except InvalidASINError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ASIN '{asin}' not found in fixture catalog: {str(err)}",
        ) from err
    except (InsufficientPriceDataError, InvalidPriceDataError) as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient price records for metrics calculation: {str(err)}",
        ) from err
    except CurrencyMismatchError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency mismatch error: {str(err)}",
        ) from err


@router.get(
    "/api/v1/products/{asin}/aspects",
    response_model=ProvenanceEnvelope[ProductAspectAnalysis],
    status_code=status.HTTP_200_OK,
    tags=["Review Forensics"],
)
def get_product_aspect_analysis(
    asin: str,
    limit: int = Query(default=100, ge=1, le=500, description="Max reviews to evaluate"),
) -> ProvenanceEnvelope[ProductAspectAnalysis]:
    """Retrieve review aspect sentiment, verbatim citations, and recurring defect forensics."""
    try:
        review_envelope = _fixture_provider.get_reviews(asin=asin, limit=limit)
        reviews = review_envelope.payload

        analysis = _aspect_analyzer.analyze(asin=asin, reviews=reviews)

        return ProvenanceEnvelope[ProductAspectAnalysis](
            source_type=review_envelope.source_type,
            source_url=review_envelope.source_url,
            raw_hash_sha256=review_envelope.raw_hash_sha256,
            confidence_score=review_envelope.confidence_score,
            is_verified_source=review_envelope.is_verified_source,
            is_fixture=review_envelope.is_fixture,
            payload=analysis,
        )
    except InvalidASINError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ASIN '{asin}' reviews not found in fixture catalog: {str(err)}",
        ) from err


@router.get(
    "/api/v1/products/{asin}/alternatives",
    response_model=ProvenanceEnvelope[AlternativeRecommendation],
    status_code=status.HTTP_200_OK,
    tags=["Product Comparison"],
)
def get_product_alternative_recommendation(
    asin: str,
    alternative_asin: Optional[str] = Query(default=None, description="Optional specific competitor ASIN to evaluate against"),
) -> ProvenanceEnvelope[AlternativeRecommendation]:
    """Evaluate target product against candidate alternatives to find strictly better recommendations."""
    try:
        target_prod = _fixture_provider.get_product(asin).payload
        target_reviews = _fixture_provider.get_reviews(asin).payload
        target_prices = _fixture_provider.get_price_history(asin).payload
        target_price = target_prices[-1].amount if target_prices else Decimal("0.0")
        target_analysis = _aspect_analyzer.analyze(asin, target_reviews)

        # Default mapping for demo if alternative_asin not specified
        alt_id = alternative_asin
        if not alt_id:
            if asin.upper() == "B0COLLEGE1":
                alt_id = "B0COLLEGE2"
            else:
                alt_id = "B08N5WRWNW"

        alt_prod = _fixture_provider.get_product(alt_id).payload
        alt_reviews = _fixture_provider.get_reviews(alt_id).payload
        alt_prices = _fixture_provider.get_price_history(alt_id).payload
        alt_price = alt_prices[-1].amount if alt_prices else Decimal("0.0")
        alt_analysis = _aspect_analyzer.analyze(alt_id, alt_reviews)

        recommendation = _comparison_engine.compare_products(
            target_product=target_prod,
            target_price=target_price,
            target_analysis=target_analysis,
            alternative_product=alt_prod,
            alternative_price=alt_price,
            alternative_analysis=alt_analysis,
            currency=target_prices[-1].currency if target_prices else "USD",
        )

        return ProvenanceEnvelope[AlternativeRecommendation](
            source_type=SourceType.MOCK_FIXTURE,
            source_url=f"mock://fixture/comparison/{asin}_vs_{alt_id}",
            confidence_score=1.0,
            is_verified_source=False,
            is_fixture=True,
            payload=recommendation,
        )
    except InvalidASINError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product or alternative ASIN not found: {str(err)}",
        ) from err


class AnalyzeProductRequest(BaseModel):
    """Request payload for full product intelligence analysis."""

    input_text: str = Field(..., description="ASIN or Amazon product URL")
    alternative_asin: Optional[str] = Field(default=None, description="Optional competitor ASIN to evaluate against")


@router.post(
    "/api/v1/analyze",
    response_model=RecommendationReport,
    status_code=status.HTTP_200_OK,
    tags=["Decision Engine"],
)
def analyze_product_sync(payload: AnalyzeProductRequest) -> RecommendationReport:
    """Execute synchronous 6-stage shopping decision pipeline."""
    try:
        return _orchestrator.run_pipeline(
            input_str=payload.input_text, alternative_asin=payload.alternative_asin
        )
    except InvalidASINError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {str(err)}",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(err)}",
        ) from err


@router.get(
    "/api/v1/analyze/stream",
    tags=["Decision Engine"],
)
async def analyze_product_stream(
    input_text: str = Query(..., description="ASIN or Amazon product URL"),
    alternative_asin: Optional[str] = Query(default=None, description="Optional competitor ASIN"),
):
    """Stream real-time pipeline milestone telemetry and final decision report via Server-Sent Events (SSE)."""
    return StreamingResponse(
        _orchestrator.stream_pipeline(input_str=input_text, alternative_asin=alternative_asin),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
