import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MapView from './components/MapView';
import MapLayersCard from './components/MapLayersCard';
import IncidentSummaryCard from './components/IncidentSummaryCard';
import ForecastTimeline from './components/ForecastTimeline';
import VesselRankingPanel from './components/VesselRankingPanel';
import VesselDetailModal from './components/VesselDetailModal';
import InvestigationInsights from './components/InvestigationInsights';
import SourceAttributionCard from './components/SourceAttributionCard';
import ForecastCard from './components/ForecastCard';
import SimulationCard from './components/SimulationCard';
import DisclaimerBar from './components/DisclaimerBar';
import { runInvestigation, checkBackendHealth, API_BASE_URL } from './services/api';
import { 
  AlertOctagon, Ship, FileText, Settings, HelpCircle, 
  ServerOff, RefreshCw, BarChart2, Compass, Play
} from 'lucide-react';

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('standby');
  const [backendConnected, setBackendConnected] = useState(null);
  const [selectedVesselMmsi, setSelectedVesselMmsi] = useState(null);
  const [activeNavTab, setActiveNavTab] = useState('dashboard');
  const [detailModalMmsi, setDetailModalMmsi] = useState(null);
  const [notification, setNotification] = useState(null);
  const [timelineStep, setTimelineStep] = useState(0);

  // Map layer controls
  const [layers, setLayers] = useState({
    spill: true,
    source: true,
    uncertainty: true,
    backwardDrift: true,
    forecast: true,
    vessels: true,
    simulation: true,
  });

  // Toast notification helper
  const showToast = (msg, duration = 4000) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), duration);
  };

  // Check connection on mount using POST /investigate
  useEffect(() => {
    async function init() {
      try {
        const health = await checkBackendHealth();
        setBackendConnected(health !== null);
      } catch (err) {
        setBackendConnected(false);
      }
    }
    init();
  }, []);

  const handleToggleLayer = (layerKey) => {
    setLayers(prev => ({
      ...prev,
      [layerKey]: !prev[layerKey]
    }));
  };

  const handleRunInvestigation = async (spillId = 'demo_001', userInitiated = true) => {
    setLoading(true);
    setError(null);
    setStatus('running');

    try {
      const result = await runInvestigation(spillId);
      setData(result);
      setStatus('complete');
      setBackendConnected(true);
      setError(null);

      // Auto select Rank #1 candidate vessel
      if (result.ranking && result.ranking.length > 0) {
        setSelectedVesselMmsi(result.ranking[0].mmsi);
      }

      if (userInitiated) {
        showToast(`✅ Investigation Pipeline executed for ${spillId} (Gulf of Mexico)!`);
      }
    } catch (err) {
      setError(err.message);
      setStatus('error');
      setBackendConnected(false);
    } finally {
      setLoading(false);
    }
  };

  // Find selected vessel & ranking objects
  const selectedVessel = data?.candidates?.find(c => c.mmsi === (detailModalMmsi || selectedVesselMmsi));
  const selectedRanking = data?.ranking?.find(r => r.mmsi === (detailModalMmsi || selectedVesselMmsi));
  const selectedSimulation = data?.simulations?.find(s => s.mmsi === (detailModalMmsi || selectedVesselMmsi));

  return (
    <div className="app-layout">
      {/* Top Header */}
      <Header 
        onRunInvestigation={() => handleRunInvestigation('demo_001', true)}
        loading={loading}
        backendConnected={backendConnected}
      />

      {/* Main Workspace Container */}
      <div className="workspace-container">
        {/* Left Navigation Rail */}
        <Sidebar activeTab={activeNavTab} onSelectTab={setActiveNavTab} />

        {/* Dynamic Nav Views */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
          
          {/* Notification Toast */}
          {notification && (
            <div style={{
              background: '#e0f2fe',
              borderBottom: '1px solid rgba(2, 132, 199, 0.3)',
              color: '#0369a1',
              padding: '8px 24px',
              fontSize: '0.8rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              zIndex: 1100
            }}>
              <span>{notification}</span>
              <button onClick={() => setNotification(null)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#0369a1', fontWeight: 800 }}>✕</button>
            </div>
          )}

          {/* TAB 1: DASHBOARD (3-Column View) */}
          {activeNavTab === 'dashboard' && (
            <div className="dashboard-grid-layout">
              {/* API Error Notification */}
              {error && (
                <div style={{ gridColumn: '1 / -1', background: '#fef2f2', border: '1px solid rgba(220, 38, 38, 0.3)', borderRadius: 8, padding: 16 }}>
                  <div style={{ color: '#dc2626', fontSize: '0.9rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <ServerOff size={18} /> BACKEND CONNECTION FAILED
                  </div>
                  <p style={{ fontSize: '0.78rem', color: '#991b1b', marginBottom: 12 }}>
                    Error connecting to FastAPI backend at <code>{API_BASE_URL}</code>:
                    <br/>
                    <code>{error}</code>
                  </p>
                  <button 
                    className="btn-primary-action font-mono"
                    style={{ background: '#dc2626' }}
                    onClick={() => handleRunInvestigation('demo_001', true)}
                  >
                    <RefreshCw size={14} /> RETRY CONNECTION
                  </button>
                </div>
              )}

              {/* COLUMN 1 (LEFT): Map Layers + Incident Summary */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <MapLayersCard layers={layers} onToggleLayer={handleToggleLayer} />
                <IncidentSummaryCard spill={data?.spill} />
              </div>

              {/* COLUMN 2 (CENTER): Large Interactive GIS Map + Timeline */}
              <div className="center-map-column" style={{ position: 'relative' }}>
                {loading && (
                  <div style={{
                    position: 'absolute',
                    inset: 0,
                    background: 'rgba(255, 255, 255, 0.75)',
                    backdropFilter: 'blur(3px)',
                    zIndex: 1000,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 12,
                    borderRadius: 8
                  }}>
                    <RefreshCw size={32} color="#0284c7" style={{ animation: 'spin 1s linear infinite' }} />
                    <div style={{ fontWeight: 800, color: '#0f172a', fontSize: '0.9rem' }}>
                      Executing P1 → P2 → P3 → P4 Pipeline...
                    </div>
                  </div>
                )}

                <MapView 
                  data={data}
                  selectedVesselMmsi={selectedVesselMmsi}
                  onSelectVessel={setSelectedVesselMmsi}
                  layers={layers}
                  timelineStep={timelineStep}
                />

                <ForecastTimeline onStepSelect={setTimelineStep} />
              </div>

              {/* COLUMN 3 (RIGHT): Ranked Vessel Attribution Panel */}
              <div className="right-ranking-column">
                <VesselRankingPanel 
                  candidates={data?.candidates}
                  rankings={data?.ranking}
                  selectedVesselMmsi={selectedVesselMmsi}
                  onSelectVessel={setSelectedVesselMmsi}
                  onOpenDetails={setDetailModalMmsi}
                />
              </div>

              {/* BOTTOM ROW: Analytics Cards Grid */}
              <div className="bottom-analytics-grid">
                <InvestigationInsights data={data} />

                <SourceAttributionCard source={data?.source} />

                <ForecastCard forecast={data?.forecast} />

                <SimulationCard 
                  candidates={data?.candidates}
                  selectedVesselMmsi={selectedVesselMmsi}
                  onSelectVessel={setSelectedVesselMmsi}
                  simulationLayerActive={layers.simulation}
                  onToggleSimulation={() => handleToggleLayer('simulation')}
                />
              </div>

              {/* Legal Disclaimer Bar */}
              <div style={{ gridColumn: '1 / -1' }}>
                <DisclaimerBar />
              </div>
            </div>
          )}

          {/* TAB 2: ANALYSIS PAGE */}
          {activeNavTab === 'analysis' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#0284c7' }}>
                  <span><BarChart2 size={18} inline style={{ marginRight: 8 }} /> Investigation Analytical Breakdown</span>
                </div>

                {!data ? (
                  <div style={{ padding: 32, textAlign: 'center' }}>
                    <Compass size={48} color="#94a3b8" style={{ marginBottom: 12 }} />
                    <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#334155', marginBottom: 6 }}>
                      Investigation Not Yet Run
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: '#64748b', maxWidth: 450, margin: '0 auto 16px' }}>
                      Run an investigation from the Dashboard to analyze P2 estimated source regions, AIS vessel telemetry, and P4 forward drift attribution scores.
                    </p>
                    <button 
                      className="btn-primary-action font-mono"
                      onClick={() => {
                        setActiveNavTab('dashboard');
                        handleRunInvestigation('demo_001', true);
                      }}
                    >
                      <Play size={14} /> RUN INVESTIGATION NOW
                    </button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 16 }}>
                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                      <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: '#0f172a', marginBottom: 8 }}>
                        🛰️ Sentinel-1 Satellite Detection (P1)
                      </h4>
                      <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.6 }}>
                        • <strong>Spill ID:</strong> {data.spill.spill_id}<br/>
                        • <strong>Observed Surface Area:</strong> {data.spill.area_km2} km²<br/>
                        • <strong>Confidence:</strong> {Math.round(data.spill.confidence * 100)}%<br/>
                        • <strong>Centroid:</strong> Lat {data.spill.centroid[0].toFixed(4)}°N, Lon {data.spill.centroid[1].toFixed(4)}°W (Gulf of Mexico)
                      </div>
                    </div>

                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                      <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: '#16a34a', marginBottom: 8 }}>
                        📍 P2 Backtracking Source Origin
                      </h4>
                      <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.6 }}>
                        • <strong>Estimated Release Window:</strong> {data.source.origin_time_start} to {data.source.origin_time_end}<br/>
                        • <strong>Backward Particle Drift Trajectories:</strong> {data.source.backward_particles.length} particle trace points<br/>
                        • <strong>Forward Dispersion Forecast:</strong> {data.forecast.length} waypoints towards Mississippi coastline
                      </div>
                    </div>

                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                      <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: '#0284c7', marginBottom: 8 }}>
                        🚢 P3 Candidate Vessel Ranking & P4 Forward Simulation
                      </h4>
                      <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.6 }}>
                        • <strong>Top Priority Candidate:</strong> MMSI {data.ranking[0].mmsi} (Score: {data.ranking[0].score.toFixed(2)})<br/>
                        • <strong>Supporting Evidence:</strong> {data.ranking[0].supporting_evidence.join('; ')}<br/>
                        • <strong>Contradictory Evidence:</strong> {data.ranking[0].contradictory_evidence.join('; ')}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: INCIDENTS VIEW */}
          {activeNavTab === 'incidents' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#dc2626' }}>
                  <span><AlertOctagon size={18} inline style={{ marginRight: 8 }} /> Active Incident Registry — Gulf of Mexico</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 16 }}>
                  Sentinel-1 SAR satellite detection feed and registered incident cases.
                </p>

                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #cbd5e1', textAlign: 'left' }}>
                      <th style={{ padding: 10 }}>Incident ID</th>
                      <th style={{ padding: 10 }}>Region</th>
                      <th style={{ padding: 10 }}>Status</th>
                      <th style={{ padding: 10 }}>Area (km²)</th>
                      <th style={{ padding: 10 }}>Confidence</th>
                      <th style={{ padding: 10 }}>Centroid (Lat/Lon)</th>
                      <th style={{ padding: 10 }}>Acquisition Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: 10, fontWeight: 700, color: '#0284c7' }}>{data?.spill?.spill_id || 'demo_001'}</td>
                      <td style={{ padding: 10 }}>Gulf of Mexico (Mississippi Canyon)</td>
                      <td style={{ padding: 10 }}><span style={{ background: '#fef2f2', color: '#dc2626', padding: '2px 8px', borderRadius: 4, fontWeight: 700 }}>ACTIVE</span></td>
                      <td style={{ padding: 10, fontWeight: 700 }}>{data?.spill?.area_km2 || 215.1} km²</td>
                      <td style={{ padding: 10, fontWeight: 700, color: '#16a34a' }}>{data?.spill ? `${Math.round(data.spill.confidence * 100)}%` : '83.5%'}</td>
                      <td style={{ padding: 10 }} className="font-mono">{data?.spill?.centroid ? `${data.spill.centroid[0].toFixed(4)}°N, ${data.spill.centroid[1].toFixed(4)}°W` : '29.1105°N, -88.7309°W'}</td>
                      <td style={{ padding: 10 }}>{data?.spill?.timestamp || '2026-08-30T10:00:00'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: VESSELS VIEW */}
          {activeNavTab === 'vessels' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#0284c7' }}>
                  <span><Ship size={18} inline style={{ marginRight: 8 }} /> Candidate Vessel Roster — AIS Telemetry</span>
                </div>

                {!data ? (
                  <div style={{ padding: 24, textStyle: 'italic', color: '#64748b', fontSize: '0.82rem' }}>
                    No investigation results loaded. Execute investigation to extract AIS tracks and rank candidate vessels.
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', marginTop: 12 }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #cbd5e1', textAlign: 'left' }}>
                        <th style={{ padding: 10 }}>Rank</th>
                        <th style={{ padding: 10 }}>Vessel Name</th>
                        <th style={{ padding: 10 }}>MMSI</th>
                        <th style={{ padding: 10 }}>Priority Score</th>
                        <th style={{ padding: 10 }}>Distance to Source</th>
                        <th style={{ padding: 10 }}>Time Gap</th>
                        <th style={{ padding: 10 }}>Speed</th>
                        <th style={{ padding: 10 }}>Heading</th>
                        <th style={{ padding: 10 }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data?.ranking?.map((r) => {
                        const candidate = data?.candidates?.find(c => c.mmsi === r.mmsi);
                        return (
                          <tr key={r.mmsi} style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: 10, fontWeight: 800 }}>#{r.rank}</td>
                            <td style={{ padding: 10, fontWeight: 700, color: '#0f172a' }}>{candidate?.vessel_name || 'Unknown'}</td>
                            <td style={{ padding: 10 }} className="font-mono">{r.mmsi}</td>
                            <td style={{ padding: 10, fontWeight: 800, color: r.rank === 1 ? '#dc2626' : '#0284c7' }}>{r.score.toFixed(2)}</td>
                            <td style={{ padding: 10 }}>{candidate?.distance_km} km</td>
                            <td style={{ padding: 10 }}>{candidate?.time_difference_hr} hr</td>
                            <td style={{ padding: 10 }}>{candidate?.speed} kts</td>
                            <td style={{ padding: 10 }}>{candidate?.heading}°</td>
                            <td style={{ padding: 10 }}>
                              <button 
                                style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: 4, cursor: 'pointer', fontSize: '0.72rem', fontWeight: 700 }}
                                onClick={() => {
                                  setActiveNavTab('dashboard');
                                  setSelectedVesselMmsi(r.mmsi);
                                  setDetailModalMmsi(r.mmsi);
                                }}
                              >
                                Details
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* TAB 5: REPORTS VIEW */}
          {activeNavTab === 'reports' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#0f172a' }}>
                  <span><FileText size={18} inline style={{ marginRight: 8 }} /> Investigation & Attribution Reports</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 16 }}>
                  Generated quantitative evidence summary and mathematical reconstruction audit reports.
                </p>

                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, marginBottom: 16 }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 800, color: '#0f172a', marginBottom: 6 }}>
                    Case: {data?.spill?.spill_id || 'demo_001'} — Gulf of Mexico Executive Summary
                  </h3>
                  <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.5 }}>
                    <strong>Observation Sensor:</strong> Sentinel-1 Synthetic Aperture Radar (SAR)<br/>
                    <strong>Detected Slick Footprint:</strong> {data?.spill?.area_km2 || 215.1} km² at centroid ({data?.spill?.centroid ? `${data.spill.centroid[0]}°N, ${data.spill.centroid[1]}°W` : '29.1105°N, -88.7309°W'})<br/>
                    <strong>Top Candidate Vessel:</strong> MMSI {data?.ranking?.[0]?.mmsi || '345678901'} (Priority Score: {data?.ranking?.[0]?.score ? data.ranking[0].score.toFixed(2) : '0.50'})<br/>
                    <strong>What-If Simulation Overlap:</strong> P4 Lagrangian forward advection-diffusion particle simulation confirms physical trajectory alignment with satellite-observed slick boundary.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: SETTINGS VIEW */}
          {activeNavTab === 'settings' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#0f172a' }}>
                  <span><Settings size={18} inline style={{ marginRight: 8 }} /> Gateway & Sensor System Settings</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
                  <div className="metric-pill">
                    <div className="metric-pill-lbl">FastAPI Gateway URL</div>
                    <div className="metric-pill-val font-mono" style={{ color: '#0284c7' }}>{API_BASE_URL}</div>
                  </div>

                  <div className="metric-pill">
                    <div className="metric-pill-lbl">Connection Gateway Status</div>
                    <div className="metric-pill-val" style={{ color: backendConnected ? '#16a34a' : '#dc2626' }}>
                      {backendConnected ? 'ONLINE • HTTP 200' : 'OFFLINE'}
                    </div>
                  </div>

                  <div className="metric-pill">
                    <div className="metric-pill-lbl">Environmental Forcing Feeds</div>
                    <div className="metric-pill-val" style={{ fontSize: '0.8rem', color: '#334155' }}>
                      ERA5 Atmospheric Wind (10m) + CMEMS Surface Ocean Current (0.49m)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: HELP VIEW */}
          {activeNavTab === 'help' && (
            <div style={{ padding: 24 }}>
              <div className="light-card">
                <div className="card-header-title" style={{ fontSize: '1rem', color: '#0f172a' }}>
                  <span><HelpCircle size={18} inline style={{ marginRight: 8 }} /> TideX MOSARIS Operational User Guide</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: 1.6, marginTop: 8 }}>
                  <p style={{ marginBottom: 10 }}>
                    <strong>TideX MOSARIS</strong> (Maritime Oil-Spill Attribution & Response Intelligence System) provides an integrated, physics-grounded decision support platform for marine emergency response authorities.
                  </p>
                  <ul style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <li><strong>P1 (SAR Detection):</strong> Processes Sentinel-1 satellite radar imagery to delineate oil slicks.</li>
                    <li><strong>P2 (Drift Modeling):</strong> Executes 2D Lagrangian particle tracking with wind and ocean current forcing for 24h reverse origin hindcasting and forward forecasting.</li>
                    <li><strong>P3 (AIS Candidates):</strong> Filters AIS telemetry to identify vessels in the estimated source region and release window.</li>
                    <li><strong>P4 (Attribution Simulation):</strong> Simulates forward oil drift from candidate release hypotheses to evaluate IoU slick boundary overlap against observed satellite slicks.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Vessel Detail Modal Drawer */}
      {detailModalMmsi && (
        <VesselDetailModal 
          vessel={selectedVessel}
          ranking={selectedRanking}
          simulation={selectedSimulation}
          simulationLayerActive={layers.simulation}
          onToggleSimulation={() => handleToggleLayer('simulation')}
          onClose={() => setDetailModalMmsi(null)}
        />
      )}
    </div>
  );
}
