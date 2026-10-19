import React from 'react';
import {
  Sparkles,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';
import type { CatalogProduct } from '../types/buywise';

interface ProductCardProps {
  product: CatalogProduct;
  onAudit: (asin: string) => void;
  isAuditing?: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAudit,
  isAuditing = false,
}) => {
  const priceNum = typeof product.price === 'number' ? product.price : parseFloat(product.price);
  const listNum = typeof product.list_price === 'number' ? product.list_price : parseFloat(product.list_price);
  const hasDiscount = listNum > priceNum;
  const discountPct = hasDiscount ? Math.round(((listNum - priceNum) / listNum) * 100) : 0;

  // Format currency
  const formatPrice = (amount: number) => {
    if (product.currency === 'INR') {
      return `₹${amount.toLocaleString('en-IN')}`;
    }
    return `$${amount.toFixed(2)}`;
  };

  // Verdict style mapper
  const getVerdictBadge = () => {
    switch (product.ai_verdict) {
      case 'BUY':
        return {
          icon: <CheckCircle2 size={13} />,
          label: 'BUY VERDICT',
          className: 'verdict-pill-buy',
          bgHint: 'pill-emerald',
        };
      case 'WAIT':
        return {
          icon: <AlertTriangle size={13} />,
          label: 'WAIT VERDICT',
          className: 'verdict-pill-wait',
          bgHint: 'pill-amber',
        };
      case 'DONT_BUY':
        return {
          icon: <ShieldAlert size={13} />,
          label: "DON'T BUY",
          className: 'verdict-pill-dont-buy',
          bgHint: 'pill-rose',
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          icon: <HelpCircle size={13} />,
          label: 'INSUFFICIENT DATA',
          className: 'verdict-pill-insufficient',
          bgHint: 'pill-slate',
        };
    }
  };

  const badge = getVerdictBadge();

  return (
    <article className="product-card" id={`product-card-${product.asin}`}>
      {/* Top Banner / Deal Pill */}
      <div className="product-card-topbar">
        {product.deal_badge ? (
          <span className="deal-badge-tag">{product.deal_badge}</span>
        ) : (
          <span className="brand-tag">{product.brand}</span>
        )}

        {product.prime && (
          <div className="prime-tag" title="Amazon Prime One-Day / Two-Day Delivery">
            <span className="prime-text">prime</span>
            <span className="prime-check">✓</span>
          </div>
        )}
      </div>

      {/* Product Image & Thumbnail */}
      <div className="product-image-container">
        <img
          src={product.image_url}
          alt={product.title}
          className="product-thumbnail"
          loading="lazy"
          onError={(e) => {
            // High-fidelity fallback placeholder if external image is blocked
            (e.target as HTMLImageElement).src =
              'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80';
          }}
        />

        <div className={`verdict-overlay-badge ${badge.className}`}>
          {badge.icon}
          <span>{badge.label}</span>
        </div>
      </div>

      {/* Product Details */}
      <div className="product-info-block">
        <div className="product-category-row">
          <span className="product-category-pill">{product.category}</span>
          <span className="product-asin-text">ASIN: {product.asin}</span>
        </div>

        <h3 className="product-title" title={product.title}>
          {product.title}
        </h3>

        {/* Rating and review count */}
        <div className="product-rating-row">
          <div className="star-rating">
            <span className="star-icons">{'★'.repeat(Math.floor(Number(product.rating)))}</span>
            <span className="rating-num">{Number(product.rating).toFixed(1)}</span>
          </div>
          <span className="rating-dot">•</span>
          <span className="review-count">
            {product.review_count.toLocaleString()} ratings
          </span>
        </div>

        {/* Price Row */}
        <div className="product-pricing-row">
          <div className="price-main">
            <span className="price-currency-sym">
              {product.currency === 'INR' ? '₹' : '$'}
            </span>
            <span className="price-amount">
              {product.currency === 'INR'
                ? priceNum.toLocaleString('en-IN')
                : priceNum.toFixed(2)}
            </span>
          </div>

          {hasDiscount && (
            <div className="price-original-wrap">
              <span className="price-list-strikethrough">
                {formatPrice(listNum)}
              </span>
              <span className="price-discount-tag">-{discountPct}%</span>
            </div>
          )}
        </div>

        {/* Specs List */}
        {product.specs && product.specs.length > 0 && (
          <div className="product-specs-list">
            {product.specs.slice(0, 3).map((spec, idx) => (
              <span key={idx} className="spec-chip">
                {spec}
              </span>
            ))}
          </div>
        )}

        {/* AI Forensic Summary Callout */}
        <div className={`ai-card-insight ${badge.bgHint}`}>
          <div className="ai-insight-header">
            <Sparkles size={13} className="ai-insight-icon" />
            <span className="ai-insight-title">BuyWise AI Pre-Purchase Forensics</span>
          </div>
          <p className="ai-insight-text">{product.ai_verdict_summary}</p>
        </div>
      </div>

      {/* Card Action Buttons */}
      <div className="product-card-actions">
        <button
          type="button"
          className="btn-audit-product"
          onClick={() => onAudit(product.asin)}
          disabled={isAuditing}
          id={`audit-btn-${product.asin}`}
        >
          <Sparkles size={15} />
          <span>{isAuditing ? 'Running AI Audit...' : 'Audit Evidence with AI'}</span>
        </button>

        <a
          href={`https://${product.marketplace || 'amazon.com'}/dp/${product.asin}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-view-amazon"
          title="Inspect Canonical Listing on Amazon"
        >
          <ExternalLink size={14} />
          <span>Amazon</span>
        </a>
      </div>
    </article>
  );
};
