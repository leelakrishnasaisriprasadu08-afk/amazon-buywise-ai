import React from 'react';
import { X, ShieldAlert, CheckCircle, Database, FileText } from 'lucide-react';

interface PrivacyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <ShieldAlert size={22} className="modal-title-icon" />
            <h3>Privacy, Security & Impartiality Policy</h3>
          </div>
          <button
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
            type="button"
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          <section className="policy-section">
            <div className="policy-item-title">
              <CheckCircle size={18} className="policy-check" />
              <h4>1. Zero User Credential Access</h4>
            </div>
            <p>
              BuyWise AI <strong>never requests, accesses, or stores</strong> your Amazon credentials,
              session cookies, payment cards, or private order histories. All operations evaluate strictly
              publicly accessible listing metadata, verified purchase reviews, and historical price records.
            </p>
          </section>

          <section className="policy-section">
            <div className="policy-item-title">
              <Database size={18} className="policy-check" />
              <h4>2. Separation of Math from LLM Inference</h4>
            </div>
            <p>
              To protect shoppers from generative hallucination, all financial computations—including
              effective discounts, rolling 30/90-day medians, and percentile ranks—are executed via
              deterministic Python <code>Decimal</code> mathematics with 0-tolerance rounding invariants.
              Language models are strictly barred from inventing prices.
            </p>
          </section>

          <section className="policy-section">
            <div className="policy-item-title">
              <FileText size={18} className="policy-check" />
              <h4>3. Cryptographic Evidence Provenance</h4>
            </div>
            <p>
              Every claim made in a recommendation report is bound to a verifiable
              <code>ProvenanceEnvelope</code> containing source URLs, retrieval timestamps, and raw payload
              SHA-256 digests. If verified evidence is insufficient, the system explicitly reports
              <strong>INSUFFICIENT EVIDENCE</strong> rather than guessing.
            </p>
          </section>

          <section className="policy-section">
            <div className="policy-item-title">
              <ShieldAlert size={18} className="policy-check" />
              <h4>4. 100% Impartiality Guarantee</h4>
            </div>
            <p>
              BuyWise AI operates independently as a consumer defense intelligence engine. We accept
              <strong>zero sponsored product placements</strong>, zero brand prioritization, and zero
              affiliate ranking distortion.
            </p>
          </section>
        </div>

        <div className="modal-footer">
          <span className="policy-audit-info">Audit Version: 1.0.0 • Amazon Hackathon Project</span>
          <button className="btn-primary" onClick={onClose} type="button">
            Understood & Agree
          </button>
        </div>
      </div>
    </div>
  );
};
