export const interviewScript = [
  {
    id: "chief_complaint",
    questionKey: "interview.questions.chiefComplaint",
    type: "text",
    inputMode: "voice",
    required: true,
  },

  {
    id: "symptoms",
    questionKey: "interview.questions.symptoms",
    type: "text",
    inputMode: "voice",
    required: true,
  },

  {
    id: "duration",
    questionKey: "interview.questions.duration",
    type: "text",
    inputMode: "voice",
    required: true,
  },

  {
    id: "fever",
    questionKey: "interview.questions.fever",
    type: "boolean",
    inputMode: "both",
    options: ["yes", "no"],
    required: true,
  },

  {
    id: "medications",
    questionKey: "interview.questions.medications",
    type: "text",
    inputMode: "both",
    required: false,
  },
];