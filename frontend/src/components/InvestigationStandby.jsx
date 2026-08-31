import React from 'react';
import { Radio, AlertOctagon, CheckCircle2, Play, Activity, ShieldCheck, Compass } from 'lucide-react';

export default function InvestigationStandby({ onRunInvestigation, backendConnected }) {
  return (
    <div className="standby-wrapper">
      <div className="radar-emblem" style={{ width: 64, height: 64, margin: '0 auto' }}>
        <Radio size={36} color="#00f2fe" />
      </div>

      <div className="standby-target-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#f43f5e', letterSpacing: '0.08em', display: 'flex', alignItems: 'center', gap: 6 }}>
            <AlertOctagon size={16} /> INCIDENT DETECTED
          </div>
          <div className="classification-tag font-mono" style={{ background: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e', border: '1px solid rgba(244, 63, 94, 0.4)' }}>
            CASE: demo_001
          </div>
        </div>

        <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff', marginBottom: 6 }}>
          Arabian Sea Marine Oil-Sill Anomaly
        </div>
        <p style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.45, marginBottom: 16 }}>
          Sentinel-1 SAR telemetry flagged a significant slick signature ~80 km west of Mumbai. Multi-stage hydrodynamic backtracking and AIS vessel attribution pipeline ready to execute.
        </p>

        {/* Readiness Checklist */}
        <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#00f2fe', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
          Pipeline Subsystem Readiness
        </div>

        <div className="checklist-row">
          <span>P1: Sentinel-1 SAR Segmentation</span>
          <span style={{ color: '#10b981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <CheckCircle2 size={13} /> READY
          </span>
        </div>

        <div className="checklist-row">
          <span>P2: Lagrangian Drift Backtracker</span>
          <span style={{ color: '#10b981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <CheckCircle2 size={13} /> READY
          </span>
        </div>

        <div className="checklist-row">
          <span>P3: Spatiotemporal AIS Filtering</span>
          <span style={{ color: '#10b981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <CheckCircle2 size={13} /> READY
          </span>
        </div>

        <div className="checklist-row" style={{ borderBottom: 'none' }}>
          <span>P4: Multi-Factor Attribution Scoring</span>
          <span style={{ color: '#10b981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <CheckCircle2 size={13} /> READY
          </span>
        </div>
      </div>

      <button 
        className="btn-command-execute font-mono" 
        style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '0.9rem' }}
        onClick={onRunInvestigation}
      >
        <Play size={18} fill="currentColor" />
        INITIATE INVESTIGATION PIPELINE
      </button>

      {backendConnected === false && (
        <div style={{ fontSize: '0.72rem', color: '#f43f5e', marginTop: -8 }}>
          ⚠️ Backend Gateway Offline (Run <code>uvicorn main:app --reload --port 8000</code> in terminal)
        </div>
      )}
    </div>
  );
}
