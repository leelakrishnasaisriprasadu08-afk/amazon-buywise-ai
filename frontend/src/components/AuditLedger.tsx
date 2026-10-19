import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, AlertCircle, FileCheck, Hash } from 'lucide-react';
import type { RecommendationReport } from '../types/buywise';

interface AuditLedgerProps {
  report: RecommendationReport;
}

export const AuditLedger: React.FC<AuditLedgerProps> = ({ report }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="card audit-card">
      <div className="card-header clickable-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="card-title-group">
          <Database size={20} className="card-icon" />
          <div>
            <h3>Evidence Provenance & Missing Data Ledger</h3>
            <span className="audit-subtitle">
              Cryptographic integrity records and explicit uncertainty disclosures
            </span>
          </div>
        </div>

        <button className="accordion-toggle-btn" type="button" aria-expanded={isOpen}>
          <span>{isOpen ? 'Collapse Audit Ledger' : 'Inspect Audit Ledger'}</span>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Explicit Missing Evidence Disclosures (Always Visible if Present) */}
      {report.missing_evidence.length > 0 && (
        <div className="missing-evidence-box">
          <div className="missing-header">
            <AlertCircle size={16} className="missing-icon" />
            <h5>Explicit Missing Evidence Disclosures</h5>
          </div>
          <ul className="missing-list">
            {report.missing_evidence.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Expandable Technical Provenance Details */}
      {isOpen && (
        <div className="audit-details-drawer">
          <div className="audit-meta-grid">
            <div className="audit-meta-item">
              <span className="audit-meta-label">Generated UTC Timestamp</span>
              <span className="audit-meta-val">{report.generated_at}</span>
            </div>
            <div className="audit-meta-item">
              <span className="audit-meta-label">Evidence Envelopes Ingested</span>
              <span className="audit-meta-val">{report.evidence_envelopes.length} records</span>
            </div>
            <div className="audit-meta-item">
              <span className="audit-meta-label">Audit Store</span>
              <span className="audit-meta-val">SQLite Thread-Safe Ledger (Persisted)</span>
            </div>
          </div>

          <div className="envelopes-list">
            <h5 className="envelopes-title">Cryptographic Ingestion Envelopes</h5>
            {report.evidence_envelopes.map((env, i) => (
              <div key={i} className="envelope-row">
                <div className="envelope-top">
                  <span className="env-source-pill">
                    <FileCheck size={12} />
                    <span>{env.source_type}</span>
                  </span>
                  <span className="env-uri">{env.source_url}</span>
                </div>
                {env.raw_hash_sha256 && (
                  <div className="envelope-hash-row">
                    <Hash size={12} className="hash-icon" />
                    <span className="env-hash">SHA-256: {env.raw_hash_sha256}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
