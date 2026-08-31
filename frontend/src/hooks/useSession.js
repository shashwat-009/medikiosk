import { useState } from 'react';
import { sessionService } from '../services/sessionService';
export function useSession() { const [session, setSession] = useState(null); return { session, createSession: async data => { const result = await sessionService.create(data); setSession(result); return result; } }; }
