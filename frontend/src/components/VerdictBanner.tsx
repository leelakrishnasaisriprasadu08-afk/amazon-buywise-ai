import React from 'react';
import {
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  AlertOctagon,
} from 'lucide-react';
import type { DecisionVerdict, RecommendationReport } from '../types/buywise';

interface VerdictBannerProps {
  report: RecommendationReport;
}

export const VerdictBanner: React.FC<VerdictBannerProps> = ({ report }) => {
  const getVerdictDetails = (verdict: DecisionVerdict) => {
    switch (verdict) {
      case 'BUY':
        return {
          label: 'BUY RECOMMENDATION',
          badgeClass: 'verdict-buy',
          icon: <CheckCircle2 size={28} className="verdict-icon" />,
          subtitle: 'Genuine verified deal near historical low with strong customer satisfaction.',
        };
      case 'WAIT':
        return {
          label: 'WAIT RECOMMENDATION',
          badgeClass: 'verdict-wait',
          icon: <Clock size={28} className="verdict-icon" />,
          subtitle: 'Current price is above historical median or an artificial pre-sale markup was detected.',
        };
      case 'DONT_BUY':
        return {
          label: "DON'T BUY RECOMMENDATION",
          badgeClass: 'verdict-dont-buy',
          icon: <XCircle size={28} className="verdict-icon" />,
          subtitle: 'Recurring hardware defects detected or a strictly superior alternative is available.',
        };
      case 'INSUFFICIENT_EVIDENCE':
        return {
          label: 'INSUFFICIENT EVIDENCE',
          badgeClass: 'verdict-insufficient',
          icon: <AlertTriangle size={28} className="verdict-icon" />,
          subtitle: 'Sample size of verified reviews or historical pricing is below confidence thresholds.',
        };
    }
  };

  const details = getVerdictDetails(report.verdict);
  const confidencePercent = Math.round(report.confidence * 100);

  return (
    <div className={`verdict-card ${details.badgeClass}`}>
      <div className="verdict-header">
        <div className="verdict-badge-row">
          <div className="verdict-pill">
            {details.icon}
            <span className="verdict-label">{details.label}</span>
          </div>

          <div className="confidence-meter-group">
            <span className="confidence-label">Decision Confidence</span>
            <div className="confidence-bar-wrapper">
              <div
                className="confidence-bar-fill"
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
            <span className="confidence-value">{confidencePercent}%</span>
          </div>
        </div>

        <div className="product-meta-row">
          <h2 className="product-title">{report.product.title || report.product.asin}</h2>
          <div className="product-tags">
            <span className="meta-tag asin-tag">ASIN: {report.product.asin}</span>
            <span className="meta-tag marketplace-tag">{report.product.marketplace}</span>
            {report.product.canonical_url && (
              <a
                href={report.product.canonical_url}
                target="_blank"
                rel="noopener noreferrer"
                className="meta-tag link-tag"
              >
                <span>View on Amazon</span>
                <ExternalLink size={12} />
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="verdict-body">
        <p className="verdict-summary">{report.summary}</p>

        {report.key_reasons.length > 0 && (
          <div className="reasons-block">
            <h4 className="block-title">
              <ShieldCheck size={16} className="block-title-icon positive-icon" />
              <span>Core Supporting Evidence</span>
            </h4>
            <ul className="reasons-list">
              {report.key_reasons.map((reason, idx) => (
                <li key={idx} className="reason-item">
                  <span className="bullet-dot" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {report.risks_and_caveats.length > 0 && (
          <div className="risks-block">
            <h4 className="block-title">
              <AlertOctagon size={16} className="block-title-icon warning-icon" />
              <span>Documented Risks & Caveats</span>
            </h4>
            <ul className="risks-list">
              {report.risks_and_caveats.map((risk, idx) => (
                <li key={idx} className="risk-item">
                  <span className="bullet-dot warning-dot" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
