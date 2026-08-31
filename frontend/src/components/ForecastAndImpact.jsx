import React from 'react';
import { Navigation, Compass, AlertCircle } from 'lucide-react';

export default function ForecastAndImpact({ forecast }) {
  if (!forecast || forecast.length === 0) return null;

  const lastPoint = forecast[forecast.length - 1];

  return (
    <div className="intel-box">
      <div className="intel-box-title">
        <span><Navigation size={15} color="#10b981" inline style={{ marginRight: 6 }} /> Forward Drift Forecast & Shoreline Impact (P2)</span>
      </div>

      <div className="metric-grid-2">
        <div className="metric-cell">
          <div className="metric-cell-lbl">Forecast Particles</div>
          <div className="metric-cell-val">{forecast.length} waypoints</div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell-lbl">Projected Terminal Grid</div>
          <div className="metric-cell-val font-mono green" style={{ fontSize: '0.78rem' }}>
            Lat {lastPoint[1].toFixed(2)}°N, Lon {lastPoint[0].toFixed(2)}°E
          </div>
        </div>
      </div>

      <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 6, padding: '10px 12px', marginTop: 10 }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#10b981', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <AlertCircle size={14} /> COASTAL DRIFT TRAJECTORY
        </div>
        <p style={{ fontSize: '0.72rem', color: '#94a3b8', lineHeight: 1.4 }}>
          Prevailing northward coastal currents project surface oil slick drift toward the Mumbai/Maharashtra coastal corridor within 18–24 hours. Containment boom deployment recommended along western approaches.
        </p>
      </div>
    </div>
  );
}
