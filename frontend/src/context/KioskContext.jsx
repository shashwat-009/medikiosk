import { createContext, useContext, useMemo, useState } from "react";

const KioskContext = createContext(null);

const initialState = {
  // Kiosk configuration
  language: null,
  mode: "allopathic",

  // Backend entities
  patient: null,
  session: null,
  consent: null,

  // Current clinical interaction
  transcript: [],

  // Documents uploaded during this session
  documents: [],

  // AI-generated clinical summary
  summary: null,

  // Emergency/red-flag state
  redFlag: null,
};

export function KioskProvider({ children }) {
  const [state, setState] = useState(initialState);

  const actions = useMemo(
    () => ({
      state,

      // Kiosk
      setLanguage: (language) =>
        setState((current) => ({
          ...current,
          language,
        })),

      setMode: (mode) =>
        setState((current) => ({
          ...current,
          mode,
        })),

      // Patient
      setPatient: (patient) =>
        setState((current) => ({
          ...current,
          patient,
        })),

      // Session
      setSession: (session) =>
        setState((current) => ({
          ...current,
          session,
        })),

      // Consent
      setConsent: (consent) =>
        setState((current) => ({
          ...current,
          consent,
        })),

      // Interview transcript
      pushTranscript: (entry) =>
        setState((current) => ({
          ...current,
          transcript: [...current.transcript, entry],
        })),

      clearTranscript: () =>
        setState((current) => ({
          ...current,
          transcript: [],
        })),

      // Documents
      addDocument: (document) =>
        setState((current) => ({
          ...current,
          documents: [...current.documents, document],
        })),

      updateDocument: (id, updates) =>
        setState((current) => ({
          ...current,
          documents: current.documents.map((document) =>
            document.id === id
              ? { ...document, ...updates }
              : document
          ),
        })),

      removeDocument: (id) =>
        setState((current) => ({
          ...current,
          documents: current.documents.filter(
            (document) => document.id !== id
          ),
        })),

      // Summary
      setSummary: (summary) =>
        setState((current) => ({
          ...current,
          summary,
        })),

      // Red flags
      triggerRedFlag: (symptom) =>
        setState((current) => ({
          ...current,
          redFlag: {
            symptom,
            time: new Date().toISOString(),
          },
        })),

      clearRedFlag: () =>
        setState((current) => ({
          ...current,
          redFlag: null,
        })),

      // Complete kiosk reset
      reset: () => setState(initialState),
    }),
    [state]
  );

  return (
    <KioskContext.Provider value={actions}>
      {children}
    </KioskContext.Provider>
  );
}

export function useKiosk() {
  const context = useContext(KioskContext);

  if (!context) {
    throw new Error(
      "useKiosk must be used within KioskProvider"
    );
  }

  return context;
}