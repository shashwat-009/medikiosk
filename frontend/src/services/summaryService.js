import { api } from './api';
export const summaryService = { get: sessionId => api(`/summaries/${sessionId}`) };
