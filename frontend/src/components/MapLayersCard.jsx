import React from 'react';
import { Layers } from 'lucide-react';

export default function MapLayersCard({ layers, onToggleLayer }) {
  return (
    <div className="light-card">
      <div className="card-header-title">
        <span><Layers size={15} inline style={{ marginRight: 6 }} /> Map Layers</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#dc2626', marginRight: 8 }}></span>
            Detected Spill (P1)
          </span>
          <input 
            type="checkbox" 
            checked={layers.spill} 
            onChange={() => onToggleLayer('spill')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#16a34a', marginRight: 8 }}></span>
            Source Region (P2)
          </span>
          <input 
            type="checkbox" 
            checked={layers.source} 
            onChange={() => onToggleLayer('source')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#f59e0b', marginRight: 8 }}></span>
            Uncertainty Boundary
          </span>
          <input 
            type="checkbox" 
            checked={layers.uncertainty} 
            onChange={() => onToggleLayer('uncertainty')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#9333ea', marginRight: 8 }}></span>
            Backward Drift Path
          </span>
          <input 
            type="checkbox" 
            checked={layers.backwardDrift} 
            onChange={() => onToggleLayer('backwardDrift')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#0284c7', marginRight: 8 }}></span>
            Forward Forecast (P2)
          </span>
          <input 
            type="checkbox" 
            checked={layers.forecast} 
            onChange={() => onToggleLayer('forecast')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#2563eb', marginRight: 8 }}></span>
            AIS Vessels & Tracks (P3)
          </span>
          <input 
            type="checkbox" 
            checked={layers.vessels} 
            onChange={() => onToggleLayer('vessels')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', cursor: 'pointer', userSelect: 'none' }}>
          <span>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#d946ef', marginRight: 8 }}></span>
            What-If Simulation (P4)
          </span>
          <input 
            type="checkbox" 
            checked={layers.simulation} 
            onChange={() => onToggleLayer('simulation')}
            style={{ accentColor: '#0284c7', width: 15, height: 15, cursor: 'pointer' }}
          />
        </label>
      </div>

      {/* Visual Legend */}
      <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid #e2e8f0' }}>
        <div style={{ fontSize: '0.65rem', color: '#64748b', fontWeight: 800, textTransform: 'uppercase', marginBottom: 6 }}>
          Visual Legend
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 4, fontSize: '0.7rem', color: '#475569' }}>
          <div>🔴 Detected Spill</div>
          <div>🟩 Source Origin</div>
          <div>🟨 Uncertainty Envelope</div>
          <div>🟪 Backward Drift</div>
          <div>🟦 Forward Forecast</div>
          <div>🔺 AIS Vessel Target</div>
          <div style={{ gridColumn: 'span 2' }}>🔮 What-If Simulation (P4)</div>
        </div>
      </div>
    </div>
  );
}
