const API_BASE_URL = "http://localhost:8000";

export async function createResponse(responseData) {
  const response = await fetch(
    `${API_BASE_URL}/responses/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(responseData),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to save response."
    );
  }

  return response.json();
}