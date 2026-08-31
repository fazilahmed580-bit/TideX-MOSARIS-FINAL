import React from 'react';
import { AlertTriangle, Target, MapPin, Compass } from 'lucide-react';

export default function IncidentIntelligence({ spill, source }) {
  if (!spill || !source) return null;

  return (
    <>
      {/* P1 SAR Spill Detection */}
      <div className="intel-box highlight">
        <div className="intel-box-title">
          <span><AlertTriangle size={15} color="#f43f5e" inline style={{ marginRight: 6 }} /> SAR Oil Spill Detection (P1)</span>
          <span style={{ fontSize: '0.68rem', color: '#f43f5e', fontWeight: 800 }}>POSITIVE DETECTION</span>
        </div>

        <div className="metric-grid-2">
          <div className="metric-cell">
            <div className="metric-cell-lbl">Case Identifier</div>
            <div className="metric-cell-val cyan font-mono">{spill.spill_id}</div>
          </div>

          <div className="metric-cell">
            <div className="metric-cell-lbl">Attribution Confidence</div>
            <div className="metric-cell-val cyan">{Math.round(spill.confidence * 100)}%</div>
          </div>

          <div className="metric-cell">
            <div className="metric-cell-lbl">Estimated Slick Area</div>
            <div className="metric-cell-val red">{spill.area_km2} km²</div>
          </div>

          <div className="metric-cell">
            <div className="metric-cell-lbl">Detection Sensor</div>
            <div className="metric-cell-val green" style={{ fontSize: '0.85rem' }}>SENTINEL-1 SAR</div>
          </div>
        </div>

        <div className="metric-cell" style={{ marginTop: 10 }}>
          <div className="metric-cell-lbl">Centroid Coordinates (API Contract)</div>
          <div className="metric-cell-val font-mono" style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Lat {spill.centroid[0].toFixed(4)}°N, Lon {spill.centroid[1].toFixed(4)}°E
          </div>
        </div>

        <div className="metric-cell" style={{ marginTop: 6 }}>
          <div className="metric-cell-lbl">Observation Acquisition Time</div>
          <div className="metric-cell-val font-mono" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            {spill.timestamp}
          </div>
        </div>
      </div>

      {/* P2 Source Backtracking */}
      <div className="intel-box">
        <div className="intel-box-title">
          <span><Target size={15} color="#f59e0b" inline style={{ marginRight: 6 }} /> Reverse Drift Backtracking (P2)</span>
        </div>

        <div className="metric-cell">
          <div className="metric-cell-lbl">Estimated Spill Release Window</div>
          <div className="metric-cell-val font-mono amber" style={{ fontSize: '0.78rem' }}>
            {source.origin_time_start} <br/> to {source.origin_time_end}
          </div>
        </div>

        <div className="metric-grid-2" style={{ marginTop: 10 }}>
          <div className="metric-cell">
            <div className="metric-cell-lbl">Backward Drift Track</div>
            <div className="metric-cell-val">{source.backward_particles?.length || 0} particles</div>
          </div>

          <div className="metric-cell">
            <div className="metric-cell-lbl">Uncertainty Envelope</div>
            <div className="metric-cell-val green" style={{ fontSize: '0.85rem' }}>ACTIVE BOUND</div>
          </div>
        </div>
      </div>
    </>
  );
}
