"""Deterministic competitor comparison and alternative product recommendation engine."""

from decimal import Decimal
from typing import Optional

from buywise.models.aspect import AspectCategory, ProductAspectAnalysis
from buywise.models.comparison import AlternativeRecommendation, FeatureDelta
from buywise.models.identity import ProductIdentity


class CompetitorComparisonEngine:
    """Evaluates target product against competitor alternatives to generate head-to-head delta analysis."""

    def compare_products(
        self,
        target_product: ProductIdentity,
        target_price: Decimal,
        target_analysis: ProductAspectAnalysis,
        alternative_product: ProductIdentity,
        alternative_price: Decimal,
        alternative_analysis: ProductAspectAnalysis,
        currency: str = "USD",
    ) -> AlternativeRecommendation:
        """Execute head-to-head delta comparison between target and alternative."""
        price_delta = target_price - alternative_price  # Positive = alternative saves money

        feature_deltas = []
        key_advantages = []
        trade_offs = []

        # 1. Price comparison
        if price_delta > Decimal("0.0"):
            feature_deltas.append(
                FeatureDelta(
                    feature_name="Effective Price",
                    target_value=f"{currency} {target_price}",
                    alternative_value=f"{currency} {alternative_price}",
                    advantage="alternative",
                    impact_summary=f"Alternative is cheaper by {currency} {price_delta}.",
                )
            )
            key_advantages.append(f"Saves {currency} {price_delta} compared to target product")
        elif price_delta < Decimal("0.0"):
            diff = abs(price_delta)
            feature_deltas.append(
                FeatureDelta(
                    feature_name="Effective Price",
                    target_value=f"{currency} {target_price}",
                    alternative_value=f"{currency} {alternative_price}",
                    advantage="target",
                    impact_summary=f"Alternative costs {currency} {diff} more.",
                )
            )
            trade_offs.append(f"Requires an additional investment of {currency} {diff}")
        else:
            feature_deltas.append(
                FeatureDelta(
                    feature_name="Effective Price",
                    target_value=f"{currency} {target_price}",
                    alternative_value=f"{currency} {alternative_price}",
                    advantage="neutral",
                    impact_summary="Identical effective price.",
                )
            )

        # 2. Defect Rate comparison
        t_defect = target_analysis.defect_rate
        a_defect = alternative_analysis.defect_rate
        if a_defect < t_defect:
            key_advantages.append(
                f"Lower defect recurrence rate ({a_defect * 100:.1f}% vs {t_defect * 100:.1f}%)"
            )
            feature_deltas.append(
                FeatureDelta(
                    feature_name="Verified Defect Rate",
                    target_value=f"{t_defect * 100:.1f}%",
                    alternative_value=f"{a_defect * 100:.1f}%",
                    advantage="alternative",
                    impact_summary="Significantly lower risk of hardware or structural breakdown.",
                )
            )
        elif a_defect > t_defect:
            trade_offs.append(
                f"Slightly higher reported defect rate ({a_defect * 100:.1f}% vs {t_defect * 100:.1f}%)"
            )

        # 3. Core Aspect comparisons
        for aspect in [AspectCategory.PERFORMANCE, AspectCategory.BATTERY, AspectCategory.DISPLAY, AspectCategory.BUILD_QUALITY]:
            t_asp = target_analysis.aspects.get(aspect)
            a_asp = alternative_analysis.aspects.get(aspect)
            if t_asp and a_asp:
                if a_asp.satisfaction_score > (t_asp.satisfaction_score + 0.10):
                    feature_deltas.append(
                        FeatureDelta(
                            feature_name=f"{aspect.value.replace('_', ' ').title()} Satisfaction",
                            target_value=f"{t_asp.satisfaction_score * 100:.0f}%",
                            alternative_value=f"{a_asp.satisfaction_score * 100:.0f}%",
                            advantage="alternative",
                            impact_summary=f"Verified buyers report significantly higher {aspect.value} satisfaction.",
                        )
                    )
                    key_advantages.append(
                        f"Superior {aspect.value.replace('_', ' ')} satisfaction ({a_asp.satisfaction_score * 100:.0f}% vs {t_asp.satisfaction_score * 100:.0f}%)"
                    )
                elif t_asp.satisfaction_score > (a_asp.satisfaction_score + 0.10):
                    feature_deltas.append(
                        FeatureDelta(
                            feature_name=f"{aspect.value.replace('_', ' ').title()} Satisfaction",
                            target_value=f"{t_asp.satisfaction_score * 100:.0f}%",
                            alternative_value=f"{a_asp.satisfaction_score * 100:.0f}%",
                            advantage="target",
                            impact_summary=f"Target product scored higher on {aspect.value}.",
                        )
                    )
                    trade_offs.append(f"Lower score on {aspect.value.replace('_', ' ')}")

        is_strictly_better = (
            price_delta >= Decimal("0.0")
            and len(key_advantages) >= 2
            and len(trade_offs) == 0
        )

        return AlternativeRecommendation(
            target_asin=target_product.asin,
            alternative_asin=alternative_product.asin,
            alternative_title=alternative_product.title or "Alternative Product",
            target_price=target_price,
            alternative_price=alternative_price,
            price_delta=price_delta,
            currency=currency,
            key_advantages=key_advantages,
            trade_offs=trade_offs,
            feature_deltas=feature_deltas,
            is_strictly_better=is_strictly_better,
        )
