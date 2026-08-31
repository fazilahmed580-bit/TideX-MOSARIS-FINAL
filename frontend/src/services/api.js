/**
 * services/api.js
 * ---------------
 * Centralized API client for communicating with the MOSARIS FastAPI backend.
 * Primary endpoint: POST http://127.0.0.1:8000/investigate
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Execute full investigation pipeline via POST /investigate
 * @param {string} spillId - Case ID (default: "demo_001")
 */
export async function runInvestigation(spillId = 'demo_001') {
  const payload = { spill_id: spillId };

  // Candidate URLs to support direct CORS or Vite proxying seamlessly
  const endpointsToTry = [
    `${API_BASE_URL}/investigate`,
    `/investigate`,
    `/api/investigate`
  ];

  let lastError = null;

  for (const endpoint of endpointsToTry) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        if (data && data.spill) {
          return data;
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned HTTP ${response.status}`);
      }
    } catch (err) {
      lastError = err;
    }
  }

  throw new Error(
    `Unable to connect to MOSARIS backend at ${API_BASE_URL}. (${lastError ? lastError.message : 'Network error'})`
  );
}

/**
 * Check backend health status by testing the primary POST /investigate endpoint
 */
export async function checkBackendHealth() {
  try {
    const data = await runInvestigation('demo_001');
    return data;
  } catch (err) {
    return null;
  }
}
