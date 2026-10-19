import React from 'react';
import { ShieldCheck, Lock, ExternalLink, ShoppingBag, MapPin } from 'lucide-react';

interface HeaderProps {
  onOpenPrivacy: () => void;
  onOpenStores?: () => void;
  onNavigateHome?: () => void;
  onScrollToCatalog?: () => void;
  productCount?: number;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenPrivacy,
  onOpenStores,
  onNavigateHome,
  onScrollToCatalog,
  productCount = 16,
}) => {
  return (
    <header className="site-header">
      <div className="header-container">
        {/* Brand Group */}
        <div
          className="brand-group"
          onClick={onNavigateHome}
          role="button"
          tabIndex={0}
          style={{ cursor: 'pointer' }}
          onKeyDown={(e) => e.key === 'Enter' && onNavigateHome && onNavigateHome()}
        >
          <div className="logo-icon-wrapper">
            <ShieldCheck className="logo-icon" size={24} />
          </div>
          <div className="brand-text">
            <div className="brand-title">
              <span>BuyWise</span>
              <span className="brand-ai">AI</span>
              <span className="hackathon-tag">Hackathon '26</span>
            </div>
            <span className="brand-subtitle">Amazon Shopping & Pre-Purchase Forensic Intelligence</span>
          </div>
        </div>

        {/* Header Navigation & Badges */}
        <nav className="header-nav">
          {onScrollToCatalog && (
            <button
              type="button"
              className="nav-link-btn nav-catalog-btn"
              onClick={onScrollToCatalog}
            >
              <ShoppingBag size={14} />
              <span>Amazon Catalog ({productCount})</span>
            </button>
          )}

          {onOpenStores && (
            <button
              type="button"
              className="nav-link-btn"
              onClick={onOpenStores}
              title="Find local authorized brand stores & service centers"
            >
              <MapPin size={14} className="text-sky-400" />
              <span>Authorized Stores</span>
            </button>
          )}

          <div className="security-badge" title="Cryptographically verified evidence">
            <Lock size={14} className="security-icon" />
            <span>Deterministic Math • Evidence Grounded</span>
          </div>

          <button
            id="privacy-policy-btn"
            className="nav-link-btn"
            onClick={onOpenPrivacy}
            type="button"
          >
            Privacy & Trust Policy
          </button>

          <a
            href="https://github.com/leelakrishnasaisriprasadu08-afk/amazon-buywise-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-link-btn nav-github"
          >
            <span>GitHub</span>
            <ExternalLink size={14} />
          </a>
        </nav>
      </div>
    </header>
  );
};
