import React, { useState, useEffect } from 'react';
import { Compass, Play, RefreshCw, Satellite, Radio, Clock, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function Header({ 
  onRunInvestigation, 
  loading, 
  backendConnected 
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
    <header className="top-header">
      {/* Brand */}
      <div className="header-left">
        <div className="brand-icon-box">
          <Compass size={24} />
        </div>
        <div className="brand-titles">
          <h1>
            TideX MOSARIS
            <span style={{ fontSize: '0.65rem', background: '#e0f2fe', color: '#0284c7', padding: '2px 6px', borderRadius: 4, border: '1px solid rgba(2, 132, 199, 0.3)' }}>
              SIH 2026 MVP
            </span>
          </h1>
          <div className="brand-subtitle">
            Maritime Oil-Spill Attribution & Response Intelligence System
          </div>
        </div>
      </div>

      {/* Telemetry & Actions */}
      <div className="header-center-telemetry">
        <div className="telemetry-badge font-mono">
          <Satellite size={14} color="#0284c7" />
          <span className="telemetry-label">SAR SAT:</span>
          <span className="telemetry-val" style={{ color: '#0284c7' }}>SENTINEL-1</span>
        </div>

        <div className="telemetry-badge font-mono">
          <Radio size={14} color="#0284c7" />
          <span className="telemetry-label">AIS FEED:</span>
          <span className="telemetry-val">LIVE • 4 CH</span>
        </div>

        <div className="telemetry-badge font-mono">
          <Clock size={14} color="#475569" />
          <span className="telemetry-label">ZULU:</span>
          <span className="telemetry-val">{utcTime || '12:00:00'} UTC</span>
        </div>

        <div className="telemetry-badge font-mono">
          <span className="telemetry-label">GATEWAY:</span>
          <span className="telemetry-val" style={{ color: backendConnected ? '#16a34a' : '#dc2626' }}>
            {backendConnected ? 'ONLINE • 8000' : 'OFFLINE'}
          </span>
        </div>

        {/* Action Button: RUN INVESTIGATION */}
        <button 
          className="btn-primary-action font-mono" 
          onClick={onRunInvestigation}
          disabled={loading}
        >
          {loading ? (
            <>
              <RefreshCw size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
              RUNNING...
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
