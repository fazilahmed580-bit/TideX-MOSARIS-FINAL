import React from 'react';
import { Ship, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function VesselAttributionMatrix({ 
  candidates, 
  rankings, 
  selectedVesselMmsi, 
  onSelectVessel 
}) {
  if (!candidates || !rankings) return null;

  // Merge candidate track info with ranking score
  const sortedDeck = rankings.map(r => {
    const candidate = candidates.find(c => c.mmsi === r.mmsi);
    return {
      ...candidate,
      ...r,
    };
  }).sort((a, b) => a.rank - b.rank);

  return (
    <div className="intel-box">
      <div className="intel-box-title">
        <span><Ship size={15} color="#00f2fe" inline style={{ marginRight: 6 }} /> Ranked Candidate Attribution (P3/P4)</span>
        <span style={{ fontSize: '0.68rem', color: '#00f2fe', fontWeight: 800 }}>
          {sortedDeck.length} CANDIDATES
        </span>
      </div>

      <div className="vessel-deck">
        {sortedDeck.map((vessel) => {
          const isSelected = vessel.mmsi === selectedVesselMmsi;
          const isTopRank = vessel.rank === 1;

          return (
            <div 
              key={vessel.mmsi} 
              className={`vessel-card-tactical ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelectVessel(vessel.mmsi)}
            >
              <div className="vessel-card-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div className={`rank-pill ${isTopRank ? 'top-priority' : ''}`}>
                    #{vessel.rank}
                  </div>
                  <div>
                    <div className="vessel-name-heading" style={{ color: isTopRank ? '#f43f5e' : '#ffffff' }}>
                      {vessel.vessel_name || 'Unknown Vessel'}
                    </div>
                    <div className="vessel-mmsi-sub font-mono">
                      MMSI: {vessel.mmsi}
                    </div>
                  </div>
                </div>

                <div className="score-badge-hud">
                  <div className="score-num-big font-mono" style={{ color: isTopRank ? '#f43f5e' : '#00f2fe' }}>
                    {vessel.score.toFixed(2)}
                  </div>
                  <div className="score-lbl-sub">Priority Score</div>
                </div>
              </div>

              {isTopRank && (
                <div style={{ 
                  fontSize: '0.65rem', 
                  fontWeight: 800, 
                  color: '#f43f5e', 
                  letterSpacing: '0.08em', 
                  background: 'rgba(244, 63, 94, 0.12)', 
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  padding: '3px 8px', 
                  borderRadius: 4, 
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                  marginBottom: 4
                }}>
                  <ShieldAlert size={12} /> HIGH ATTRIBUTION PRIORITY
                </div>
              )}

              <div className="vessel-data-strip font-mono">
                <div className="strip-item">
                  <span className="strip-item-lbl">DIST TO ORIGIN</span>
                  <span className="strip-item-val">{vessel.distance_km} km</span>
                </div>
                <div className="strip-item">
                  <span className="strip-item-lbl">TIME GAP</span>
                  <span className="strip-item-val">{vessel.time_difference_hr} hr</span>
                </div>
                <div className="strip-item">
                  <span className="strip-item-lbl">SPEED</span>
                  <span className="strip-item-val">{vessel.speed} kts</span>
                </div>
                <div className="strip-item">
                  <span className="strip-item-lbl">HEADING</span>
                  <span className="strip-item-val">{vessel.heading}°</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
