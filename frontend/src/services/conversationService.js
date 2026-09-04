const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";


function formatErrorDetail(detail) {
  if (!detail) {
    return null;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item?.msg) {
          return item.msg;
        }

        try {
          return JSON.stringify(item);
        } catch {
          return "Request validation failed";
        }
      })
      .join("; ");
  }

  if (detail?.msg) {
    return detail.msg;
  }

  try {
    return JSON.stringify(detail);
  } catch {
    return "Request failed";
  }
}


async function parseResponse(response) {
  const data =
    await response.json().catch(
      () => null
    );

  if (!response.ok) {
    throw new Error(
      formatErrorDetail(
        data?.detail
      ) ??
        `Conversation request failed: ${response.status}`
    );
  }

  return data;
}


export async function startConversation({
  sessionId,
  complaint,
  language = "en",
  mode = "allopathy",
}) {
  const response =
    await fetch(
      `${API_BASE_URL}/conversation/start`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({
          session_id:
            sessionId,

          complaint,

          language,

          mode,
        }),
      }
    );

  return parseResponse(
    response
  );
}


export async function submitConversationAnswer({
  sessionId,
  fieldId,
  answer,
  questionId,
  inputType = "touch",
}) {
  const response =
    await fetch(
      `${API_BASE_URL}/conversation/answer`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({
          session_id:
            sessionId,

          field_id:
            fieldId,

          answer,

          question_id:
            questionId,

          input_type:
            inputType,
        }),
      }
    );

  return parseResponse(
    response
  );
}


export async function getNextConversationQuestion(
  sessionId
) {
  const response =
    await fetch(
      `${API_BASE_URL}/conversation/${sessionId}/next`
    );

  return parseResponse(
    response
  );
}