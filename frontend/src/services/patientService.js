const API_BASE_URL = "http://localhost:8000";

export async function createPatient(patientData) {
  const response = await fetch(
    `${API_BASE_URL}/patients/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(patientData),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to create patient."
    );
  }

  return response.json();
}