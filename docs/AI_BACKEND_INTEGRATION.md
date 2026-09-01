\# MediKiosk AI → Backend Integration Contract



\## 1. Purpose



This document defines how the completed AI modules in MediKiosk

should be consumed by the backend.



The backend should orchestrate the AI modules but should NOT duplicate

their internal clinical logic.



\---



\## 2. Completed AI Modules



The AI layer currently contains:



\- ASR

\- Clinical History Ontology

\- Question Bank

\- Dialogue State

\- Adaptive Questioning

\- Red-Flag Detection

\- Conversation History

\- Structured Output



The AI modules are independently implemented and tested.



\---



\## 3. Overall Data Flow



```text

Frontend

&#x20;  |

&#x20;  | Audio / Text

&#x20;  v

Backend

&#x20;  |

&#x20;  v

ASR (for audio input)

&#x20;  |

&#x20;  v

ASRResponse

&#x20;  |

&#x20;  v

Conversation Layer

&#x20;  |

&#x20;  +--> Dialogue State

&#x20;  |

&#x20;  +--> Red-Flag Detection

&#x20;  |

&#x20;  +--> Adaptive Questioning

&#x20;  |

&#x20;  +--> Conversation History

&#x20;  |

&#x20;  v

Structured Output

&#x20;  |

&#x20;  v

Backend API Response

&#x20;  |

&#x20;  v

Frontend

