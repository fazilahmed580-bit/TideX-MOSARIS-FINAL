import React, { useState, useEffect } from 'react';
import { Compass, Play, RefreshCw, Satellite, Radio, HardDrive } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function CommandHeader({ 
  onRunInvestigation, 
  loading, 
  status, 
  backendConnected,
  lastUpdated 
}) {
  const [utcTime, setUtcTime] = useState('');

  // Live UTC Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace('GMT', 'UTC').split(' ').slice(4, 5)[0]);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="top-command-bar">
      {/* Brand & Incident Identification */}
      <div className="header-left-brand">
        <div className="radar-emblem">
          <Compass size={26} />
        </div>
        <div className="brand-titles">
          <h1>
            TideX MOSARIS
            <span className="classification-tag font-mono">SIH 2026</span>
          </h1>
          <p>Maritime Oil-Spill Attribution & Response Intelligence System</p>
        </div>
      </div>

      {/* Center & Right Telemetry Controls */}
      <div className="header-telemetry">
        {/* Sensor Feeds Status */}
        <div className="telemetry-chip font-mono">
          <Satellite size={14} color="#00f2fe" />
          <span className="chip-label">SAR SAT:</span>
          <span className="chip-val" style={{ color: '#00f2fe' }}>SENTINEL-1</span>
        </div>

        <div className="telemetry-chip font-mono">
          <Radio size={14} color="#38bdf8" />
          <span className="chip-label">AIS FEED:</span>
          <span className="chip-val">LIVE 4 CH</span>
        </div>

        {/* Live Clock */}
        <div className="telemetry-chip font-mono">
          <span className="chip-label">ZULU:</span>
          <span className="chip-val" style={{ color: '#00f2fe' }}>{utcTime || '12:00:00'} UTC</span>
        </div>

        {/* Backend Connectivity Status */}
        <div className="telemetry-chip font-mono">
          <div className={`status-indicator ${backendConnected ? 'online' : backendConnected === false ? 'error' : 'busy'}`}></div>
          <span className="chip-label">GATEWAY:</span>
          <span className="chip-val" style={{ color: backendConnected ? '#10b981' : '#f43f5e' }}>
            {backendConnected ? 'ONLINE :8000' : 'OFFLINE'}
          </span>
        </div>

        {/* Primary Action Button */}
        <button 
          className="btn-command-execute font-mono" 
          onClick={onRunInvestigation}
          disabled={loading}
        >
          {loading ? (
            <>
              <RefreshCw size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
              INVESTIGATING...
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              RUN INVESTIGATION
            </>
          )}
        </button>
      </div>
    </header>
  );
}
