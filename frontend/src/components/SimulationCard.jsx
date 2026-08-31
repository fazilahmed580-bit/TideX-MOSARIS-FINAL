import React from 'react';
import { Eye, Sparkles } from 'lucide-react';

export default function SimulationCard({ 
  candidates, 
  selectedVesselMmsi, 
  onSelectVessel, 
  simulationLayerActive, 
  onToggleSimulation 
}) {
  if (!candidates || candidates.length === 0) {
    return (
      <div className="light-card">
        <div className="card-header-title">
          <span><Sparkles size={15} inline style={{ marginRight: 6 }} /> What-If Simulation (P4)</span>
        </div>
        <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          No candidate vessels available for simulation.
        </div>
      </div>
    );
  }

  const selectedVessel = candidates.find(c => c.mmsi === selectedVesselMmsi) || candidates[0];

  return (
    <div className="light-card">
      <div className="card-header-title">
        <span style={{ color: '#d946ef' }}>
          <Sparkles size={15} color="#d946ef" inline style={{ marginRight: 6 }} /> WHAT-IF SIMULATION (P4)
        </span>
      </div>

      <div style={{ marginBottom: 8 }}>
        <div style={{ fontSize: '0.65rem', color: '#64748b', fontWeight: 700, textTransform: 'uppercase', marginBottom: 4 }}>
          Target Vessel Scenario
        </div>
        <select 
          value={selectedVesselMmsi || ''} 
          onChange={(e) => onSelectVessel(e.target.value)}
          style={{
            width: '100%',
            background: '#ffffff',
            color: '#0f172a',
            border: '1px solid #cbd5e1',
            borderRadius: 4,
            padding: '6px 8px',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          {candidates.map(c => (
            <option key={c.mmsi} value={c.mmsi}>
              {c.vessel_name || c.mmsi} (MMSI {c.mmsi})
            </option>
          ))}
        </select>
      </div>

      <button 
        style={{
          width: '100%',
          background: simulationLayerActive ? '#d946ef' : '#faf5ff',
          color: simulationLayerActive ? '#ffffff' : '#d946ef',
          border: '1px solid rgba(217, 70, 239, 0.4)',
          borderRadius: 6,
          padding: '8px 12px',
          fontSize: '0.78rem',
          fontWeight: 700,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
          transition: 'all 0.2s ease'
        }}
        onClick={onToggleSimulation}
      >
        <Eye size={15} />
        {simulationLayerActive ? 'HIDE SIMULATION LAYER' : 'RUN WHAT-IF SIMULATION'}
      </button>

      <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: 8, fontStyle: 'italic' }}>
        Visualizes simulated slick trajectory if {selectedVessel.vessel_name || selectedVessel.mmsi} was the origin.
      </div>
    </div>
  );
}
