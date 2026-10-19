import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Zap,
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  TrendingDown,
  Star,
  ArrowRight,
  Layers,
  RotateCw,
} from 'lucide-react';
import { TiltedGridHero, type TiltedGridImage } from '@/components/ui/tilted-grid-hero';
import type { CatalogProduct } from '../types/buywise';

interface AmazonProductShowcaseProps {
  products: CatalogProduct[];
  onSelectProduct: (asin: string) => void;
}

export const AmazonProductShowcase: React.FC<AmazonProductShowcaseProps> = ({
  products,
  onSelectProduct,
}) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  const [viewMode, setViewMode] = useState<'one-by-one' | 'continuous'>('one-by-one');
  const timerRef = useRef<number | null>(null);

  const total = products.length;

  // Auto-advance loop along the exterior curve every 3.8s when not hovered
  useEffect(() => {
    if (!isPlaying || isHovered || total <= 1 || viewMode !== 'one-by-one') {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = window.setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % total);
    }, 3800);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, isHovered, total, viewMode]);

  const handlePrev = () => {
    if (total === 0) return;
    setActiveIndex((prev) => (prev - 1 + total) % total);
  };

  const handleNext = () => {
    if (total === 0) return;
    setActiveIndex((prev) => (prev + 1) % total);
  };

  // Convert catalog products into TiltedGridImage items for continuous exterior stream
  const continuousImages: TiltedGridImage[] = products.map((p) => ({
    src: p.image_url,
    alt: p.title,
    asin: p.asin,
    title: `${p.brand} - ${p.title} (${p.currency === 'INR' ? '₹' : '$'}${p.price})`,
    price: p.price,
    verdict: p.ai_verdict,
  }));

  const activeProduct = products[activeIndex] || products[0];

  // Helper for verdict styling and icons
  const getVerdictDetails = (verdict: string) => {
    switch (verdict) {
      case 'BUY':
        return {
          label: 'BUY RECOMMENDATION',
          badgeClass: 'badge-buy',
          icon: <TrendingDown size={14} className="text-emerald-400" />,
          color: '#10b981',
        };
      case 'WAIT':
        return {
          label: 'WAIT FOR PRICE DROP',
          badgeClass: 'badge-wait',
          icon: <AlertTriangle size={14} className="text-amber-400" />,
          color: '#f59e0b',
        };
      case 'DONT_BUY':
        return {
          label: "DON'T BUY (DEFECT DETECTED)",
          badgeClass: 'badge-dont-buy',
          icon: <ShieldAlert size={14} className="text-rose-400" />,
          color: '#f43f5e',
        };
      default:
        return {
          label: 'INSUFFICIENT EVIDENCE',
          badgeClass: 'badge-insufficient',
          icon: <ShieldCheck size={14} className="text-indigo-400" />,
          color: '#6366f1',
        };
    }
  };

  if (!products || products.length === 0) {
    return null;
  }

  return (
    <section className="amazon-showcase-section" id="curved-product-stream">
      {/* Showcase Section Header */}
      <div className="showcase-header">
        <div className="flex flex-wrap items-center justify-between gap-3 w-full">
          <div className="showcase-eyebrow">
            <Zap size={14} className="eyebrow-icon text-sky-400" />
            <span>Exterior 3D Cylinder Loop • One-By-One Product Inspection</span>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-1.5 rounded-full border border-white/10 bg-slate-900/80 p-1 backdrop-blur-md">
            <button
              type="button"
              className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-all ${
                viewMode === 'one-by-one'
                  ? 'bg-sky-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
              onClick={() => setViewMode('one-by-one')}
            >
              <RotateCw size={12} />
              <span>Exterior One-by-One</span>
            </button>
            <button
              type="button"
              className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-all ${
                viewMode === 'continuous'
                  ? 'bg-sky-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
              onClick={() => setViewMode('continuous')}
            >
              <Layers size={12} />
              <span>Exterior Flow Ribbon</span>
            </button>
          </div>
        </div>

        <h2 className="showcase-title">
          Amazon Products in <span className="highlight-text">Exterior 3D Orbit</span>
        </h2>
        <p className="showcase-subtitle">
          Rotating along the exterior curve so each product is presented clearly one by one.
          Inspect the genuine price, defects, and click to audit evidence instantly.
        </p>
      </div>

      {/* VIEW MODE 1: EXTERIOR 3D ONE-BY-ONE CAROUSEL */}
      {viewMode === 'one-by-one' ? (
        <div
          className="exterior-carousel-container"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {/* Navigation Chevron Left */}
          <button
            type="button"
            className="exterior-nav-arrow arrow-left"
            onClick={handlePrev}
            aria-label="Previous Amazon Product"
            title="Previous Product"
          >
            <ChevronLeft size={24} />
          </button>

          {/* 3D Perspective Stage */}
          <div className="exterior-stage-viewport">
            <div className="exterior-cards-track">
              {products.map((product, i) => {
                // Circular offset relative to activeIndex (-N/2 to N/2)
                let offset = (i - activeIndex) % total;
                if (offset > total / 2) offset -= total;
                if (offset < -total / 2) offset += total;

                const isCenter = offset === 0;
                const isImmediateLeft = offset === -1;
                const isImmediateRight = offset === 1;
                const isFarLeft = offset === -2;
                const isFarRight = offset === 2;
                const isVisible = Math.abs(offset) <= 2;

                if (!isVisible) {
                  return null;
                }

                // 3D Exterior Convex Cylinder Math:
                // Center card bows OUTWARD toward viewer (Z = +50px, rotateY = 0deg)
                // Left and Right cards curve BACKWARDS into the depth (Z = -70px / -190px, rotateY = +26deg / -26deg)
                let transformStyle = '';
                let opacity = 0;
                let zIndex = 1;

                if (isCenter) {
                  transformStyle = 'translateX(0%) translateZ(60px) rotateY(0deg) scale(1.05)';
                  opacity = 1;
                  zIndex = 30;
                } else if (isImmediateRight) {
                  transformStyle = 'translateX(92%) translateZ(-70px) rotateY(-26deg) scale(0.88)';
                  opacity = 0.78;
                  zIndex = 20;
                } else if (isImmediateLeft) {
                  transformStyle = 'translateX(-92%) translateZ(-70px) rotateY(26deg) scale(0.88)';
                  opacity = 0.78;
                  zIndex = 20;
                } else if (isFarRight) {
                  transformStyle = 'translateX(175%) translateZ(-190px) rotateY(-46deg) scale(0.72)';
                  opacity = 0.35;
                  zIndex = 10;
                } else if (isFarLeft) {
                  transformStyle = 'translateX(-175%) translateZ(-190px) rotateY(46deg) scale(0.72)';
                  opacity = 0.35;
                  zIndex = 10;
                }

                const verdictInfo = getVerdictDetails(product.ai_verdict);

                return (
                  <div
                    key={product.asin}
                    className={`exterior-product-card ${isCenter ? 'card-center' : 'card-side'}`}
                    style={{
                      transform: transformStyle,
                      opacity,
                      zIndex,
                    }}
                    onClick={() => {
                      if (!isCenter) {
                        setActiveIndex(i);
                      } else {
                        onSelectProduct(product.asin);
                      }
                    }}
                  >
                    {/* Top Badges Row */}
                    <div className="card-top-bar">
                      <div className="flex items-center gap-1.5">
                        <span className="card-brand-tag">{product.brand}</span>
                        {product.prime && <span className="card-prime-badge">Prime</span>}
                      </div>

                      <div className={`card-verdict-pill ${verdictInfo.badgeClass}`}>
                        {verdictInfo.icon}
                        <span>{product.ai_verdict}</span>
                      </div>
                    </div>

                    {/* Product Image Stage */}
                    <div className="card-image-wrapper">
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="card-product-img"
                        loading="lazy"
                      />
                      {product.deal_badge && (
                        <div className="card-deal-floating-badge">
                          <Sparkles size={11} />
                          <span>{product.deal_badge}</span>
                        </div>
                      )}
                    </div>

                    {/* Product Info Body */}
                    <div className="card-info-body">
                      <h3 className="card-product-title" title={product.title}>
                        {product.title}
                      </h3>

                      {/* Pricing Details */}
                      <div className="card-pricing-row">
                        <div className="price-tag-group">
                          <span className="current-price">
                            {product.currency === 'INR' ? '₹' : '$'}
                            {typeof product.price === 'number'
                              ? product.price.toLocaleString()
                              : product.price}
                          </span>
                          {product.list_price && (
                            <span className="list-price">
                              {product.currency === 'INR' ? '₹' : '$'}
                              {typeof product.list_price === 'number'
                                ? product.list_price.toLocaleString()
                                : product.list_price}
                            </span>
                          )}
                        </div>

                        {/* Star Rating */}
                        <div className="card-rating-group">
                          <Star size={13} className="text-amber-400 fill-amber-400" />
                          <span className="rating-value">{product.rating}</span>
                          <span className="review-count">({product.review_count})</span>
                        </div>
                      </div>

                      {/* Verdict Reason / Flaw Notice */}
                      <div className="card-reason-box">
                        <span className="reason-text">{product.ai_verdict_summary}</span>
                      </div>

                      {/* Specs Tags Preview */}
                      {product.specs && product.specs.length > 0 && (
                        <div className="card-specs-row">
                          {product.specs.slice(0, 2).map((spec, sIdx) => (
                            <span key={sIdx} className="spec-chip">
                              {spec}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Audit Action Button */}
                      <div className="card-action-row">
                        <button
                          type="button"
                          className="btn-card-audit"
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectProduct(product.asin);
                          }}
                        >
                          <span>Audit Evidence</span>
                          <ArrowRight size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Navigation Chevron Right */}
          <button
            type="button"
            className="exterior-nav-arrow arrow-right"
            onClick={handleNext}
            aria-label="Next Amazon Product"
            title="Next Product"
          >
            <ChevronRight size={24} />
          </button>

          {/* Interactive Controls Bar at Bottom of Showcase */}
          <div className="exterior-controls-bar">
            {/* Play/Pause Toggle */}
            <button
              type="button"
              className="ctrl-btn-play"
              onClick={() => setIsPlaying(!isPlaying)}
              title={isPlaying ? 'Pause Auto-Orbit' : 'Play Auto-Orbit'}
            >
              {isPlaying ? <Pause size={13} /> : <Play size={13} />}
              <span>{isPlaying ? 'Pause Orbit' : 'Resume'}</span>
            </button>

            {/* Product Indicator Dots / Selector */}
            <div className="exterior-dots-list">
              {products.map((p, dotIdx) => (
                <button
                  key={p.asin}
                  type="button"
                  className={`dot-indicator ${dotIdx === activeIndex ? 'active-dot' : ''}`}
                  onClick={() => setActiveIndex(dotIdx)}
                  title={`View #${dotIdx + 1}: ${p.title}`}
                />
              ))}
            </div>

            {/* Current Product Counter */}
            <div className="exterior-counter-tag">
              <span>Product {activeIndex + 1} of {total}: </span>
              <strong>{activeProduct ? activeProduct.brand : ''}</strong>
            </div>
          </div>
        </div>
      ) : (
        /* VIEW MODE 2: EXTERIOR CONTINUOUS RIBBON (using updated TiltedGridHero) */
        <div className="tilted-grid-wrapper">
          <TiltedGridHero
            images={continuousImages}
            speed={4.2}
            curve={75}
            curveDirection="exterior"
            tileHeight={34}
            aspectRatio={16 / 10}
            onItemClick={(item) => {
              if (item.asin) {
                onSelectProduct(item.asin);
              }
            }}
            className="h-[360px] w-full rounded-2xl border border-white/10 bg-gradient-to-b from-slate-900/60 to-slate-950/80 shadow-2xl backdrop-blur-xl"
          >
            <div className="pointer-events-none relative z-10 flex h-full flex-col items-center justify-between py-6 text-center">
              <div className="flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-950/60 px-4 py-1.5 text-xs font-semibold text-sky-300 shadow-lg backdrop-blur-md">
                <Sparkles size={13} className="text-sky-400" />
                <span>Exterior Curve Active • Click Any Product Tile</span>
              </div>

              <div className="pointer-events-auto rounded-xl border border-white/10 bg-slate-900/80 px-5 py-2 shadow-2xl backdrop-blur-md transition-all hover:border-sky-500/50">
                <span className="text-xs text-slate-400">Exterior Stream: </span>
                <strong className="text-xs font-semibold text-white">
                  {products.length} Amazon Items Rotating Outward
                </strong>
                <span className="mx-2 text-slate-600">•</span>
                <span className="text-xs text-emerald-400 font-medium">Click to Audit</span>
              </div>
            </div>
          </TiltedGridHero>
        </div>
      )}
    </section>
  );
};
