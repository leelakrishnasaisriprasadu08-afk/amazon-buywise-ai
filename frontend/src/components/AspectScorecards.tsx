import React, { useState } from 'react';
import {
  Activity,
  CheckCircle,
  AlertTriangle,
  Quote,
  Battery,
  Cpu,
  Monitor,
  Wrench,
  ThumbsUp,
} from 'lucide-react';
import type { AspectCategory, ProductAspectAnalysis } from '../types/buywise';

interface AspectScorecardsProps {
  analysis: ProductAspectAnalysis | null;
}

export const AspectScorecards: React.FC<AspectScorecardsProps> = ({ analysis }) => {
  const [selectedCategory, setSelectedCategory] = useState<AspectCategory>('performance');

  if (!analysis || analysis.total_reviews_analyzed === 0) {
    return (
      <div className="card aspect-card empty-card">
        <div className="card-header">
          <Activity size={20} className="card-icon" />
          <h3>Review Aspect Forensics</h3>
        </div>
        <p className="empty-notice">
          Insufficient customer reviews found to perform aspect sentiment decomposition.
        </p>
      </div>
    );
  }

  const getAspectIcon = (cat: AspectCategory) => {
    switch (cat) {
      case 'battery':
        return <Battery size={16} />;
      case 'performance':
        return <Cpu size={16} />;
      case 'display':
        return <Monitor size={16} />;
      case 'build_quality':
      case 'defect':
        return <Wrench size={16} />;
      default:
        return <Activity size={16} />;
    }
  };

  const aspectsList = Object.values(analysis.aspects);
  const currentAspect = analysis.aspects[selectedCategory] || aspectsList[0];

  return (
    <div className="card aspect-card">
      <div className="card-header">
        <div className="card-title-group">
          <Activity size={20} className="card-icon" />
          <h3>Verified Review Aspect Forensics</h3>
        </div>
        <div className="verified-ratio-badge">
          <CheckCircle size={14} className="verified-check" />
          <span>{Math.round(analysis.verified_review_ratio * 100)}% Verified Purchasers</span>
        </div>
      </div>

      {analysis.defect_rate > 0.15 && (
        <div className="alert-banner alert-danger">
          <AlertTriangle size={18} className="alert-icon" />
          <div className="alert-text">
            <strong>Critical Hardware Defect Pattern ({Math.round(analysis.defect_rate * 100)}%):</strong>
            <span>
              {analysis.critical_defects.join('; ') || 'High recurring failure incidence detected in reviews.'}
            </span>
          </div>
        </div>
      )}

      {/* Aspect Category Tabs */}
      <div className="aspect-tabs-row">
        {aspectsList.map((asp) => {
          const satisfactionPercent = Math.round(asp.satisfaction_score * 100);
          const isSelected = asp.category === selectedCategory;
          return (
            <button
              key={asp.category}
              className={`aspect-tab-btn ${isSelected ? 'active-tab' : ''}`}
              onClick={() => setSelectedCategory(asp.category)}
              type="button"
            >
              <span className="aspect-tab-icon">{getAspectIcon(asp.category)}</span>
              <span className="aspect-tab-name">
                {asp.category.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </span>
              <span
                className={`aspect-tab-score ${
                  satisfactionPercent >= 65 ? 'score-high' : satisfactionPercent <= 40 ? 'score-low' : ''
                }`}
              >
                {satisfactionPercent}%
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Aspect Details & Grounded Citations */}
      {currentAspect && (
        <div className="aspect-details-box">
          <div className="aspect-details-header">
            <div>
              <h4 className="aspect-focus-title">
                {currentAspect.category.replace('_', ' ').toUpperCase()} SATISFACTION
              </h4>
              <span className="aspect-mention-counts">
                {currentAspect.positive_mentions} positive mentions • {currentAspect.negative_mentions} negative mentions
              </span>
            </div>

            <div className="aspect-meter-wrapper">
              <div
                className="aspect-meter-fill"
                style={{
                  width: `${Math.round(currentAspect.satisfaction_score * 100)}%`,
                  backgroundColor:
                    currentAspect.satisfaction_score >= 0.65
                      ? 'var(--accent-emerald)'
                      : currentAspect.satisfaction_score <= 0.40
                      ? 'var(--accent-rose)'
                      : 'var(--accent-amber)',
                }}
              />
            </div>
          </div>

          <div className="citations-container">
            <h5 className="citations-header">Verbatim Grounded Citations (Direct from Verified Shoppers)</h5>
            {currentAspect.citations.length === 0 ? (
              <p className="no-citations">No direct quote excerpts extracted for this category.</p>
            ) : (
              <div className="citations-grid">
                {currentAspect.citations.map((cite) => (
                  <div key={cite.review_id} className="citation-card">
                    <Quote size={16} className="citation-quote-icon" />
                    <p className="citation-text">"{cite.quote}"</p>
                    <div className="citation-meta">
                      {cite.is_verified_purchase && (
                        <span className="citation-badge-verified">
                          <CheckCircle size={12} />
                          <span>Verified Purchase</span>
                        </span>
                      )}
                      <span className="citation-id">ID: {cite.review_id}</span>
                      {cite.helpful_votes > 0 && (
                        <span className="citation-helpful">
                          <ThumbsUp size={11} />
                          <span>{cite.helpful_votes}</span>
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
