import { useState } from 'react';
import { consentService } from '../services/consentService';
export function useConsent() { const [consent, setConsent] = useState(null); return { consent, submitConsent: async data => { const result = await consentService.submit(data); setConsent(result); return result; } }; }
