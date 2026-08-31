import React from 'react';
import { AlertOctagon, RefreshCw, ServerOff } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function ConnectionErrorModal({ error, onRetry }) {
  if (!error) return null;

  return (
    <div style={{ padding: '20px' }}>
      <div className="intel-box" style={{ background: 'rgba(244, 63, 94, 0.08)', borderColor: 'rgba(244, 63, 94, 0.4)' }}>
        <div style={{ color: '#f43f5e', fontSize: '0.9rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <ServerOff size={20} /> BACKEND CONNECTION LOST
        </div>

        <p style={{ fontSize: '0.78rem', color: '#fca5a5', lineHeight: 1.45, marginBottom: 12 }}>
          Unable to establish communication with the MOSARIS FastAPI backend at <code>{API_BASE_URL}</code>.
        </p>

        <div style={{ background: 'rgba(2, 6, 23, 0.8)', padding: '10px 12px', borderRadius: 4, fontSize: '0.72rem', color: '#94a3b8', marginBottom: 16 }} className="font-mono">
          $ cd backend<br/>
          $ .\venv\Scripts\Activate.ps1<br/>
          $ uvicorn main:app --reload --port 8000
        </div>

        <button 
          className="btn-command-execute font-mono" 
          style={{ width: '100%', justifyContent: 'center', background: '#f43f5e' }}
          onClick={onRetry}
        >
          <RefreshCw size={15} /> RETRY CONNECTION
        </button>
      </div>
    </div>
  );
}
