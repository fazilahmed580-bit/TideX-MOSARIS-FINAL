import React, { useState } from 'react';
import { Target, Info, CheckCircle2 } from 'lucide-react';

export default function SourceAttributionCard({ source }) {
  const [showDetails, setShowDetails] = useState(false);

  if (!source) {
    return (
      <div className="light-card">
        <div className="card-header-title">
          <span><Target size={15} inline style={{ marginRight: 6 }} /> Source Attribution (P2)</span>
        </div>
        <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          No source backtracking data available.
        </div>
      </div>
    );
  }

  return (
    <div className="light-card">
      <div className="card-header-title">
        <span style={{ color: '#16a34a' }}>
          <Target size={15} color="#16a34a" inline style={{ marginRight: 6 }} /> SOURCE ATTRIBUTION (P2)
        </span>
        <button 
          style={{ background: '#f0fdf4', border: '1px solid rgba(22, 163, 74, 0.3)', color: '#16a34a', borderRadius: 4, padding: '2px 8px', fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer' }}
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'HIDE DETAILS' : 'VIEW DETAILS'}
        </button>
      </div>

      <div className="metric-pill" style={{ marginBottom: 8 }}>
        <div className="metric-pill-lbl">Origin Time Window</div>
        <div className="metric-pill-val font-mono" style={{ fontSize: '0.78rem', color: '#16a34a' }}>
          {source.origin_time_start} to {source.origin_time_end}
        </div>
      </div>

      <div className="metrics-row-2">
        <div className="metric-pill">
          <div className="metric-pill-lbl">Backward Drift</div>
          <div className="metric-pill-val font-mono">{source.backward_particles?.length || 0} pts</div>
        </div>
        <div className="metric-pill">
          <div className="metric-pill-lbl">Uncertainty Envelope</div>
          <div className="metric-pill-val" style={{ color: '#d97706', fontSize: '0.8rem' }}>ACTIVE</div>
        </div>
      </div>

      {showDetails && (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid #e2e8f0', fontSize: '0.75rem', color: '#475569', lineHeight: 1.4 }}>
          <strong style={{ color: '#0f172a' }}>Backtracking Hydrodynamics:</strong><br/>
          Lagrangian particle tracking model computed 7 reverse drift steps from the detected slick centroid to estimate the initial discharge window.
        </div>
      )}
    </div>
  );
}
