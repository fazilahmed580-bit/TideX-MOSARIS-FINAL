import React, { useEffect, useState } from 'react';
import { Satellite, Navigation, Ship, Award, CheckCircle } from 'lucide-react';

const PIPELINE_STAGES = [
  { step: 'SAR-P1', label: 'Processing Sentinel-1 SAR Oil Spill Geometry (Polygon & Centroid)...' },
  { step: 'DRIFT-P2', label: 'Executing Reverse Hydrodynamic Particle Backtracking & Origin Window...' },
  { step: 'AIS-P3', label: 'Querying Historical AIS Corridor & Filtering Candidate Vessel Trajectories...' },
  { step: 'ATTRIB-P4', label: 'Computing Evidence Ranking Vectors & Forward Spill What-If Simulations...' },
  { step: 'SYNTH-P5', label: 'Synthesizing Full MOSARIS Attribution Dossier...' }
];

export default function InvestigationProgressHUD({ loading }) {
  const [currentIdx, setCurrentIdx] = useState(0);

  useEffect(() => {
    if (!loading) {
      setCurrentIdx(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentIdx((prev) => (prev < PIPELINE_STAGES.length - 1 ? prev + 1 : prev));
    }, 400);

    return () => clearInterval(interval);
  }, [loading]);

  if (!loading) return null;

  return (
    <div className="mission-loading-hud">
      <div className="mission-radar-spinner"></div>
      
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '1.1rem', fontWeight: 900, letterSpacing: '0.12em', color: '#00f2fe', marginBottom: 4 }}>
          EXECUTING MOSARIS ATTRIBUTION ENGINE
        </div>
        <div className="font-mono" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          LIVE PIPELINE ORCHESTRATION IN PROGRESS
        </div>
      </div>

      <div className="mission-stage-text font-mono">
        <span style={{ color: '#00f2fe', fontWeight: 800, marginRight: 8 }}>
          [{PIPELINE_STAGES[currentIdx].step}]
        </span>
        {PIPELINE_STAGES[currentIdx].label}
      </div>
    </div>
  );
}
