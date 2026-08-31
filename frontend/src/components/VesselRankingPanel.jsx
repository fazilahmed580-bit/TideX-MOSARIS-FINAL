import React from 'react';
import { Ship, Info } from 'lucide-react';

export default function VesselRankingPanel({ 
  candidates, 
  rankings, 
  selectedVesselMmsi, 
  onSelectVessel,
  onOpenDetails 
}) {
  if (!candidates || !rankings) {
    return (
      <div className="light-card">
        <div className="card-header-title">
          <span><Ship size={15} inline style={{ marginRight: 6 }} /> Ranked Vessel Attribution (P3 / P4)</span>
        </div>
        <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          No vessel candidates loaded. Execute investigation to extract AIS tracks and compute attribution scores.
        </div>
      </div>
    );
  }

  // Merge candidate info with ranking scores and order by rank
  const sortedCandidates = rankings.map(r => {
    const candidate = candidates.find(c => c.mmsi === r.mmsi);
    return {
      ...candidate,
      ...r,
    };
  }).sort((a, b) => a.rank - b.rank);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div className="card-header-title" style={{ padding: '0 4px', margin: 0 }}>
        <span style={{ color: '#0f172a' }}>
          <Ship size={16} color="#0284c7" inline style={{ marginRight: 6 }} /> RANKED VESSEL ATTRIBUTION (P3/P4)
        </span>
        <span style={{ fontSize: '0.65rem', background: '#e0f2fe', color: '#0284c7', padding: '2px 6px', borderRadius: 4, fontWeight: 700 }}>
          {sortedCandidates.length} CANDIDATES
        </span>
      </div>

      {sortedCandidates.map((vessel) => {
        const isSelected = vessel.mmsi === selectedVesselMmsi;
        const isTopRank = vessel.rank === 1;

        return (
          <div 
            key={vessel.mmsi} 
            className={`vessel-card-light ${isSelected ? 'selected' : ''}`}
            onClick={() => onSelectVessel(vessel.mmsi)}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div className={`rank-badge-light ${isTopRank ? 'top-1' : ''}`}>
                  #{vessel.rank}
                </div>
                <div>
                  <div style={{ fontSize: '0.92rem', fontWeight: 800, color: isTopRank ? '#dc2626' : '#0f172a' }}>
                    {vessel.vessel_name || 'Unknown Vessel'}
                  </div>
                  <div className="font-mono" style={{ fontSize: '0.72rem', color: '#64748b' }}>
                    MMSI: {vessel.mmsi}
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div className="vessel-score-val font-mono" style={{ color: isTopRank ? '#dc2626' : '#0284c7' }}>
                  {vessel.score.toFixed(2)}
                </div>
                <div style={{ fontSize: '0.6rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>
                  Priority Score
                </div>
              </div>
            </div>

            {isTopRank && (
              <div style={{ 
                fontSize: '0.65rem', 
                fontWeight: 800, 
                color: '#dc2626', 
                background: '#fef2f2', 
                border: '1px solid rgba(220, 38, 38, 0.3)',
                padding: '2px 8px', 
                borderRadius: 4, 
                display: 'inline-block',
                marginBottom: 4 
              }}>
                HIGH PRIORITY CANDIDATE
              </div>
            )}

            <div className="vessel-details-grid font-mono">
              <div>
                <div style={{ fontSize: '0.6rem', color: '#64748b' }}>DIST</div>
                <div style={{ fontWeight: 600, color: '#334155' }}>{vessel.distance_km} km</div>
              </div>
              <div>
                <div style={{ fontSize: '0.6rem', color: '#64748b' }}>TIME GAP</div>
                <div style={{ fontWeight: 600, color: '#334155' }}>{vessel.time_difference_hr} hr</div>
              </div>
              <div>
                <div style={{ fontSize: '0.6rem', color: '#64748b' }}>SPEED</div>
                <div style={{ fontWeight: 600, color: '#334155' }}>{vessel.speed} kts</div>
              </div>
              <div>
                <div style={{ fontSize: '0.6rem', color: '#64748b' }}>HEADING</div>
                <div style={{ fontWeight: 600, color: '#334155' }}>{vessel.heading}°</div>
              </div>
            </div>

            <div style={{ marginTop: 10, display: 'flex', justifyContent: 'flex-end' }}>
              <button 
                style={{
                  background: isSelected ? '#0284c7' : '#f1f5f9',
                  color: isSelected ? '#ffffff' : '#0284c7',
                  border: '1px solid #cbd5e1',
                  borderRadius: 4,
                  padding: '4px 10px',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectVessel(vessel.mmsi);
                  onOpenDetails(vessel.mmsi);
                }}
              >
                <Info size={12} /> VIEW DETAILS
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
