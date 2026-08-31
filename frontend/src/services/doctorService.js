import { api } from './api';
export const doctorService = { login: data => api('/doctor/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }) };
