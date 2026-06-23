export const API_BASE_URL = import.meta.env.VITE_API_URL

export const apiClient = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  const response = await fetch(url, defaultOptions);
  
  if (!response.ok) {
    throw new Error(`Error en la petición: ${response.statusText}`);
  }
  
  return response.json();
};
