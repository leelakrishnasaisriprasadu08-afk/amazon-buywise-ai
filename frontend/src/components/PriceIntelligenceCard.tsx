import React, { useState } from 'react';
import {
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  DollarSign,
  Globe,
  Loader2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import type { PriceMetrics } from '../types/buywise';
import { fetchWebPricingCrossCheck, type WebProductResult } from '../services/api';

interface PriceIntelligenceCardProps {
  metrics: PriceMetrics | null;
  productTitle?: string;
}

export const PriceIntelligenceCard: React.FC<PriceIntelligenceCardProps> = ({
  metrics,
  productTitle,
}) => {
  const [crossCheckResults, setCrossCheckResults] = useState<WebProductResult[]>([]);
  const [isLoadingCrossCheck, setIsLoadingCrossCheck] = useState(false);
  const [showCrossCheck, setShowCrossCheck] = useState(false);
  const [hasFetched, setHasFetched] = useState(false);

  const handleToggleCrossCheck = async () => {
    const nextState = !showCrossCheck;
    setShowCrossCheck(nextState);

    if (nextState && !hasFetched) {
      const q = productTitle || metrics?.asin || 'laptop';
      setIsLoadingCrossCheck(true);
      try {
        const results = await fetchWebPricingCrossCheck(q);
        setCrossCheckResults(results);
        setHasFetched(true);
      } catch (err) {
        console.error('Failed to cross check pricing:', err);
      } finally {
        setIsLoadingCrossCheck(false);
      }
    }
  };
  if (!metrics) {
    return (
      <div className="card price-card empty-card">
        <div className="card-header">
          <DollarSign size={20} className="card-icon" />
          <h3>Price Intelligence</h3>
        </div>
        <p className="empty-notice">
          No historical price tracking depth available for this listing.
        </p>
      </div>
    );
  }

  const percentileNum = parseFloat(metrics.percentile_rank);

  return (
    <div className="card price-card">
      <div className="card-header">
        <div className="card-title-group">
          <DollarSign size={20} className="card-icon" />
          <h3>Price Intelligence & Deal Verification</h3>
        </div>
        {metrics.is_all_time_low && (
          <span className="badge-pill pill-success">
            <Sparkles size={13} />
            <span>All-Time Low Price</span>
          </span>
        )}
      </div>

      {metrics.is_artificial_discount && (
        <div className="alert-banner alert-warning">
          <AlertTriangle size={18} className="alert-icon" />
          <div className="alert-text">
            <strong>Artificial Discount Detected:</strong>
            <span>
              The reference MSRP was inflated immediately prior to this promotion. The current price is
              not a genuine reduction compared to the 90-day median.
            </span>
          </div>
        </div>
      )}

      <div className="price-overview-grid">
        <div className="price-stat-box">
          <span className="stat-label">Current Observed Price</span>
          <div className="stat-value-row">
            <span className="stat-value stat-primary">
              {metrics.currency} {metrics.current_price}
            </span>
          </div>
        </div>

        <div className="price-stat-box">
          <span className="stat-label">90-Day Rolling Median</span>
          <span className="stat-value">
            {metrics.currency} {metrics.rolling_90d_median || metrics.median_price}
          </span>
        </div>

        <div className="price-stat-box">
          <span className="stat-label">Historical 90-Day Range</span>
          <span className="stat-value stat-range">
            {metrics.currency} {metrics.min_price} – {metrics.currency} {metrics.max_price}
          </span>
        </div>

        <div className="price-stat-box">
          <span className="stat-label">Historical Percentile</span>
          <div className="stat-value-row">
            <span className={`stat-value ${percentileNum <= 30 ? 'stat-good' : percentileNum >= 70 ? 'stat-bad' : ''}`}>
              {percentileNum.toFixed(1)}%
            </span>
            {percentileNum <= 30 ? (
              <TrendingDown size={16} className="trend-good" />
            ) : percentileNum >= 70 ? (
              <TrendingUp size={16} className="trend-bad" />
            ) : null}
          </div>
        </div>
      </div>

      <div className="percentile-track-container">
        <div className="track-labels">
          <span>All-Time Low (0%)</span>
          <span>Historical Median (50%)</span>
          <span>Cyclical Peak (100%)</span>
        </div>
        <div className="percentile-track">
          <div
            className="percentile-marker"
            style={{ left: `${Math.min(Math.max(percentileNum, 2), 98)}%` }}
            title={`Current price is at ${percentileNum}% of its historical curve`}
          >
            <span className="marker-pin" />
          </div>
        </div>
        <span className="percentile-caption">
          {percentileNum <= 30
            ? '✓ Price is currently situated near the lowest historical bounds.'
            : percentileNum >= 70
            ? '⚠ Price is currently near its highest historical peak.'
            : '• Price is floating near its standard historical median.'}
        </span>
      </div>

      {/* Real-time Multi-Retailer & Manufacturer MSRP Cross-Check (OpenWebNinja search-light-v2) */}
      <div className="mt-4 pt-3 border-t border-white/10">
        <button
          type="button"
          onClick={handleToggleCrossCheck}
          className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-white/5 hover:border-sky-500/30 transition-all text-xs font-semibold text-slate-300 hover:text-white"
        >
          <div className="flex items-center gap-2">
            <Globe size={14} className="text-sky-400" />
            <span>Cross-Check Web & Manufacturer MSRP</span>
            <span className="text-[10px] text-sky-400 font-mono bg-sky-950/60 px-1.5 py-0.5 rounded border border-sky-400/20">
              OpenWebNinja Light v2
            </span>
          </div>
          {showCrossCheck ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {showCrossCheck && (
          <div className="mt-3 space-y-2 text-left">
            {isLoadingCrossCheck ? (
              <div className="py-4 flex items-center justify-center gap-2 text-xs text-slate-400">
                <Loader2 size={16} className="animate-spin text-sky-400" />
                <span>Scanning Google Shopping & manufacturer databases...</span>
              </div>
            ) : crossCheckResults.length > 0 ? (
              <div className="space-y-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Web-Wide Verified Listings ({crossCheckResults.length}):
                </span>
                {crossCheckResults.slice(0, 4).map((item, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5 flex items-center justify-between gap-3 text-xs"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      {item.image_url && (
                        <img
                          src={item.image_url}
                          alt=""
                          className="w-8 h-8 rounded object-contain bg-slate-800 shrink-0"
                        />
                      )}
                      <div className="min-w-0">
                        <p className="font-semibold text-white truncate text-xs" title={item.product_title}>
                          {item.product_title}
                        </p>
                        <span className="text-[10px] text-slate-400">{item.source}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <strong className="text-sky-300 font-bold block">{item.price}</strong>
                        {item.original_price && (
                          <span className="text-[10px] text-slate-500 line-through">
                            MSRP {item.original_price}
                          </span>
                        )}
                      </div>
                      {item.product_page_url && item.product_page_url !== '#' && (
                        <a
                          href={item.product_page_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1 rounded text-slate-400 hover:text-sky-300"
                          title="View external store listing"
                        >
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-3 text-center text-xs text-slate-400">
                No external web listings found for this specific query.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
