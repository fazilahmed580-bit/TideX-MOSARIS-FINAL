import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Eye, ShieldAlert, Sparkles } from 'lucide-react';

export default function EvidenceAndSimulation({ 
  selectedVessel, 
  ranking, 
  simulation, 
  simulationLayerActive, 
  onToggleSimulation 
}) {
  if (!selectedVessel || !ranking) return null;

  return (
    <div className="intel-box" style={{ background: '#091122', borderColor: 'rgba(0, 242, 254, 0.2)' }}>
      <div className="intel-box-title">
        <span>
          <Sparkles size={15} color="#00f2fe" inline style={{ marginRight: 6 }} />
          Evidence Dossier: {selectedVessel.vessel_name || selectedVessel.mmsi}
        </span>
      </div>

      {/* What-If Simulation Toggle Button */}
      <button 
        className="btn-command-execute font-mono" 
        style={{ 
          width: '100%', 
          justify: 'center', 
          marginBottom: 12,
          padding: '10px 14px',
          background: simulationLayerActive ? 'linear-gradient(135deg, #c084fc 0%, #7e22ce 100%)' : 'rgba(255, 255, 255, 0.05)',
          borderColor: 'rgba(192, 132, 252, 0.5)',
          boxShadow: simulationLayerActive ? '0 0 20px rgba(192, 132, 252, 0.4)' : 'none'
        }}
        onClick={onToggleSimulation}
      >
        <Eye size={16} />
        {simulationLayerActive ? 'HIDE WHAT-IF SIMULATION LAYER' : 'LAUNCH WHAT-IF SPILL SIMULATION'}
      </button>

      {/* Supporting Evidence */}
      <div className="evidence-container">
        <div className="evidence-header-tag" style={{ color: '#34d399' }}>
          <CheckCircle2 size={15} /> SUPPORTING EVIDENCE ({ranking.supporting_evidence?.length || 0})
        </div>
        <ul className="evidence-list">
          {ranking.supporting_evidence?.map((item, idx) => (
            <li key={idx} className="evidence-row support">
              <span>+</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>

        {/* Contradictory Evidence */}
        <div className="evidence-header-tag" style={{ color: '#f87171', marginTop: 14 }}>
          <XCircle size={15} /> CONTRADICTORY EVIDENCE ({ranking.contradictory_evidence?.length || 0})
        </div>
        <ul className="evidence-list">
          {ranking.contradictory_evidence?.map((item, idx) => (
            <li key={idx} className="evidence-row contradict">
              <span>-</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Mandatory Attribution Score Disclaimer Notice */}
      <div className="score-legal-disclaimer">
        <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: 1, color: '#f59e0b' }} />
        <div>
          <strong>INVESTIGATION PRIORITY DISCLAIMER:</strong><br/>
          Scores represent multi-factor attribution confidence for operational investigation prioritization only. They do <u>NOT</u> constitute legal proof, criminal culpability, or proof of guilt.
        </div>
      </div>
    </div>
  );
}
