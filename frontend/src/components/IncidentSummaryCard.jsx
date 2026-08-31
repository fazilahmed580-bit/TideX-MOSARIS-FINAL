import React from 'react';
import { AlertOctagon } from 'lucide-react';

export default function IncidentSummaryCard({ spill }) {
  if (!spill) {
    return (
      <div className="light-card">
        <div className="card-header-title" style={{ color: '#64748b' }}>
          <span><AlertOctagon size={15} inline style={{ marginRight: 6 }} /> Incident Summary</span>
        </div>
        <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          No active incident loaded. Click "RUN INVESTIGATION" to load telemetry data.
        </div>
      </div>
    );
  }

  return (
    <div className="light-card" style={{ borderColor: 'rgba(220, 38, 38, 0.3)', background: '#fff' }}>
      <div className="card-header-title">
        <span style={{ color: '#dc2626' }}>
          <AlertOctagon size={15} color="#dc2626" inline style={{ marginRight: 6 }} /> SPILL DETECTED
        </span>
        <span style={{ fontSize: '0.65rem', background: '#fef2f2', color: '#dc2626', padding: '2px 6px', borderRadius: 4, fontWeight: 700 }}>
          CONFIRMED
        </span>
      </div>

      <div className="metrics-row-2">
        <div className="metric-pill">
          <div className="metric-pill-lbl">ID</div>
          <div className="metric-pill-val font-mono" style={{ color: '#0284c7' }}>{spill.spill_id}</div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Status</div>
          <div className="metric-pill-val" style={{ color: '#dc2626', fontSize: '0.85rem' }}>
            {spill.spill_detected ? 'ACTIVE' : 'INACTIVE'}
          </div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Area</div>
          <div className="metric-pill-val" style={{ color: '#dc2626' }}>{spill.area_km2} km²</div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Confidence</div>
          <div className="metric-pill-val" style={{ color: '#0284c7' }}>{Math.round(spill.confidence * 100)}%</div>
        </div>
      </div>

      <div className="metric-pill" style={{ marginTop: 8 }}>
        <div className="metric-pill-lbl">Centroid Location</div>
        <div className="metric-pill-val font-mono" style={{ fontSize: '0.78rem', color: '#475569' }}>
          Lat {spill.centroid[0].toFixed(4)}°N, Lon {spill.centroid[1].toFixed(4)}°E
        </div>
      </div>

      <div className="metric-pill" style={{ marginTop: 6 }}>
        <div className="metric-pill-lbl">Time</div>
        <div className="metric-pill-val font-mono" style={{ fontSize: '0.75rem', color: '#475569' }}>
          {spill.timestamp}
        </div>
      </div>
    </div>
  );
}
