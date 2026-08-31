import React from 'react';
import { X, CheckCircle2, XCircle, AlertTriangle, Eye, Ship } from 'lucide-react';

export default function VesselDetailModal({ 
  vessel, 
  ranking, 
  simulationLayerActive, 
  onToggleSimulation, 
  onClose 
}) {
  if (!vessel || !ranking) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card-light" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="rank-badge-light top-1">
              #{ranking.rank}
            </div>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f172a' }}>
                {vessel.vessel_name || 'Unknown Vessel'}
              </h2>
              <div className="font-mono" style={{ fontSize: '0.75rem', color: '#64748b' }}>
                MMSI: {vessel.mmsi}
              </div>
            </div>
          </div>

          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#64748b' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Score & Parameters */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginBottom: 16 }}>
          <div className="metric-pill">
            <div className="metric-pill-lbl">Priority Score</div>
            <div className="metric-pill-val font-mono" style={{ color: '#0284c7' }}>{ranking.score.toFixed(2)}</div>
          </div>
          <div className="metric-pill">
            <div className="metric-pill-lbl">Distance</div>
            <div className="metric-pill-val font-mono">{vessel.distance_km} km</div>
          </div>
          <div className="metric-pill">
            <div className="metric-pill-lbl">Time Gap</div>
            <div className="metric-pill-val font-mono">{vessel.time_difference_hr} hr</div>
          </div>
          <div className="metric-pill">
            <div className="metric-pill-lbl">Speed</div>
            <div className="metric-pill-val font-mono">{vessel.speed} kts</div>
          </div>
        </div>

        {/* Simulation Toggle Action Button */}
        <button 
          className="btn-primary-action font-mono"
          style={{ 
            width: '100%', 
            justify: 'center', 
            marginBottom: 16,
            background: simulationLayerActive ? '#9333ea' : '#0284c7',
            borderColor: simulationLayerActive ? '#7e22ce' : '#0284c7'
          }}
          onClick={onToggleSimulation}
        >
          <Eye size={16} />
          {simulationLayerActive ? 'HIDE WHAT-IF SIMULATION LAYER' : 'LAUNCH WHAT-IF SPILL SIMULATION'}
        </button>

        {/* Supporting Evidence */}
        <div style={{ background: '#f0fdf4', border: '1px solid rgba(22, 163, 74, 0.3)', borderRadius: 8, padding: 14, marginBottom: 12 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#16a34a', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <CheckCircle2 size={16} /> SUPPORTING EVIDENCE ({ranking.supporting_evidence?.length || 0})
          </div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {ranking.supporting_evidence?.map((item, idx) => (
              <li key={idx} style={{ fontSize: '0.78rem', color: '#14532d', display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                <span style={{ fontWeight: 800 }}>+</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Contradictory Evidence */}
        <div style={{ background: '#fef2f2', border: '1px solid rgba(220, 38, 38, 0.3)', borderRadius: 8, padding: 14, marginBottom: 16 }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#dc2626', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <XCircle size={16} /> CONTRADICTORY EVIDENCE ({ranking.contradictory_evidence?.length || 0})
          </div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {ranking.contradictory_evidence?.map((item, idx) => (
              <li key={idx} style={{ fontSize: '0.78rem', color: '#7f1d1d', display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                <span style={{ fontWeight: 800 }}>-</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Mandatory Disclaimer */}
        <div className="disclaimer-bar-light">
          <AlertTriangle size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>INVESTIGATION PRIORITY SCORE DISCLAIMER:</strong><br/>
            Scores represent investigation priority and are NOT a probability of guilt, legal finding, or proof of legal responsibility.
          </div>
        </div>
      </div>
    </div>
  );
}
