import { useState } from 'react';
import { patientService } from '../services/patientService';
export function usePatient() { const [patient, setPatient] = useState(null); return { patient, createPatient: async data => { const result = await patientService.create(data); setPatient(result); return result; } }; }
