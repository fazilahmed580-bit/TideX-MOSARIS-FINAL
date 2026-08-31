import React, { useState, useEffect } from 'react';
import { Play, Pause } from 'lucide-react';

const TIMELINE_STEPS = [
  { label: 'NOW', offsetHr: 0 },
  { label: '+6h', offsetHr: 6 },
  { label: '+12h', offsetHr: 12 },
  { label: '+18h', offsetHr: 18 },
  { label: '+24h', offsetHr: 24 },
  { label: '+36h', offsetHr: 36 },
  { label: '+48h', offsetHr: 48 },
];

export default function ForecastTimeline({ onStepSelect }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);

  // Play animation timer
  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setActiveIdx((prevIdx) => {
          const nextIdx = (prevIdx + 1) % TIMELINE_STEPS.length;
          if (onStepSelect) onStepSelect(nextIdx);
          return nextIdx;
        });
      }, 1200);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, onStepSelect]);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleStepClick = (idx) => {
    setActiveIdx(idx);
    if (onStepSelect) onStepSelect(idx);
  };

  return (
    <div className="timeline-card">
      <button 
        onClick={togglePlay}
        style={{
          background: isPlaying ? '#0284c7' : '#f1f5f9',
          border: '1px solid #cbd5e1',
          borderRadius: 6,
          width: 34,
          height: 34,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: isPlaying ? '#ffffff' : '#0284c7',
          cursor: 'pointer'
        }}
        title={isPlaying ? 'Pause Drift Animation' : 'Play Drift Animation'}
      >
        {isPlaying ? <Pause size={16} /> : <Play size={16} fill="currentColor" />}
      </button>

      <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#0284c7', textTransform: 'uppercase' }}>
        Drift Timeline
      </div>

      <div className="timeline-ticks">
        {TIMELINE_STEPS.map((step, idx) => (
          <div 
            key={idx}
            className={`timeline-step ${activeIdx === idx ? 'active' : ''}`}
            onClick={() => handleStepClick(idx)}
          >
            {step.label}
          </div>
        ))}
      </div>
    </div>
  );
}
