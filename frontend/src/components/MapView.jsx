import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';

const LIGHT_TILE_CONFIGS = {
  'osm-standard': {
    name: 'OpenStreetMap Standard',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }
};

const createVesselIconLight = (isSelected, isTopRank) => {
  const color = isTopRank ? '#dc2626' : isSelected ? '#0284c7' : '#2563eb';
  const size = isSelected ? 30 : 22;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" stroke="#ffffff" stroke-width="1.8">
      <polygon points="12 2 19 21 12 17 5 21 12 2" />
    </svg>
  `;

  return L.divIcon({
    html: svg,
    className: 'vessel-icon-light',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
};

const createSpillCentroidIconLight = () => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="#dc2626" stroke="#ffffff" stroke-width="2">
      <circle cx="12" cy="12" r="9"/>
      <circle cx="12" cy="12" r="3.5" fill="#ffffff"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'spill-centroid-icon-light',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
};

// Initial P1 satellite detected oil slick polygon in Gulf of Mexico
const DEFAULT_INITIAL_SPILL = {
  spill_id: 'demo_001',
  timestamp: '2026-08-30T10:00:00',
  spill_detected: true,
  centroid: [29.1105, -88.7309],
  area_km2: 215.1,
  confidence: 0.835,
  polygon: {
    type: 'Polygon',
    coordinates: [[
      [-88.78, 29.15],
      [-88.68, 29.18],
      [-88.65, 29.08],
      [-88.72, 29.02],
      [-88.80, 29.06],
      [-88.78, 29.15]
    ]]
  }
};

export default function MapView({ 
  data, 
  selectedVesselMmsi, 
  onSelectVessel, 
  layers,
  timelineStep = 0
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  // Default initial map center: Gulf of Mexico (lat 28.75, lon -88.35)
  const defaultCenter = [28.75, -88.35];
  const defaultZoom = 8;

  const [cursorCoords, setCursorCoords] = useState({ lat: 28.7500, lon: -88.3500 });

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

  // Init Leaflet map instance
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: defaultZoom,
      zoomControl: false,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const tileConf = LIGHT_TILE_CONFIGS['osm-standard'];
    L.tileLayer(tileConf.url, {
      attribution: tileConf.attribution,
      maxZoom: 19,
    }).addTo(map);

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

  // Render Map Layers on state change
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    // CLEAR ALL EXISTING LAYERS BEFORE REDRAWING
    layerGroup.clearLayers();

    const bounds = L.latLngBounds();
    const spillData = data?.spill || DEFAULT_INITIAL_SPILL;

    // 1. Detected Oil Spill Polygon (Red) & Centroid (P1)
    if (layers.spill && spillData) {
      const spillCoords = toLeafletPolygon(spillData.polygon);
      if (spillCoords.length > 0) {
        const spillPolygon = L.polygon(spillCoords, {
          color: '#dc2626',
          weight: 3,
          fillColor: '#ef4444',
          fillOpacity: 0.4,
        }).addTo(layerGroup);

        spillPolygon.bindPopup(`
          <div style="color: #0f172a; font-family: sans-serif;">
            <strong style="color: #dc2626; font-size: 14px;">🛢️ DETECTED OIL SPILL (P1)</strong><br/>
            <b>Spill ID:</b> ${spillData.spill_id}<br/>
            <b>Surface Area:</b> ${spillData.area_km2} km²<br/>
            <b>Confidence:</b> ${Math.round(spillData.confidence * 100)}%<br/>
            <b>Region:</b> Gulf of Mexico<br/>
            <b>Acquisition:</b> ${spillData.timestamp}
          </div>
        `);

        spillPolygon.getBounds().isValid() && bounds.extend(spillPolygon.getBounds());
      }

      if (spillData.centroid && spillData.centroid.length === 2) {
        const centroidMarker = L.marker(spillData.centroid, {
          icon: createSpillCentroidIconLight(),
        }).addTo(layerGroup);

        centroidMarker.bindPopup(`
          <div style="color: #0f172a;">
            <strong>Spill Centroid Location</strong><br/>
            Lat: ${spillData.centroid[0].toFixed(4)}°N, Lon: ${spillData.centroid[1].toFixed(4)}°W
          </div>
        `);

        bounds.extend(spillData.centroid);
      }
    }

    // Only render investigation-derived layers if investigation data is loaded
    if (data) {
      // 2. Source Region (Green Polygon) & Uncertainty Envelope (P2)
      if (layers.source && data.source) {
        const originCoords = toLeafletPolygon(data.source.origin_region);
        if (originCoords.length > 0) {
          const originPolygon = L.polygon(originCoords, {
            color: '#16a34a',
            weight: 2.5,
            fillColor: '#16a34a',
            fillOpacity: 0.3,
          }).addTo(layerGroup);

          originPolygon.bindPopup(`
            <div style="color: #0f172a;">
              <strong style="color: #16a34a;">📍 ESTIMATED ORIGIN REGION (P2 SOURCE)</strong><br/>
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
            color: '#d97706',
            weight: 2,
            dashArray: '5, 5',
            fillColor: '#f59e0b',
            fillOpacity: 0.15,
          }).addTo(layerGroup);

          uncertaintyPolygon.bindPopup(`
            <div style="color: #0f172a;">
              <strong style="color: #d97706;">⚠️ UNCERTAINTY BOUNDARY (P2)</strong><br/>
              Hydrodynamic drift probability envelope
            </div>
          `);
        }
      }

      // 3. Backward Drift Path (P2)
      if (layers.backwardDrift && data.source && data.source.backward_particles) {
        const backwardPts = toLeafletPoints(data.source.backward_particles);
        if (backwardPts.length > 0) {
          L.polyline(backwardPts, {
            color: '#9333ea',
            weight: 2.5,
            dashArray: '3, 6',
          }).addTo(layerGroup);

          backwardPts.forEach((pt) => {
            L.circleMarker(pt, {
              radius: 3.5,
              color: '#9333ea',
              fillColor: '#9333ea',
              fillOpacity: 0.9,
            }).addTo(layerGroup);
          });
        }
      }

      // 4. Forward Forecast Path filtered by Timeline Step (P2)
      if (layers.forecast && data.forecast) {
        const rawForecastPts = toLeafletPoints(data.forecast);
        const maxPts = Math.min(rawForecastPts.length, Math.max(1, timelineStep + 2));
        const forecastPts = rawForecastPts.slice(0, maxPts);

        if (forecastPts.length > 0) {
          L.polyline(forecastPts, {
            color: '#0284c7',
            weight: 3,
            dashArray: '8, 4',
          }).addTo(layerGroup);

          forecastPts.forEach((pt) => {
            L.circleMarker(pt, {
              radius: 4,
              color: '#0284c7',
              fillColor: '#0284c7',
              fillOpacity: 0.95,
            }).addTo(layerGroup);
          });
        }
      }

      // 5. AIS Vessels & Tracks (P3)
      if (layers.vessels && data.candidates) {
        data.candidates.forEach((vessel) => {
          const isSelected = selectedVesselMmsi ? String(vessel.mmsi) === String(selectedVesselMmsi) : false;
          const rankingObj = data.ranking?.find(r => String(r.mmsi) === String(vessel.mmsi));
          const isTopRank = rankingObj?.rank === 1;

          const trackCoords = toLeafletPolyline(vessel.track);
          if (trackCoords.length > 0) {
            const trackLine = L.polyline(trackCoords, {
              color: isSelected ? '#0284c7' : isTopRank ? '#dc2626' : '#2563eb',
              weight: isSelected ? 4.5 : 2.5,
              opacity: isSelected ? 1 : 0.7,
            }).addTo(layerGroup);

            bounds.extend(trackLine.getBounds());

            const lastPos = trackCoords[trackCoords.length - 1];
            const vesselMarker = L.marker(lastPos, {
              icon: createVesselIconLight(isSelected, isTopRank),
            }).addTo(layerGroup);

            vesselMarker.on('click', () => {
              onSelectVessel(vessel.mmsi);
            });

            vesselMarker.bindPopup(`
              <div style="color: #0f172a; font-family: sans-serif; min-width: 170px;">
                <strong style="color: #0284c7; font-size: 13px;">🚢 ${vessel.vessel_name || 'Unknown Vessel'} (P3)</strong><br/>
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
      if (layers.simulation && data.simulations) {
        data.simulations.forEach((sim) => {
          const isSelected = selectedVesselMmsi ? String(sim.mmsi) === String(selectedVesselMmsi) : true;

          // If a candidate vessel is selected, highlight its P4 simulation
          if (selectedVesselMmsi && !isSelected) return;

          if (sim.predicted_polygons) {
            sim.predicted_polygons.forEach((poly) => {
              const simCoords = toLeafletPolygon(poly);
              if (simCoords.length > 0) {
                const simPolygon = L.polygon(simCoords, {
                  color: '#d946ef',
                  weight: 3.5,
                  dashArray: '6, 6',
                  fillColor: '#f0abfc',
                  fillOpacity: 0.45,
                }).addTo(layerGroup);

                const rankingObj = data.ranking?.find(r => String(r.mmsi) === String(sim.mmsi));
                const candObj = data.candidates?.find(c => String(c.mmsi) === String(sim.mmsi));

                simPolygon.bindPopup(`
                  <div style="color: #0f172a; font-family: sans-serif;">
                    <strong style="color: #c026d3; font-size: 13px;">🔮 WHAT-IF OIL-DRIFT SIMULATION (P4)</strong><br/>
                    <b>Vessel Target:</b> ${candObj?.vessel_name || 'Unknown'} (MMSI: ${sim.mmsi})<br/>
                    <b>Attribution Priority Rank:</b> #${rankingObj?.rank || 'N/A'}<br/>
                    <b>Priority Score:</b> ${rankingObj?.score ? rankingObj.score.toFixed(2) : 'N/A'}<br/>
                    <p style="font-size: 11px; margin-top: 4px; color: #475569;">
                      Forward Lagrangian oil-drift footprint simulated from candidate release hypothesis to satellite observation time.
                    </p>
                  </div>
                `);

                bounds.extend(simPolygon.getBounds());
              }
            });
          }
        });
      }
    }

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
    }
  }, [data, selectedVesselMmsi, layers, timelineStep]);

  return (
    <div className="map-wrapper-card">
      {/* Lat/Lon Cursor HUD */}
      <div className="map-coords-hud-light font-mono">
        {cursorCoords.lat.toFixed(4)}°N, {cursorCoords.lon.toFixed(4)}°W | Gulf of Mexico
      </div>

      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
