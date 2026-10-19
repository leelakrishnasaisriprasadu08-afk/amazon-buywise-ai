import React from 'react';
import { ArrowRight, Check, Award, ArrowUpRight } from 'lucide-react';
import type { AlternativeRecommendation } from '../types/buywise';

interface CompetitorCardProps {
  alternative: AlternativeRecommendation | null;
  onAuditAlternative?: (asin: string) => void;
}

export const CompetitorCard: React.FC<CompetitorCardProps> = ({
  alternative,
  onAuditAlternative,
}) => {
  if (!alternative) return null;

  return (
    <div className="card competitor-card">
      <div className="card-header">
        <div className="card-title-group">
          <Award size={22} className="card-icon highlight-icon" />
          <div>
            <h3>Competitor Comparison: Superior Alternative Found</h3>
            <span className="competitor-subtitle">
              BuyWise AI identified a strictly superior product in the same price tier
            </span>
          </div>
        </div>

        {parseFloat(alternative.price_delta) > 0 && (
          <span className="savings-badge">
            Saves {alternative.currency} {alternative.price_delta}
          </span>
        )}
      </div>

      <div className="alternative-product-banner">
        <div className="alt-title-box">
          <span className="alt-tag">RECOMMENDED UPGRADE</span>
          <h4 className="alt-product-title">{alternative.alternative_title}</h4>
          <span className="alt-asin">ASIN: {alternative.alternative_asin}</span>
        </div>

        <div className="alt-price-box">
          <span className="alt-price-label">Alternative Price</span>
          <span className="alt-price-value">
            {alternative.currency} {alternative.alternative_price}
          </span>
          <span className="target-price-ref">
            Target was: {alternative.currency} {alternative.target_price}
          </span>
        </div>

        {onAuditAlternative && (
          <button
            className="btn-switch-audit"
            onClick={() => onAuditAlternative(alternative.alternative_asin)}
            type="button"
          >
            <span>Audit This Model</span>
            <ArrowRight size={14} />
          </button>
        )}
      </div>

      {/* Feature Delta Table */}
      {alternative.feature_deltas.length > 0 && (
        <div className="comparison-table-wrapper">
          <h5 className="table-heading">Head-to-Head Specification & Quality Delta</h5>
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Feature / Metric</th>
                <th>Target Product</th>
                <th>Alternative Product</th>
                <th>Why It Matters</th>
              </tr>
            </thead>
            <tbody>
              {alternative.feature_deltas.map((delta, i) => (
                <tr key={i} className={`row-${delta.advantage}`}>
                  <td className="feature-cell">{delta.feature_name}</td>
                  <td className="target-val-cell">{delta.target_value}</td>
                  <td className="alt-val-cell">
                    <span>{delta.alternative_value}</span>
                    {delta.advantage === 'alternative' && (
                      <Check size={14} className="cell-win-icon" />
                    )}
                  </td>
                  <td className="impact-cell">{delta.impact_summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Advantages list */}
      <div className="advantages-box">
        <h5 className="advantages-title">Key Advantages of Switching</h5>
        <div className="advantages-grid">
          {alternative.key_advantages.map((adv, i) => (
            <div key={i} className="advantage-item">
              <ArrowUpRight size={15} className="advantage-arrow" />
              <span>{adv}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
