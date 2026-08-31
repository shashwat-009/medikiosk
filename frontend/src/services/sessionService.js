const API_BASE_URL = "http://localhost:8000";

export async function createSession(patientId) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        patient_id: patientId,
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to create session."
    );
  }

  return response.json();
}