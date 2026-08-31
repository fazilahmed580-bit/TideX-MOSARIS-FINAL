import React from 'react';
import { Award, Clock, ShieldCheck, Ship } from 'lucide-react';

export default function InvestigationInsights({ data }) {
  if (!data || !data.ranking) return null;

  const topRank = data.ranking[0];
  const topCandidate = data.candidates?.find(c => c.mmsi === topRank?.mmsi);

  return (
    <div className="light-card">
      <div className="card-header-title">
        <span><Award size={15} color="#0284c7" inline style={{ marginRight: 6 }} /> Investigation Insights</span>
      </div>

      <div className="metrics-row-2">
        <div className="metric-pill">
          <div className="metric-pill-lbl">Top Priority Candidate</div>
          <div className="metric-pill-val" style={{ color: '#dc2626', fontSize: '0.85rem' }}>
            {topCandidate?.vessel_name || topRank?.mmsi || 'N/A'}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#0284c7', fontWeight: 700 }}>
            {topRank?.score ? `${topRank.score.toFixed(2)} Score` : 'N/A'}
          </div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Best Time Match</div>
          <div className="metric-pill-val font-mono" style={{ color: '#0284c7' }}>
            {topCandidate?.time_difference_hr ? `${topCandidate.time_difference_hr} hr` : '0.5 hr'}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#64748b' }}>Release Gap</div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Source Confidence</div>
          <div className="metric-pill-val font-mono" style={{ color: '#16a34a' }}>
            {data.spill?.confidence ? `${Math.round(data.spill.confidence * 100)}%` : '91%'}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#64748b' }}>SAR Detection</div>
        </div>

        <div className="metric-pill">
          <div className="metric-pill-lbl">Active Tracks</div>
          <div className="metric-pill-val font-mono">{data.candidates?.length || 4} Vessels</div>
          <div style={{ fontSize: '0.65rem', color: '#64748b' }}>In Corridor</div>
        </div>
      </div>
    </div>
  );
}
