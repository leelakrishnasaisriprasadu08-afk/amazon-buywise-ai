import React from 'react';
import { Loader2, CheckCircle2, Clock } from 'lucide-react';
import type { StreamingMilestone } from '../types/buywise';

interface ReasoningTimelineProps {
  milestones: StreamingMilestone[];
  isStreaming: boolean;
}

const STAGES = [
  { step: 1, title: 'Canonical Resolution', code: 'RESOLVE' },
  { step: 2, title: 'Deterministic Pricing', code: 'PRICING' },
  { step: 3, title: 'Review Forensics', code: 'REVIEWS' },
  { step: 4, title: 'Competitor Deltas', code: 'COMPARE' },
  { step: 5, title: 'Multi-Factor Gate', code: 'DECIDE' },
];

export const ReasoningTimeline: React.FC<ReasoningTimelineProps> = ({
  milestones,
  isStreaming,
}) => {
  if (milestones.length === 0 && !isStreaming) return null;

  const currentStep = milestones.length > 0 ? milestones[milestones.length - 1].step : 1;

  return (
    <div className="card timeline-card">
      <div className="timeline-header">
        <div className="timeline-title-row">
          {isStreaming ? (
            <Loader2 size={18} className="spinner-icon" />
          ) : (
            <CheckCircle2 size={18} className="timeline-done-icon" />
          )}
          <h4>{isStreaming ? 'Agent Reasoning Pipeline Streaming...' : 'Decision Pipeline Complete'}</h4>
        </div>
        <span className="timeline-step-badge">Step {Math.min(currentStep, 5)} of 5</span>
      </div>

      {/* Progress Steps Track */}
      <div className="progress-steps-row">
        {STAGES.map((s) => {
          const isDone = currentStep > s.step || !isStreaming;
          const isCurrent = currentStep === s.step && isStreaming;

          return (
            <div
              key={s.step}
              className={`step-bubble ${isDone ? 'step-done' : ''} ${isCurrent ? 'step-current' : ''}`}
            >
              <div className="bubble-indicator">
                {isDone ? (
                  <CheckCircle2 size={14} />
                ) : isCurrent ? (
                  <Loader2 size={14} className="spinner-mini" />
                ) : (
                  <span>{s.step}</span>
                )}
              </div>
              <span className="bubble-label">{s.title}</span>
            </div>
          );
        })}
      </div>

      {/* Live Log Stream */}
      <div className="timeline-log-box">
        {milestones.map((m, idx) => (
          <div key={idx} className="log-entry">
            <span className="log-step-tag">[{m.stage}]</span>
            <span className="log-message">{m.message}</span>
          </div>
        ))}
        {isStreaming && (
          <div className="log-entry log-active">
            <Clock size={12} className="pulse-icon" />
            <span className="log-message">Awaiting next telemetry milestone...</span>
          </div>
        )}
      </div>
    </div>
  );
};
