import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Phone,
  Globe,
  Star,
  Search,
  X,
  ShieldCheck,
  Building2,
  ExternalLink,
  Loader2,
} from 'lucide-react';
import { fetchLocalStores, type LocalStoreResult } from '../services/api';

interface LocalStoresModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialBrand?: string;
}

const POPULAR_QUERIES = [
  'Apple Store San Francisco',
  'Sony Service Center New York',
  'Samsung Experience Store Chicago',
  'Hotels in San Francisco, USA',
  'Dell Authorized Service Center',
];

export const LocalStoresModal: React.FC<LocalStoresModalProps> = ({
  isOpen,
  onClose,
  initialBrand,
}) => {
  const [searchQuery, setSearchQuery] = useState(
    initialBrand ? `${initialBrand} Store San Francisco` : 'Apple Store San Francisco'
  );
  const [stores, setStores] = useState<LocalStoreResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    if (isOpen) {
      const q = initialBrand
        ? `${initialBrand} Store San Francisco`
        : 'Apple Store San Francisco';
      setSearchQuery(q);
      executeSearch(q);
    }
  }, [isOpen, initialBrand]);

  const executeSearch = async (queryToSearch: string) => {
    if (!queryToSearch.trim()) return;
    setIsLoading(true);
    setHasSearched(true);
    try {
      const results = await fetchLocalStores(queryToSearch.trim(), 8);
      setStores(results);
    } catch (err) {
      console.error('Failed to load local stores:', err);
      setStores([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(searchQuery);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-card max-w-2xl w-full p-6 bg-slate-900/95 border border-white/10 rounded-2xl shadow-2xl backdrop-blur-xl text-left"
        onClick={(e) => e.stopPropagation()}
        style={{ maxHeight: '90vh', overflowY: 'auto' }}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-400/20 text-sky-400">
              <Building2 size={20} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">
                Authorized Brand Stores & Local Centers
              </h3>
              <p className="text-xs text-slate-400">
                Powered by OpenWebNinja Local Business API • Verify physical warranty hubs
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleFormSubmit} className="mt-4 flex gap-2">
          <div className="relative flex-1">
            <Search
              size={18}
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="text"
              className="w-full bg-slate-800/80 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-sky-400 transition-colors"
              placeholder="Search store, city, or hotels (e.g., 'Apple Store San Francisco')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-sm font-semibold flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            <span>Find Stores</span>
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-1.5 mt-3">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Quick Queries:
          </span>
          {POPULAR_QUERIES.map((chip, idx) => (
            <button
              key={idx}
              type="button"
              className="px-2.5 py-1 rounded-md text-xs bg-slate-800/60 hover:bg-slate-700/80 border border-white/5 text-slate-300 hover:text-sky-300 transition-all"
              onClick={() => {
                setSearchQuery(chip);
                executeSearch(chip);
              }}
            >
              {chip}
            </button>
          ))}
        </div>

        {/* Stores Results List */}
        <div className="mt-5 space-y-3">
          {isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-2">
              <Loader2 size={28} className="animate-spin text-sky-400" />
              <span className="text-xs">Querying OpenWebNinja Local Business Directory...</span>
            </div>
          ) : stores.length > 0 ? (
            stores.map((store) => (
              <div
                key={store.business_id}
                className="p-4 rounded-xl bg-slate-800/40 border border-white/5 hover:border-sky-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white">{store.name}</h4>
                    {store.verified && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-1.5 py-0.5 rounded">
                        <ShieldCheck size={11} />
                        <span>Verified</span>
                      </span>
                    )}
                  </div>

                  <div className="flex items-start gap-1.5 text-xs text-slate-300">
                    <MapPin size={13} className="text-sky-400 shrink-0 mt-0.5" />
                    <span>{store.full_address}</span>
                  </div>

                  {store.phone_number && (
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Phone size={12} className="text-slate-400 shrink-0" />
                      <a
                        href={`tel:${store.phone_number}`}
                        className="hover:text-sky-300 transition-colors"
                      >
                        {store.phone_number}
                      </a>
                    </div>
                  )}
                </div>

                <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 shrink-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-white/5">
                  {store.rating && (
                    <div className="flex items-center gap-1 text-xs">
                      <Star size={13} className="text-amber-400 fill-amber-400" />
                      <strong className="text-white font-bold">{store.rating}</strong>
                      {store.review_count && (
                        <span className="text-slate-500 text-[11px]">
                          ({store.review_count.toLocaleString()})
                        </span>
                      )}
                    </div>
                  )}

                  {store.website && (
                    <a
                      href={store.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-sky-400 hover:text-sky-300 underline"
                    >
                      <Globe size={12} />
                      <span>Visit Site</span>
                      <ExternalLink size={10} />
                    </a>
                  )}
                </div>
              </div>
            ))
          ) : hasSearched ? (
            <div className="py-8 text-center text-slate-400 text-xs">
              No matching local stores found for this query. Try a different city or brand.
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="mt-5 pt-3 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-500">
          <span>Official OpenWebNinja Local Business Data</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
