export async function refreshAccessToken() {
    const response = await fetch(`${process.env.PUBLIC_URL}/api/refresh`, { method: 'POST', credentials: 'include' });
  
    if (response.status === 401) {
      throw new Error("Invalid refresh token")
    }
    if (response.status >= 500) {
        console.log("Error refreshing token");
        alert("There was an error, please try again later.");
    }
  }
  
  export async function fetchWithToken(url, options = {}) {
    const response = await fetch(url, { ...options, credentials: 'include' });
    if (response.status === 401) {
      try {
        await refreshAccessToken();
        return await fetch(url, { ...options, credentials: 'include' });
      } catch (authError) {
        console.error('Token refresh failed:', authError);
        alert("Please refresh the page and log in again.")
      }
    }
  
    return response;
  }