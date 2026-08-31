import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Layers, Compass } from 'lucide-react';

const TILE_CONFIGS = {
  'carto-dark': {
    name: 'CartoDB Dark Matter',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; OpenStreetMap &copy; CARTO'
  },
  'osm-standard': {
    name: 'OpenStreetMap Standard',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors'
  },
  'esri-satellite': {
    name: 'Esri Ocean Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri'
  }
};

const createVesselMarkerIcon = (isSelected, isTopRank) => {
  const color = isTopRank ? '#f43f5e' : isSelected ? '#00f2fe' : '#38bdf8';
  const size = isSelected ? 32 : 24;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" stroke="#ffffff" stroke-width="1.8">
      <polygon points="12 2 19 21 12 17 5 21 12 2" />
    </svg>
  `;

  return L.divIcon({
    html: svg,
    className: 'tactical-vessel-icon',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
};

const createSpillCentroidMarkerIcon = () => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="#f43f5e" stroke="#ffffff" stroke-width="2">
      <circle cx="12" cy="12" r="9"/>
      <circle cx="12" cy="12" r="3.5" fill="#ffffff"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'tactical-spill-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

export default function TacticalMap({ 
  data, 
  selectedVesselMmsi, 
  onSelectVessel, 
  layers, 
  onToggleLayer 
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const tileLayerRef = useRef(null);
  const layerGroupRef = useRef(null);

  const [tileProvider, setTileProvider] = useState('carto-dark');
  const [cursorCoords, setCursorCoords] = useState({ lat: 18.9500, lon: 71.8600 });

  const defaultCenter = [18.95, 71.86];
  const defaultZoom = 9;

  // GeoJSON coordinate converters [lon, lat] -> [lat, lon]
  const toLeafletPolygon = (polygon) => {
    if (!polygon || !polygon.coordinates) return [];
    return polygon.coordinates.map(ring => ring.map(pt => [pt[1], pt[0]]));
  };

  const toLeafletPolyline = (lineString) => {
    if (!lineString || !lineString.coordinates) return [];
    return lineString.coordinates.map(pt => [pt[1], pt[0]]);
  };

  const toLeafletPoints = (points) => {
    if (!points || !Array.isArray(points)) return [];
    return points.map(pt => [pt[1], pt[0]]);
  };

  // Init Leaflet
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: defaultZoom,
      zoomControl: false,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const tileConf = TILE_CONFIGS['carto-dark'];
    const tiles = L.tileLayer(tileConf.url, {
      attribution: tileConf.attribution,
      maxZoom: 19,
    }).addTo(map);

    tileLayerRef.current = tiles;
    layerGroupRef.current = L.layerGroup().addTo(map);

    map.on('mousemove', (e) => {
      setCursorCoords({ lat: e.latlng.lat, lon: e.latlng.lng });
    });

    mapInstanceRef.current = map;

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Handle Tile Provider Changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }

    const tileConf = TILE_CONFIGS[tileProvider] || TILE_CONFIGS['carto-dark'];
    const newTiles = L.tileLayer(tileConf.url, {
      attribution: tileConf.attribution,
      maxZoom: 19,
    }).addTo(map);

    tileLayerRef.current = newTiles;
  }, [tileProvider]);

  // Render Map Layers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();
    if (!data) return;

    const bounds = L.latLngBounds();

    // 1. Detected Oil Spill Polygon & Centroid (P1)
    if (layers.spill && data.spill) {
      const spillCoords = toLeafletPolygon(data.spill.polygon);
      if (spillCoords.length > 0) {
        const spillPolygon = L.polygon(spillCoords, {
          color: '#f43f5e',
          weight: 3,
          fillColor: '#f43f5e',
          fillOpacity: 0.45,
        }).addTo(layerGroup);

        spillPolygon.bindPopup(`
          <div style="color: #020617; font-family: sans-serif;">
            <strong style="color: #f43f5e; font-size: 14px;">🛢️ SAR DETECTED OIL SPILL</strong><br/>
            <b>Spill ID:</b> ${data.spill.spill_id}<br/>
            <b>Surface Area:</b> ${data.spill.area_km2} km²<br/>
            <b>Confidence:</b> ${Math.round(data.spill.confidence * 100)}%<br/>
            <b>Acquisition:</b> ${data.spill.timestamp}
          </div>
        `);

        spillPolygon.getBounds().isValid() && bounds.extend(spillPolygon.getBounds());
      }

      if (data.spill.centroid && data.spill.centroid.length === 2) {
        const centroidMarker = L.marker(data.spill.centroid, {
          icon: createSpillCentroidMarkerIcon(),
        }).addTo(layerGroup);

        centroidMarker.bindPopup(`
          <div style="color: #020617;">
            <strong>Spill Centroid Location</strong><br/>
            Lat: ${data.spill.centroid[0].toFixed(4)}°N, Lon: ${data.spill.centroid[1].toFixed(4)}°E
          </div>
        `);

        bounds.extend(data.spill.centroid);
      }
    }

    // 2. Source Region & Uncertainty Boundary (P2)
    if (layers.source && data.source) {
      const originCoords = toLeafletPolygon(data.source.origin_region);
      if (originCoords.length > 0) {
        const originPolygon = L.polygon(originCoords, {
          color: '#f59e0b',
          weight: 2.5,
          dashArray: '6, 6',
          fillColor: '#f59e0b',
          fillOpacity: 0.25,
        }).addTo(layerGroup);

        originPolygon.bindPopup(`
          <div style="color: #020617;">
            <strong style="color: #d97706;">📍 ESTIMATED ORIGIN SOURCE</strong><br/>
            <b>Release Window:</b> ${data.source.origin_time_start} to ${data.source.origin_time_end}
          </div>
        `);

        bounds.extend(originPolygon.getBounds());
      }
    }

    if (layers.uncertainty && data.source && data.source.uncertainty_polygon) {
      const uncertaintyCoords = toLeafletPolygon(data.source.uncertainty_polygon);
      if (uncertaintyCoords.length > 0) {
        const uncertaintyPolygon = L.polygon(uncertaintyCoords, {
          color: '#fde047',
          weight: 1.5,
          dashArray: '4, 8',
          fillColor: '#fde047',
          fillOpacity: 0.12,
        }).addTo(layerGroup);

        uncertaintyPolygon.bindPopup(`
          <div style="color: #020617;">
            <strong style="color: #ca8a04;">⚠️ UNCERTAINTY ENVELOPE</strong><br/>
            Broader hydrodynamic drift boundary
          </div>
        `);
      }
    }

    // 3. Backward Drift Trajectory (P2)
    if (layers.backwardDrift && data.source && data.source.backward_particles) {
      const backwardPts = toLeafletPoints(data.source.backward_particles);
      if (backwardPts.length > 0) {
        L.polyline(backwardPts, {
          color: '#00f2fe',
          weight: 2.5,
          dashArray: '4, 6',
        }).addTo(layerGroup);

        backwardPts.forEach((pt) => {
          L.circleMarker(pt, {
            radius: 3.5,
            color: '#00f2fe',
            fillColor: '#00f2fe',
            fillOpacity: 0.85,
          }).addTo(layerGroup);
        });
      }
    }

    // 4. Forward Forecast Trajectory (P2)
    if (layers.forecast && data.forecast) {
      const forecastPts = toLeafletPoints(data.forecast);
      if (forecastPts.length > 0) {
        L.polyline(forecastPts, {
          color: '#10b981',
          weight: 2.5,
          dashArray: '8, 4',
        }).addTo(layerGroup);

        forecastPts.forEach((pt) => {
          L.circleMarker(pt, {
            radius: 4,
            color: '#10b981',
            fillColor: '#10b981',
            fillOpacity: 0.9,
          }).addTo(layerGroup);
        });
      }
    }

    // 5. AIS Candidate Vessel Tracks (P3/P4)
    if (layers.vessels && data.candidates) {
      data.candidates.forEach((vessel) => {
        const isSelected = vessel.mmsi === selectedVesselMmsi;
        const rankingObj = data.ranking?.find(r => r.mmsi === vessel.mmsi);
        const isTopRank = rankingObj?.rank === 1;

        const trackCoords = toLeafletPolyline(vessel.track);
        if (trackCoords.length > 0) {
          const trackLine = L.polyline(trackCoords, {
            color: isSelected ? '#00f2fe' : isTopRank ? '#f43f5e' : '#38bdf8',
            weight: isSelected ? 4.5 : 2.5,
            opacity: isSelected ? 1 : 0.65,
          }).addTo(layerGroup);

          bounds.extend(trackLine.getBounds());

          const lastPos = trackCoords[trackCoords.length - 1];
          const vesselMarker = L.marker(lastPos, {
            icon: createVesselMarkerIcon(isSelected, isTopRank),
          }).addTo(layerGroup);

          vesselMarker.on('click', () => {
            onSelectVessel(vessel.mmsi);
          });

          vesselMarker.bindPopup(`
            <div style="color: #020617; font-family: sans-serif; min-width: 170px;">
              <strong style="color: #0284c7; font-size: 13px;">🚢 ${vessel.vessel_name || 'Unknown Vessel'}</strong><br/>
              <b>MMSI:</b> ${vessel.mmsi}<br/>
              <b>Priority Rank:</b> #${rankingObj?.rank || 'N/A'}<br/>
              <b>Priority Score:</b> ${rankingObj?.score ? rankingObj.score.toFixed(2) : 'N/A'}<br/>
              <b>Speed:</b> ${vessel.speed} kts | <b>Heading:</b> ${vessel.heading}°<br/>
              <b>Dist to Origin:</b> ${vessel.distance_km} km
            </div>
          `);
        }
      });
    }

    // 6. What-If Simulation Polygon (P4)
    if (layers.simulation && selectedVesselMmsi && data.simulations) {
      const sim = data.simulations.find(s => s.mmsi === selectedVesselMmsi);
      if (sim && sim.predicted_polygons) {
        sim.predicted_polygons.forEach((poly) => {
          const simCoords = toLeafletPolygon(poly);
          if (simCoords.length > 0) {
            const simPolygon = L.polygon(simCoords, {
              color: '#c084fc',
              weight: 2.5,
              dashArray: '5, 5',
              fillColor: '#c084fc',
              fillOpacity: 0.35,
            }).addTo(layerGroup);

            simPolygon.bindPopup(`
              <div style="color: #020617;">
                <strong style="color: #7e22ce;">🔮 WHAT-IF SIMULATED SPILL</strong><br/>
                Simulated spill outcome if vessel MMSI ${selectedVesselMmsi} was the source.
              </div>
            `);

            bounds.extend(simPolygon.getBounds());
          }
        });
      }
    }

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 11 });
    }
  }, [data, selectedVesselMmsi, layers]);

  return (
    <div className="tactical-map-container">
      {/* Floating HUD Layer & Map Controls */}
      <div className="map-hud-floating-card">
        <div className="hud-card-title">
          <Layers size={14} /> Map Intelligence Layers
        </div>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#f43f5e' }}></span>
            Detected Spill (P1)
          </span>
          <input type="checkbox" checked={layers.spill} onChange={() => onToggleLayer('spill')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#f59e0b' }}></span>
            Source Region (P2)
          </span>
          <input type="checkbox" checked={layers.source} onChange={() => onToggleLayer('source')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#fde047' }}></span>
            Uncertainty Boundary
          </span>
          <input type="checkbox" checked={layers.uncertainty} onChange={() => onToggleLayer('uncertainty')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#00f2fe' }}></span>
            Backward Drift Path
          </span>
          <input type="checkbox" checked={layers.backwardDrift} onChange={() => onToggleLayer('backwardDrift')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#10b981' }}></span>
            Forward Forecast
          </span>
          <input type="checkbox" checked={layers.forecast} onChange={() => onToggleLayer('forecast')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#38bdf8' }}></span>
            AIS Vessels & Tracks
          </span>
          <input type="checkbox" checked={layers.vessels} onChange={() => onToggleLayer('vessels')} />
        </label>

        <label className="layer-toggle-row">
          <span>
            <span className="layer-color-dot" style={{ background: '#c084fc' }}></span>
            What-If Simulation
          </span>
          <input type="checkbox" checked={layers.simulation} onChange={() => onToggleLayer('simulation')} />
        </label>

        {/* Free Map Tile Basemap Switcher */}
        <div style={{ marginTop: 10, paddingTop: 8, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', marginBottom: 4, fontWeight: 700 }}>
            Tactical Basemap
          </div>
          <select 
            value={tileProvider} 
            onChange={(e) => setTileProvider(e.target.value)}
            style={{
              width: '100%',
              background: '#070d1e',
              color: '#f1f5f9',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 4,
              padding: '4px 8px',
              fontSize: '0.74rem',
              cursor: 'pointer'
            }}
          >
            <option value="carto-dark">CartoDB Dark Matter</option>
            <option value="osm-standard">OpenStreetMap Standard</option>
            <option value="esri-satellite">Esri Ocean Satellite</option>
          </select>
        </div>
      </div>

      {/* Real-time Cursor Coordinates HUD */}
      <div className="map-coords-badge font-mono">
        GRID: {cursorCoords.lat.toFixed(4)}°N, {cursorCoords.lon.toFixed(4)}°E | ARABIAN SEA
      </div>

      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
