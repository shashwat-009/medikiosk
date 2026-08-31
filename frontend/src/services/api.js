const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export async function api(path, options = {}) { const response = await fetch(`${API_BASE_URL}${path}`, options); if (!response.ok) throw new Error(`Request failed: ${response.status}`); return response.status === 204 ? null : response.json(); }
