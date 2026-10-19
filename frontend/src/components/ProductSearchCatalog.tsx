import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  SlidersHorizontal,
  Sparkles,
  ShoppingBag,
} from 'lucide-react';
import type { CatalogProduct } from '../types/buywise';
import { ProductCard } from './ProductCard';

interface ProductSearchCatalogProps {
  products: CatalogProduct[];
  searchQuery: string;
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
  onAuditProduct: (asin: string) => void;
  onQuickSearch: (query: string) => void;
  isAuditing?: boolean;
  isLoading?: boolean;
}

const CATEGORY_TABS = [
  { id: 'all', label: '🔥 All Deals' },
  { id: 'laptops', label: '💻 Laptops & MacBooks' },
  { id: 'smartphones', label: '📱 Smartphones' },
  { id: 'audio', label: '🎧 Audio & Headphones' },
  { id: 'gaming', label: '🖱️ Gaming & PC' },
  { id: 'tech accessories', label: '⚡ Accessories' },
];

const POPULAR_SEARCH_CHIPS = [
  'MacBook Air',
  'Gaming Mouse',
  'Sony Headphones',
  'iPhone 15 Pro',
  'Samsung S24',
  'College Laptop',
  'Anker Power Bank',
];

export const ProductSearchCatalog: React.FC<ProductSearchCatalogProps> = ({
  products,
  searchQuery,
  selectedCategory,
  onSelectCategory,
  onAuditProduct,
  onQuickSearch,
  isAuditing = false,
  isLoading = false,
}) => {
  const [selectedVerdict, setSelectedVerdict] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('ai_recommended');

  // Filter and Sort products
  const displayProducts = useMemo(() => {
    let result = [...products];

    // Filter by AI Verdict
    if (selectedVerdict !== 'all') {
      result = result.filter((p) => p.ai_verdict === selectedVerdict);
    }

    // Sort products
    result.sort((a, b) => {
      const priceA = typeof a.price === 'number' ? a.price : parseFloat(a.price);
      const priceB = typeof b.price === 'number' ? b.price : parseFloat(b.price);
      const ratingA = typeof a.rating === 'number' ? a.rating : parseFloat(a.rating);
      const ratingB = typeof b.rating === 'number' ? b.rating : parseFloat(b.rating);

      const discountA = Number(a.list_price) > priceA ? (Number(a.list_price) - priceA) / Number(a.list_price) : 0;
      const discountB = Number(b.list_price) > priceB ? (Number(b.list_price) - priceB) / Number(b.list_price) : 0;

      switch (sortBy) {
        case 'price_asc':
          return priceA - priceB;
        case 'price_desc':
          return priceB - priceA;
        case 'rating_desc':
          return ratingB - ratingA;
        case 'discount_desc':
          return discountB - discountA;
        case 'ai_recommended':
        default: {
          // BUY verdicts first, then WAIT, then DONT_BUY
          const verdictWeight: Record<string, number> = {
            BUY: 4,
            WAIT: 3,
            DONT_BUY: 2,
            INSUFFICIENT_EVIDENCE: 1,
          };
          const weightDiff = (verdictWeight[b.ai_verdict] || 0) - (verdictWeight[a.ai_verdict] || 0);
          if (weightDiff !== 0) return weightDiff;
          return b.review_count - a.review_count;
        }
      }
    });

    return result;
  }, [products, selectedVerdict, sortBy]);

  return (
    <section className="catalog-section" id="amazon-product-catalog">
      {/* Category Tabs Bar */}
      <div className="catalog-tabs-container">
        <div className="category-tabs-scroll">
          {CATEGORY_TABS.map((tab) => {
            const isActive =
              (tab.id === 'all' && (!selectedCategory || selectedCategory.toLowerCase() === 'all')) ||
              selectedCategory.toLowerCase().includes(tab.id);

            return (
              <button
                key={tab.id}
                type="button"
                className={`category-tab-btn ${isActive ? 'active' : ''}`}
                onClick={() => onSelectCategory(tab.id === 'all' ? 'all' : tab.id)}
              >
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Catalog Control Bar: Results count, Verdict Filter, Sort */}
      <div className="catalog-controls-bar">
        <div className="catalog-results-counter">
          <ShoppingBag size={18} className="counter-icon" />
          <span className="results-count-text">
            <strong>{displayProducts.length}</strong> Amazon Products Found
          </span>
          {searchQuery && (
            <span className="active-query-tag">
              for "<em>{searchQuery}</em>"
            </span>
          )}
          {isLoading && (
            <span className="catalog-loading-pill" style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', opacity: 0.8 }}>
              • updating...
            </span>
          )}
        </div>

        <div className="catalog-filter-controls">
          {/* AI Verdict Filter */}
          <div className="filter-select-wrapper">
            <Filter size={14} className="control-icon" />
            <select
              aria-label="Filter by BuyWise AI verdict"
              className="control-select"
              value={selectedVerdict}
              onChange={(e) => setSelectedVerdict(e.target.value)}
            >
              <option value="all">All AI Verdicts</option>
              <option value="BUY">🟢 BUY (Verified Deals)</option>
              <option value="WAIT">🟡 WAIT (Price Markups)</option>
              <option value="DONT_BUY">🔴 DON'T BUY (Hardware Defects)</option>
              <option value="INSUFFICIENT_EVIDENCE">⚡ INSUFFICIENT DATA</option>
            </select>
          </div>

          {/* Sort By Select */}
          <div className="filter-select-wrapper">
            <SlidersHorizontal size={14} className="control-icon" />
            <select
              aria-label="Sort products"
              className="control-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="ai_recommended">AI Recommended First</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating_desc">Highest Customer Rating</option>
              <option value="discount_desc">Biggest Savings %</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      {displayProducts.length > 0 ? (
        <div className="products-grid">
          {displayProducts.map((product) => (
            <ProductCard
              key={product.asin}
              product={product}
              onAudit={onAuditProduct}
              isAuditing={isAuditing}
            />
          ))}
        </div>
      ) : (
        <div className="catalog-empty-state">
          <div className="empty-icon-box">
            <Search size={32} />
          </div>
          <h3 className="empty-title">No Amazon products found</h3>
          <p className="empty-desc">
            We couldn't find matching products for "<strong>{searchQuery}</strong>". Try searching another keyword or pick from popular queries below.
          </p>

          <div className="empty-suggestions-group">
            <span className="suggestions-label">Try searching:</span>
            <div className="suggestions-chips">
              {POPULAR_SEARCH_CHIPS.map((chip) => (
                <button
                  key={chip}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => onQuickSearch(chip)}
                >
                  <Sparkles size={12} />
                  <span>{chip}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
