const RENDER_API_URL = 'https://neoplasms-classifier.onrender.com/predict'

// The home demo is built with VITE_API_URL=/predict; other builds keep the published API.
export function apiUrl(env) {
  return env?.VITE_API_URL || RENDER_API_URL
}
