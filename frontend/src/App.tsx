import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Zap,
  TrendingDown,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  DollarSign,
  Scale,
  FileText,
  Plus,
  Minus,
  ShieldCheck,
  Binary,
  X,
} from 'lucide-react';
import { Header } from './components/Header';
import { PrivacyModal } from './components/PrivacyModal';
import { LocalStoresModal } from './components/LocalStoresModal';
import { VerdictBanner } from './components/VerdictBanner';
import { PriceIntelligenceCard } from './components/PriceIntelligenceCard';
import { AspectScorecards } from './components/AspectScorecards';
import { CompetitorCard } from './components/CompetitorCard';
import { AuditLedger } from './components/AuditLedger';
import { ReasoningTimeline } from './components/ReasoningTimeline';
import { ProductSearchCatalog } from './components/ProductSearchCatalog';
import { AlexaVoiceAgent } from './components/AlexaVoiceAgent';
import { AmazonProductShowcase } from './components/AmazonProductShowcase';
import { analyzeProductStream, searchCatalog } from './services/api';
import type { CatalogProduct, RecommendationReport, StreamingMilestone } from './types/buywise';

const HACKATHON_DEMO_CHIPS = [
  {
    asin: 'B0COLLEGE1',
    label: 'College Student Laptop (₹52K)',
    subtitle: 'Soldered RAM vs Better Alt',
    badge: 'Switch & Save ₹2,010',
    icon: <Sparkles size={14} />,
  },
  {
    asin: 'B08N5WRWNW',
    label: 'MacBook Air M1 ($749)',
    subtitle: 'Genuine Deal at All-Time Low',
    badge: 'BUY Recommendation',
    icon: <TrendingDown size={14} />,
  },
  {
    asin: 'B09V3K3EXP',
    label: 'Flagship Smartphone ($899)',
    subtitle: 'Pre-Sale MSRP Markup',
    badge: 'WAIT Recommendation',
    icon: <AlertTriangle size={14} />,
  },
  {
    asin: 'B07DEFECT0',
    label: 'Ergonomic Gaming Mouse',
    subtitle: 'High 4.4★ but Hardware Defect',
    badge: "DON'T BUY",
    icon: <ShieldAlert size={14} />,
  },
  {
    asin: 'B0NEWITEM0',
    label: 'Compact 7-Port Hub',
    subtitle: 'Brand New Listing, 1 Review',
    badge: 'Insufficient Evidence',
    icon: <Zap size={14} />,
  },
];

export const App: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [alternativeAsin, setAlternativeAsin] = useState('');
  const [showAltInput, setShowAltInput] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);
  const [isStoresOpen, setIsStoresOpen] = useState(false);

  // Catalog products state
  const [catalogProducts, setCatalogProducts] = useState<CatalogProduct[]>([]);
  const [isLoadingCatalog, setIsLoadingCatalog] = useState(true);

  // Analysis / Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [milestones, setMilestones] = useState<StreamingMilestone[]>([]);
  const [report, setReport] = useState<RecommendationReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeAuditedTarget, setActiveAuditedTarget] = useState<string>('');

  const catalogRef = useRef<HTMLDivElement>(null);
  const auditSectionRef = useRef<HTMLDivElement>(null);

  // Fetch catalog products whenever activeQuery or selectedCategory changes
  useEffect(() => {
    let isCurrent = true;
    setIsLoadingCatalog(true);

    searchCatalog(activeQuery, selectedCategory)
      .then((items) => {
        if (isCurrent) {
          setCatalogProducts(items);
          setIsLoadingCatalog(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load products:', err);
        if (isCurrent) setIsLoadingCatalog(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [activeQuery, selectedCategory]);

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = inputText.trim();
    setActiveQuery(query);

    // Scroll to catalog grid smoothly
    setTimeout(() => {
      catalogRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  const handleStartAudit = (asinOrQueryToAudit?: string, altToAudit?: string) => {
    const target = (asinOrQueryToAudit || inputText || activeQuery).trim();
    if (!target) return;

    setActiveAuditedTarget(target);
    setErrorMessage(null);
    setMilestones([]);
    setReport(null);
    setIsStreaming(true);

    if (asinOrQueryToAudit) {
      setInputText(asinOrQueryToAudit);
    }
    if (altToAudit !== undefined) {
      setAlternativeAsin(altToAudit);
    }

    const effectiveAlt = altToAudit !== undefined ? altToAudit : alternativeAsin;

    // Scroll to active audit section
    setTimeout(() => {
      auditSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);

    analyzeProductStream(
      target,
      (milestone) => {
        setMilestones((prev) => [...prev, milestone]);
      },
      (finalReport) => {
        setReport(finalReport);
        setIsStreaming(false);
      },
      (err) => {
        setErrorMessage(err);
        setIsStreaming(false);
      },
      effectiveAlt
    );
  };

  const handleResetAudit = () => {
    setReport(null);
    setMilestones([]);
    setErrorMessage(null);
    setIsStreaming(false);
    setActiveAuditedTarget('');
  };

  const handleQuickSearch = (query: string) => {
    setInputText(query);
    setActiveQuery(query);
    setTimeout(() => {
      catalogRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  const handleScrollToCatalog = () => {
    catalogRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="app-shell">
      <Header
        onOpenPrivacy={() => setIsPrivacyOpen(true)}
        onOpenStores={() => setIsStoresOpen(true)}
        onNavigateHome={() => {
          handleResetAudit();
          setInputText('');
          setActiveQuery('');
          setSelectedCategory('all');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        onScrollToCatalog={handleScrollToCatalog}
        productCount={catalogProducts.length}
      />

      <main className="main-content">
        {/* Active Analysis or Live Audit Section */}
        <div ref={auditSectionRef}>
          {(isStreaming || report || errorMessage) && (
            <section className="analysis-section" style={{ marginBottom: '2.5rem' }}>
              <div className="analysis-toolbar">
                <button
                  className="btn-back-link"
                  onClick={handleResetAudit}
                  type="button"
                  id="close-audit-btn"
                >
                  <RotateCcw size={15} />
                  <span>Close Audit & Return to Catalog</span>
                </button>

                <div className="target-pill">
                  <span>Auditing:</span>
                  <strong>{report?.product.title || report?.product.asin || activeAuditedTarget}</strong>
                </div>
              </div>

              {/* Error Banner */}
              {errorMessage && (
                <div className="alert-banner alert-danger">
                  <ShieldAlert size={20} className="alert-icon" />
                  <div className="alert-text">
                    <strong>Analysis Error:</strong>
                    <span>{errorMessage}</span>
                  </div>
                </div>
              )}

              {/* Reasoning Timeline (Milestones streaming in) */}
              <ReasoningTimeline milestones={milestones} isStreaming={isStreaming} />

              {/* Completed Decision Report */}
              {report && (
                <div className="results-container">
                  <VerdictBanner report={report} />

                  <div className="dashboard-grid">
                    <PriceIntelligenceCard
                      metrics={report.price_metrics}
                      productTitle={report.product.title || activeAuditedTarget}
                    />
                    <AspectScorecards analysis={report.aspect_analysis} />
                  </div>

                  {report.alternative && (
                    <CompetitorCard
                      alternative={report.alternative}
                      onAuditAlternative={(altAsin) => handleStartAudit(altAsin)}
                    />
                  )}

                  <AuditLedger report={report} />
                </div>
              )}
            </section>
          )}
        </div>

        {/* Hero Landing Section */}
        <section className="hero-section">
          <div className="hero-content">
            <span className="hero-eyebrow">
              <Sparkles size={14} className="eyebrow-icon" />
              <span>Amazon Hackathon 2026 • Real-Time Evidence Audit & Return Reduction Engine</span>
            </span>

            <h1 className="hero-title">
              Real-time Amazon search with <span className="highlight-text">AI forensic intelligence</span>.
            </h1>

            <p className="hero-description">
              Enter any Amazon product name or ASIN. BuyWise AI instantly displays matching Amazon products,
              uncovers fake pre-sale discounts using deterministic price math, and clusters verified review defects before you buy.
            </p>

            {/* Alexa+ Voice Intelligence Centerpiece (Amazon Hackathon Priority) */}
            <AlexaVoiceAgent
              onExecuteSearch={handleQuickSearch}
              onExecuteAudit={(target) => handleStartAudit(target)}
              currentAuditedTitle={report?.product.title || activeAuditedTarget}
              currentVerdict={report?.verdict}
            />

            {/* Smart Search Form */}
            <form onSubmit={handleSearchSubmit} className="search-box-card">
              <div className="search-inputs-group">
                <div className="input-field-wrapper">
                  <Search className="search-input-icon" size={20} />
                  <input
                    id="product-input-field"
                    type="text"
                    className="search-input"
                    placeholder="Enter product name (e.g. 'MacBook Air', 'Gaming Mouse', 'Sony XM5') or ASIN..."
                    value={inputText}
                    onChange={(e) => {
                      setInputText(e.target.value);
                      // Live filter catalog as user types if they type 2+ characters
                      if (e.target.value.length >= 2 || e.target.value.length === 0) {
                        setActiveQuery(e.target.value);
                      }
                    }}
                  />
                  {inputText && (
                    <button
                      type="button"
                      aria-label="Clear search input"
                      className="btn-clear-input"
                      onClick={() => {
                        setInputText('');
                        setActiveQuery('');
                      }}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '0.2rem',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>

              {/* Action Buttons: Search Catalog OR Immediate AI Audit */}
              <div className="search-actions-group">
                <button
                  id="search-amazon-btn"
                  className="btn-search-amazon"
                  type="submit"
                >
                  <Search size={16} />
                  <span>Search Products</span>
                </button>

                <button
                  id="submit-audit-btn"
                  className="btn-audit"
                  onClick={() => handleStartAudit()}
                  disabled={!inputText.trim() || isStreaming}
                  type="button"
                >
                  <span>Audit with AI</span>
                  <ArrowRight size={18} />
                </button>
              </div>
            </form>

            {/* Optional Competitor Comparison Field Toggle */}
            <div className="secondary-input-row">
              <button
                type="button"
                className="toggle-secondary-btn"
                onClick={() => setShowAltInput(!showAltInput)}
              >
                {showAltInput ? <Minus size={14} /> : <Plus size={14} />}
                <span>{showAltInput ? 'Hide Competitor ASIN input' : 'Compare directly against specific Competitor ASIN (Optional)'}</span>
              </button>
              {showAltInput && (
                <input
                  type="text"
                  className="secondary-input-field"
                  placeholder="Enter competitor ASIN (e.g. B0COMPET01)..."
                  value={alternativeAsin}
                  onChange={(e) => setAlternativeAsin(e.target.value)}
                />
              )}
            </div>

            {/* Hackathon Quick-Audit Benchmarks */}
            <div className="demo-chips-section">
              <span className="chips-label">Hackathon Live Benchmark Scenarios (Click to test):</span>
              <div className="chips-grid">
                {HACKATHON_DEMO_CHIPS.map((chip) => (
                  <button
                    key={chip.asin}
                    className="demo-chip-card"
                    onClick={() => handleStartAudit(chip.asin)}
                    type="button"
                  >
                    <div className="chip-top">
                      <span className="chip-icon">{chip.icon}</span>
                      <span className="chip-title">{chip.label}</span>
                    </div>
                    <span className="chip-subtitle">{chip.subtitle}</span>
                    <span className="chip-badge">{chip.badge}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Option A: Interactive 3D Cylindrical Amazon Product Stream */}
        <AmazonProductShowcase
          products={catalogProducts}
          onSelectProduct={(asin) => handleStartAudit(asin)}
        />

        {/* Real-Time Amazon Product Catalog Section */}
        <div ref={catalogRef}>
          <ProductSearchCatalog
            products={catalogProducts}
            searchQuery={activeQuery}
            selectedCategory={selectedCategory}
            onSelectCategory={(cat) => setSelectedCategory(cat)}
            onAuditProduct={(asin) => handleStartAudit(asin)}
            onQuickSearch={handleQuickSearch}
            isAuditing={isStreaming}
            isLoading={isLoadingCatalog}
          />
        </div>

        {/* Architecture & Trust Framework Showcase */}
        <section className="landing-showcase">
          <div className="landing-pillars-section">
            <span className="section-eyebrow">
              <Binary size={14} />
              <span>Evidence-Grounded Intelligence Core</span>
            </span>
            <h2 className="section-title">Why Traditional Reviews & Star Ratings Fail</h2>
            <p className="section-subtitle">
              Star ratings blend outdated reviews and hide recurring hardware failures. Retailers inflate MSRP to fabricate false 50% discounts. BuyWise AI deploys four deterministic forensic checks before you spend.
            </p>

            <div className="pillars-grid">
              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <DollarSign size={20} />
                </div>
                <h3 className="pillar-title">1. Deterministic Price Math</h3>
                <p className="pillar-description">
                  Pure Python <code>Decimal</code> arithmetic calculates true effective discounts against rolling 30/90-day medians and historical price percentiles, flagging pre-sale price markups.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <FileText size={20} />
                </div>
                <h3 className="pillar-title">2. Review Aspect Forensics</h3>
                <p className="pillar-description">
                  Hybrid BM25 + Semantic scoring extracts sentiment across 7 hardware aspects (battery, display, durability, etc.), quoting verbatim review evidence and clustering recurring defects.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <Scale size={20} />
                </div>
                <h3 className="pillar-title">3. Objective Alternative Engine</h3>
                <p className="pillar-description">
                  Discovers objectively superior catalog alternatives offering verified cost savings or fixing verified hardware flaws, with zero sponsored affiliate placement bias.
                </p>
              </div>

              <div className="pillar-card">
                <div className="pillar-icon-box">
                  <ShieldCheck size={20} />
                </div>
                <h3 className="pillar-title">4. Cryptographic Provenance</h3>
                <p className="pillar-description">
                  Every material claim is bound to a timestamped provenance envelope with SHA-256 payload digests. If evidence is insufficient, it explicitly halts at <strong>INSUFFICIENT EVIDENCE</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* Security Invariant Guarantee Box */}
          <div className="security-guarantee-card">
            <div className="guarantee-header">
              <div className="guarantee-title-group">
                <ShieldCheck size={22} className="guarantee-check-icon" />
                <h3 className="guarantee-title">Zero-Compromise Security & Impartiality Architecture</h3>
              </div>
              <button
                type="button"
                className="guarantee-btn-link"
                onClick={() => setIsPrivacyOpen(true)}
              >
                Read Full Security & Privacy Policy →
              </button>
            </div>

            <div className="guarantee-grid">
              <div className="guarantee-item">
                <CheckCircle2 size={16} className="guarantee-check-icon" />
                <div>
                  <strong>No User Credentials:</strong> Never requests Amazon passwords, session tokens, or payment card details.
                </div>
              </div>
              <div className="guarantee-item">
                <CheckCircle2 size={16} className="guarantee-check-icon" />
                <div>
                  <strong>No LLM Arithmetic:</strong> Zero hallucinated discount math; all financial metrics are computed deterministically.
                </div>
              </div>
              <div className="guarantee-item">
                <CheckCircle2 size={16} className="guarantee-check-icon" />
                <div>
                  <strong>No Fabricated Fraud Claims:</strong> Accusations of "fake reviews" are strictly barred without verified defect clustering.
                </div>
              </div>
              <div className="guarantee-item">
                <CheckCircle2 size={16} className="guarantee-check-icon" />
                <div>
                  <strong>Zero Affiliate Bias:</strong> Recommendations are strictly algorithmic and mathematically defendable for consumers.
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="footer-container">
          <div className="footer-left">
            <span>BuyWise AI • Built for the Amazon Hackathon</span>
            <span className="footer-sep">•</span>
            <span>Deterministic Math • Evidence Grounded • Zero Fabricated Claims</span>
          </div>

          <div className="footer-right">
            <button
              className="footer-link-btn"
              onClick={() => setIsPrivacyOpen(true)}
              type="button"
            >
              Privacy & Security Policy
            </button>
          </div>
        </div>
      </footer>

      <PrivacyModal isOpen={isPrivacyOpen} onClose={() => setIsPrivacyOpen(false)} />
      <LocalStoresModal
        isOpen={isStoresOpen}
        onClose={() => setIsStoresOpen(false)}
        initialBrand={report?.product.brand || undefined}
      />
    </div>
  );
};

export default App;
