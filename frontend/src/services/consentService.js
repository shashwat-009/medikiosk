const API_BASE_URL = "http://localhost:8000";

export async function createConsent(consentData) {
  const response = await fetch(
    `${API_BASE_URL}/consents/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(consentData),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to save consent."
    );
  }

  return response.json();
}