export async function refreshAccessToken() {
  const response = await fetch(`${process.env.PUBLIC_URL}/api/refresh`, { method: 'POST', credentials: 'include' });

  if (response.status === 401) {
    throw new Error("Invalid refresh token");
  }
  if (response.status >= 500) {
    console.log("Error refreshing token");
    throw new Error("Server error");
  }
  return response;
}

export async function fetchWithToken(url, options = {}) {
  try {
    const response = await fetch(url, { ...options, credentials: 'include' });
    
    if (response.status === 401) {
      try {
        await refreshAccessToken();
        return await fetch(url, { ...options, credentials: 'include' });
      } catch (authError) {
        console.error('Token refresh failed:', authError);
        return response;
      }
    }
    
    return response;
  } catch (error) {
    console.error('Network error:', error);
    throw error;
  }
}