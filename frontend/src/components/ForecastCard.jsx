import React, { useState } from 'react';
import { Compass, Navigation } from 'lucide-react';

export default function ForecastCard({ forecast }) {
  const [showTimelineModal, setShowTimelineModal] = useState(false);

  if (!forecast || forecast.length === 0) {
    return (
      <div className="light-card">
        <div className="card-header-title">
          <span><Navigation size={15} inline style={{ marginRight: 6 }} /> Forward Forecast (P3)</span>
        </div>
        <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          No forward forecast model output available.
        </div>
      </div>
    );
  }

  const lastPoint = forecast[forecast.length - 1];

  return (
    <div className="light-card">
      <div className="card-header-title">
        <span style={{ color: '#0284c7' }}>
          <Navigation size={15} color="#0284c7" inline style={{ marginRight: 6 }} /> FORWARD FORECAST (P3)
        </span>
        <button 
          style={{ background: '#e0f2fe', border: '1px solid rgba(2, 132, 199, 0.3)', color: '#0284c7', borderRadius: 4, padding: '2px 8px', fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer' }}
          onClick={() => setShowTimelineModal(!showTimelineModal)}
        >
          {showTimelineModal ? 'HIDE FORECAST' : 'VIEW FORECAST'}
        </button>
      </div>

      <div className="metrics-row-2">
        <div className="metric-pill">
          <div className="metric-pill-lbl">Particles</div>
          <div className="metric-pill-val font-mono">{forecast.length} waypoints</div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Projected Terminal</div>
          <div className="metric-pill-val font-mono" style={{ fontSize: '0.78rem', color: '#0284c7' }}>
            Lat {lastPoint[1].toFixed(2)}°N, Lon {lastPoint[0].toFixed(2)}°E
          </div>
        </div>
      </div>

      <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: 8, fontStyle: 'italic' }}>
        Current model projects drift north-northeast along Mumbai coastal waters.
      </div>

      {showTimelineModal && (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid #e2e8f0', fontSize: '0.75rem', color: '#475569' }}>
          <strong style={{ color: '#0f172a' }}>Forecast Projection Timeline:</strong>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
            {forecast.map((pt, idx) => (
              <div key={idx} className="font-mono" style={{ fontSize: '0.7rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>Step +{idx * 6}h:</span>
                <span>Lat {pt[1].toFixed(4)}°N, Lon {pt[0].toFixed(4)}°E</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
